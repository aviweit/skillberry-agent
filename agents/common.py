import json
import logging
import re
from typing import (
    Any,
    Annotated,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypedDict,
    Union,
)

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool

from langgraph.graph.message import add_messages


logger = logging.getLogger(__name__)


class ReactToolsCallingAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    _tools: Sequence[Union[Dict[str, Any], Type, Callable, BaseTool]]
    _llm: LanguageModelInput


def parse_tool_call_from_content(content: str) -> Optional[List[Dict[str, Any]]]:
    match = re.search(r"\{.*\}", content)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        
        # Support multiple field name variations for backward compatibility
        # Try "parameters" first (OpenAI standard), then "arguments" (common alternative)
        args = parsed.get("parameters")
        if args is None:
            args = parsed.get("arguments", {})
        
        # Support both "name" and "function" fields for tool name
        name = parsed.get("name")
        if not name:
            name = parsed.get("function", "")
        
        return [
            {
                "type": parsed.get("type", "function"),
                "name": name,
                "args": args,
                "id": parsed.get("id", "0"),
            }
        ]
    except json.JSONDecodeError as e:
        logger.error (f"parse_tool_call_from_content: json.JSONDecodeError: {e}")
        return None


def normalize_tool_node(state: ReactToolsCallingAgentState) -> Dict[str, Any]:
    thinking_log = ""
    if not state or "messages" not in state or not state["messages"]:
        thinking_log += "empty state nothing to normalize. "
        logging.info("normalize_tool_node: empty state nothing to normalize.")
        return {"messages": state.get("messages", []), "thinking_log": thinking_log}

    # shallow copy
    messages = state["messages"][:]
    last_message = messages[-1]

    logging.info(f"ENTER normalize_tool_node with {last_message}")

    tool_calls = getattr(last_message, "tool_calls", None)
    content = getattr(last_message, "content", "")

    # Could either be None or []
    if not tool_calls:
        parsed_tool_calls = parse_tool_call_from_content(content)
        if parsed_tool_calls:
            thinking_log += "parsed tool calls from content. "
            normalized = AIMessage(
                content="",
                tool_calls=parsed_tool_calls
            )
            logging.info(f"normalize_tool_node: replacing last message with normalized message: {normalized}")
            messages[-1] = normalized
        else:
            thinking_log += "no tool calls found leaving message unchanged. "
            logging.info("normalize_tool_node: no tool calls found leaving message unchanged.")
    else:
        thinking_log += "tool calls already present leaving message unchanged. "
        logging.info("normalize_tool_node: tool calls already present leaving message unchanged.")

    return {"messages": messages, "thinking_log": thinking_log}
