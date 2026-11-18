"""Tests that skill prompts (SKILL.md snippets) reach the agent in full, never truncated.

The store registers each snippet as an MCP prompt whose listed ``description`` is a summary of at
most ~100 characters (first line or first 100 chars). The agent must inject the prompt's CONTENT,
fetched with ``get_prompt``, and never fall back to that summary.
"""
import asyncio
import logging
from types import SimpleNamespace

import pytest
from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session

from skillberry_agent_lib.skillberry_store import collect_prompts, prompt_content_text

# A SKILL.md body much longer than 100 characters whose first line is short, like AppWorld's
# ReAct prompt (first line "USER:"): the store's description would be just "USER:".
LONG_BODY = "USER:\n" + "\n".join(
    f"Rule {i}: always look up API specifications before calling an API." for i in range(200)
)


def _truncated_description(content: str) -> str:
    """The store's generate_description(): first line if <= 100 chars, else first 100 chars."""
    first_line = content.split("\n")[0].strip()
    if first_line and len(first_line) <= 100:
        return first_line
    return content[:100].strip() + ("..." if len(content) > 100 else "")


class FakeSession:
    """Minimal stand-in for an MCP ClientSession."""

    def __init__(self, prompts, results=None, errors=None):
        self._prompts = prompts
        self._results = results or {}
        self._errors = errors or {}

    async def list_prompts(self):
        return SimpleNamespace(prompts=self._prompts)

    async def get_prompt(self, name):
        if name in self._errors:
            raise self._errors[name]
        return self._results[name]


def _meta(name, description):
    return SimpleNamespace(name=name, description=description)


def _result(*texts):
    return SimpleNamespace(messages=[SimpleNamespace(content=SimpleNamespace(type="text", text=t)) for t in texts])


class TestPromptContentText:
    def test_single_text_message(self):
        assert prompt_content_text(_result("hello")) == "hello"

    def test_all_messages_are_kept(self):
        assert prompt_content_text(_result("part one", "part two")) == "part one\npart two"

    def test_plain_string_content(self):
        result = SimpleNamespace(messages=[SimpleNamespace(content="plain string")])
        assert prompt_content_text(result) == "plain string"

    def test_no_messages_is_none(self):
        assert prompt_content_text(SimpleNamespace(messages=[])) is None
        assert prompt_content_text(None) is None


class TestCollectPrompts:
    def test_long_content_is_not_truncated(self):
        desc = _truncated_description(LONG_BODY)
        assert desc == "USER:"  # the summary the store would list
        session = FakeSession([_meta("SKILL", desc)], results={"SKILL": _result(LONG_BODY)})
        prompts = asyncio.run(collect_prompts(session))
        assert len(prompts) == 1
        assert prompts[0].name == "SKILL"
        assert prompts[0].description == LONG_BODY
        assert len(prompts[0].description) > 100

    def test_fetch_failure_does_not_fall_back_to_truncated_description(self, caplog):
        session = FakeSession(
            [_meta("SKILL", _truncated_description(LONG_BODY))],
            errors={"SKILL": RuntimeError("connection reset")},
        )
        with caplog.at_level(logging.ERROR):
            prompts = asyncio.run(collect_prompts(session))
        assert prompts == []  # skipped, NOT replaced by "USER:"
        assert "Not injecting it" in caplog.text

    def test_prompt_without_content_is_skipped(self, caplog):
        session = FakeSession([_meta("EMPTY", "summary")], results={"EMPTY": SimpleNamespace(messages=[])})
        with caplog.at_level(logging.ERROR):
            assert asyncio.run(collect_prompts(session)) == []
        assert "returned no content" in caplog.text

    def test_one_failure_does_not_drop_the_others(self):
        session = FakeSession(
            [_meta("BAD", "x"), _meta("GOOD", "y")],
            results={"GOOD": _result(LONG_BODY)},
            errors={"BAD": RuntimeError("boom")},
        )
        prompts = asyncio.run(collect_prompts(session))
        assert [p.name for p in prompts] == ["GOOD"]
        assert prompts[0].description == LONG_BODY

    def test_no_prompts(self):
        assert asyncio.run(collect_prompts(FakeSession([]))) == []


@pytest.mark.asyncio
async def test_real_mcp_server_returns_full_skill_content():
    """End to end over a real MCP session: register the prompt the way the store's
    VirtualMcpServer._register_prompts does (truncated description, full content) and check the
    agent collects the full content."""
    server = FastMCP("store-like")
    description = _truncated_description(LONG_BODY)

    @server.prompt(name="SKILL", description=description)
    def skill_prompt():
        return LONG_BODY

    async with create_connected_server_and_client_session(server._mcp_server) as session:
        listed = await session.list_prompts()
        assert listed.prompts[0].description == "USER:"  # the listing really is truncated
        prompts = await collect_prompts(session)

    assert len(prompts) == 1
    assert prompts[0].description == LONG_BODY
