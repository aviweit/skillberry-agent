from typing_extensions import TypedDict
from typing import Annotated, List, Dict, Sequence
from langgraph.graph import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


# TODO: move to datamodel


class State(TypedDict):
    """
    The state of the main graph.

    """
    thinking_log: Annotated[list[AIMessage], add_messages]
    original_user_prompt: HumanMessage
    chat_history: list[BaseMessage]
    useful_tools: List[Dict[str, str]] # TODO: remove? 
    existing_tools: List[Dict[str, str]] # TODO: remove?
    need_to_generate_tools: List[Dict[str, str]] # TODO: remove?
    generated_tools: List[Dict[str, str]] # TODO: remove?
    skillberry_context: Dict[str, str]

    messages: Annotated[Sequence[BaseMessage], add_messages]
