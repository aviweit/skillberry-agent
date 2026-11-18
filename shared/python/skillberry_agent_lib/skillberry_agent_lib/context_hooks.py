"""
Per-request hooks driven by Skillberry context headers (``skillberry-context-*``).

A client turns a hook on for one request by sending its context header. With none of these
keys present, every hook is a no-op and the request is handled exactly as before.

Hooks:

- ``history_start_regex`` (header ``skillberry-context-history_start_regex``):
  drop the incoming chat history before the FIRST non-system message whose text matches the
  regex (``re.search``; anchor with ``^`` to match at the start of a message). That message and
  everything after it are kept, as are all system messages. When nothing matches, the history is
  kept whole and a warning is logged.

- ``template`` (headers ``skillberry-context-template-<var>[-<field>...]``, e.g.
  ``skillberry-context-template-main_user-email``): render the injected skill prompt text as a
  Jinja template with those values, e.g. ``{{ main_user.email }}``. Undefined variables are an
  error: the prompt is then injected unrendered and the error is logged.
"""

import logging
import re
from typing import Any, List, Optional

HISTORY_START_REGEX_KEY = "history_start_regex"
TEMPLATE_KEY = "template"

logger = logging.getLogger(__name__)


def _message_text(message: Any) -> str:
    """Text content of a LangChain message (string content or a list of content blocks)."""
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "\n".join(parts)
    return str(content)


def trim_chat_history(chat_history: List[Any], skillberry_context: Optional[dict]) -> List[Any]:
    """Apply the ``history_start_regex`` hook. Returns a new list; the input is not modified."""
    from langchain_core.messages import SystemMessage

    pattern = (skillberry_context or {}).get(HISTORY_START_REGEX_KEY)
    if not pattern:
        return chat_history
    try:
        regex = re.compile(pattern)
    except re.error as e:
        logger.error(f"Invalid {HISTORY_START_REGEX_KEY} {pattern!r}: {e}. Chat history kept whole.")
        return chat_history

    for index, message in enumerate(chat_history):
        if isinstance(message, SystemMessage):
            continue
        if regex.search(_message_text(message)):
            kept_system = [m for m in chat_history[:index] if isinstance(m, SystemMessage)]
            dropped = index - len(kept_system)
            logger.info(
                f"{HISTORY_START_REGEX_KEY}: history starts at message {index + 1} of {len(chat_history)}; "
                f"dropped {dropped} earlier message(s), kept {len(kept_system)} system message(s)."
            )
            return kept_system + list(chat_history[index:])

    logger.warning(f"{HISTORY_START_REGEX_KEY} {pattern!r} matched no message. Chat history kept whole.")
    return chat_history


def render_skill_prompt(prompt_text: str, skillberry_context: Optional[dict]) -> str:
    """Apply the ``template`` hook to the injected skill prompt text."""
    values = (skillberry_context or {}).get(TEMPLATE_KEY)
    if not prompt_text or not isinstance(values, dict) or not values:
        return prompt_text
    try:
        from jinja2 import Environment, StrictUndefined

        environment = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
        rendered = environment.from_string(prompt_text).render(**values)
    except Exception as e:  # jinja2 missing, a syntax error, or an undefined variable
        logger.error(f"Could not render the skill prompt with {TEMPLATE_KEY} values: {e}. Injected unrendered.")
        return prompt_text
    logger.info(f"Rendered the skill prompt with {TEMPLATE_KEY} values: {sorted(values)}")
    return rendered


__all__ = [
    "HISTORY_START_REGEX_KEY",
    "TEMPLATE_KEY",
    "render_skill_prompt",
    "trim_chat_history",
]
