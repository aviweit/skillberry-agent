import logging
from typing import Dict

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END

from agents.mcp_tools import mcp_tools
from agents.state import State


logger = logging.getLogger(__name__)

mcp_tools_agentic_graph = None


def define_mcp_agentic_graph():
    logger.info("!!!! define_mcp_agentic_graph !!!")
    global mcp_tools_agentic_graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("mcp_tools",
                           mcp_tools)

    graph_builder.add_edge(START, "mcp_tools")
    graph_builder.add_edge("mcp_tools", END)

    # Compile the agentic graph
    mcp_tools_agentic_graph = graph_builder.compile()
    logger.info("Tools agentic graph compiled")
    return mcp_tools_agentic_graph


def stream_graph_updates(chat_history: list[BaseMessage], skillberry_context: Dict):
    """
    Handles an incoming user prompt request. Uses a state graph built for an MCP mode

    Parameters:
        chat_history (list[BaseMessage]): incoming user prompt
        skillberry_context (Dict): The context

    """

    # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    # print(f"{input_messages}")
    # print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

    for event in mcp_tools_agentic_graph.stream({"chat_history": chat_history,
                                             "messages": chat_history,
                                             "skillberry_context": skillberry_context,
                                             "thinking_log": []}):
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        # print(f"{input_messages}")
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        for value in event.values():
            logging.info("==> stream_graph_updates: event.value: [%s]", value)
    values = event.values()
    return values
