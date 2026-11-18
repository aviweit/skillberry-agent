"""Tests for the Skillberry-context request hooks: history trimming by regex and skill-prompt templating."""
import glob
import json
import logging
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from skillberry_agent_lib.context_hooks import render_skill_prompt, trim_chat_history
from skillberry_agent_lib.prompt import build_chat_messages

# The marker that separates AppWorld's few-shot prompt from the real task turn.
APPWORLD_REGEX = r"^\s*Using these APIs, now generate code to solve the actual task:"


def _appworld_like_history():
    """A short stand-in for an AppWorld ReAct request: demo turns, key instructions, real task, episode."""
    return [
        HumanMessage(content="I am your supervisor ... Using these APIs, you can now generate code, that I will execute, to solve the task."),
        AIMessage(content="Okay. ```python\nprint(apis.api_docs.show_api_descriptions(app_name='spotify'))\n```"),
        HumanMessage(content="Output:\n```\n[...]\n```"),
        HumanMessage(content="**Key instructions**:\n\nA. General instructions: ..."),
        HumanMessage(content="Using these APIs, now generate code to solve the actual task:\n\nMy name is: Timothy White. ...\nTask: Start playing a playlist ..."),
        AIMessage(content="Let me look up the Simple Note APIs. ```python\n...\n```"),
        HumanMessage(content="Output:\n```\n[...]\n```"),
    ]


class TestTrimChatHistory:
    def test_no_key_is_a_noop(self):
        history = _appworld_like_history()
        assert trim_chat_history(history, {"env_id": "e1"}) is history
        assert trim_chat_history(history, None) is history

    def test_appworld_marker_keeps_the_real_task_and_after(self):
        history = _appworld_like_history()
        trimmed = trim_chat_history(history, {"history_start_regex": APPWORLD_REGEX})
        assert trimmed == history[4:]
        assert trimmed[0].content.startswith("Using these APIs, now generate code to solve the actual task:")
        assert len(history) == 7  # input not modified

    def test_demo_look_alike_line_does_not_match(self):
        # Message 1 contains "Using these APIs, you can now generate code" -- it must not be the start.
        trimmed = trim_chat_history(_appworld_like_history(), {"history_start_regex": APPWORLD_REGEX})
        assert "I am your supervisor" not in trimmed[0].content

    def test_system_messages_before_the_match_are_kept(self):
        history = [SystemMessage(content="agent prompt")] + _appworld_like_history()
        trimmed = trim_chat_history(history, {"history_start_regex": APPWORLD_REGEX})
        assert isinstance(trimmed[0], SystemMessage) and trimmed[0].content == "agent prompt"
        assert trimmed[1:] == history[5:]

    def test_first_match_wins(self):
        history = [HumanMessage(content="START one"), HumanMessage(content="x"), HumanMessage(content="START two")]
        assert trim_chat_history(history, {"history_start_regex": "^START"}) == history

    def test_no_match_keeps_everything_and_warns(self, caplog):
        history = _appworld_like_history()
        with caplog.at_level(logging.WARNING):
            assert trim_chat_history(history, {"history_start_regex": "^never matches"}) is history
        assert "matched no message" in caplog.text

    def test_invalid_regex_keeps_everything_and_logs_error(self, caplog):
        history = _appworld_like_history()
        with caplog.at_level(logging.ERROR):
            assert trim_chat_history(history, {"history_start_regex": "("}) is history
        assert "Invalid history_start_regex" in caplog.text

    def test_list_content_blocks_are_searched(self):
        history = [HumanMessage(content="a"), HumanMessage(content=[{"type": "text", "text": "MARK here"}])]
        assert trim_chat_history(history, {"history_start_regex": "^MARK"}) == history[1:]


class TestRenderSkillPrompt:
    TEMPLATE = "My name is: {{ main_user.first_name }} {{ main_user.last_name }}. Email {{ main_user.email }}."

    def test_no_template_values_is_a_noop(self):
        assert render_skill_prompt(self.TEMPLATE, {"env_id": "e1"}) == self.TEMPLATE
        assert render_skill_prompt(self.TEMPLATE, None) == self.TEMPLATE

    def test_nested_values_from_headers_render(self):
        ctx = {"template": {"main_user": {"first_name": "Timothy", "last_name": "White", "email": "t@x.com"}}}
        assert render_skill_prompt(self.TEMPLATE, ctx) == "My name is: Timothy White. Email t@x.com."

    def test_undefined_variable_leaves_prompt_unrendered(self, caplog):
        ctx = {"template": {"main_user": {"first_name": "Timothy"}}}
        with caplog.at_level(logging.ERROR):
            assert render_skill_prompt(self.TEMPLATE, ctx) == self.TEMPLATE
        assert "Could not render" in caplog.text

    def test_non_dict_template_value_is_ignored(self):
        assert render_skill_prompt(self.TEMPLATE, {"template": "oops"}) == self.TEMPLATE

    def test_trailing_newline_kept(self):
        ctx = {"template": {"x": "1"}}
        assert render_skill_prompt("v={{ x }}\n", ctx) == "v=1\n"


class TestBuildChatMessagesWithHooks:
    def test_both_hooks_through_build_chat_messages(self):
        skill_md = "FEW-SHOT DEMO for {{ main_user.email }}\nUSER:\n...\nASSISTANT:\n..."
        ctx = {
            "env_id": "e1",
            "history_start_regex": APPWORLD_REGEX,
            "template": {"main_user": {"email": "t@x.com"}},
        }
        history = _appworld_like_history()
        with patch("skillberry_agent_lib.prompt.get_mcp_prompts_and_format", return_value=skill_md):
            messages = build_chat_messages(history, 8001, "srv", ctx)
        assert isinstance(messages[0], SystemMessage)
        assert messages[0].content.startswith("FEW-SHOT DEMO for t@x.com")
        assert messages[1].content.startswith("Using these APIs, now generate code to solve the actual task:")
        assert len(messages) == 1 + 3

    def test_no_hook_headers_behave_as_before(self):
        history = _appworld_like_history()
        with patch("skillberry_agent_lib.prompt.get_mcp_prompts_and_format", return_value="P {{ x }}"):
            messages = build_chat_messages(history, 8001, "srv", {"env_id": "e1"})
        assert messages[0].content == "P {{ x }}"  # injected verbatim
        assert len(messages) == 1 + 7


RUN_DUMPS = sorted(glob.glob("/home/weit/appworld/experiments/outputs/*/tasks/*/messages.json"))


@pytest.mark.skipif(not RUN_DUMPS, reason="no AppWorld run dumps on this machine")
@pytest.mark.parametrize("dump", RUN_DUMPS)
def test_regex_on_real_appworld_requests(dump):
    """On real dumped AppWorld requests, the marker keeps exactly the real task turn and after."""
    data = json.load(open(dump))
    role_to_cls = {"user": HumanMessage, "assistant": AIMessage, "system": SystemMessage}
    history = [role_to_cls[m["role"]](content=m.get("content") or "") for m in data["messages"]]
    trimmed = trim_chat_history(history, {"history_start_regex": APPWORLD_REGEX})
    assert len(trimmed) == len(history) - (data["num_prompt_messages"] - 1)
    assert trimmed[0] is history[data["num_prompt_messages"] - 1]
