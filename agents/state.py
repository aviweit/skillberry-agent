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
    chat_history: list[BaseMessage]
    messages: Annotated[Sequence[BaseMessage], add_messages]
    skillberry_context: Dict[str, str]
