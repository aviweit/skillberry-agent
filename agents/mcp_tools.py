import asyncio
import json
import logging

from typing import (
    Annotated,
    Sequence,
    TypedDict,
)

from langchain_core.language_models import LanguageModelInput
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig

from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from agents.remote_tools_wrapper import TOOLS
from agents.state import State
from agents.vmcp_server_manager import vmsm
from llm.common import current_llm
from config.config_ui import config as _config
from utils.utils import extract_base_url


logger = logging.getLogger(__name__)


execute_tools_with_parameters_chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert assistant"),
        (
            "system",
            "If a tool returns an exception, and error, no result or any other failure, "
            "return to the user immediately! and the user to provide additional information or clarification. "
            "DO NOT try to call any additional tools or functions until the user provides additional information or clarification.",
        ),
        (
            "system",
            "Try to use tools and ask the user for clarification and additional information as much as possible. "
            " If, and only if this completely fails, use the transfer_to_human_agents tool.",
        ),
        "{chat_history}",
        (
            "system",
            "DO NOT USE the transfer_to_human_agents tool !!!",
        ),
    ]
)


class ReactToolsCallingAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    _llm: LanguageModelInput


def call_llm_model_node(state: ReactToolsCallingAgentState, config: RunnableConfig):
    messages = state["messages"]
    last_message = state["messages"][-1]

    logging.info(f"=====> Calling LLM to response (call_llm_model_node).")
    logging.info(f"Latest message is: {last_message}")

    response = state["_llm"].invoke(messages, config)
    return {"messages": [response]}


def mcp_tools(state: State):
    """
    Defines and compiles a LangGraph workflow for a react-style agent, connecting
    LLM and tool nodes with conditional logic to control execution flow.

    Note: This method/node selects the proper MCP server (using context) for LLM completion.

    If no MCP server is found out from the given environment ID (passed in skillberry_context),
    a new MCP server is created and get loaded with Tau2 tools. The MCP server is removed once the
    scenario completes (via "disconnect" control command).  

    """
    logging.info(f"=======>>> Node: mcp_tools. started <<<=======")
    thinking_log = ""

    chat_history = state["chat_history"]
    skillberry_context = state["skillberry_context"]
    tools_service_base_url = _config.get("tools_service_base_url")

    try:
        server = vmsm.get_server(skillberry_context)
    except: # not found
        server = vmsm.add_server(skillberry_context, tools=TOOLS)

    port = server.port
    mcp_client_base_url = f"{extract_base_url(tools_service_base_url)}:{port}"
    client = MultiServerMCPClient(
        {
            "tau2-tools": {
                "url": f"{mcp_client_base_url}/sse",
                "transport": "sse",
            }
        }
    )

    tools = asyncio.run(client.get_tools())

    try:
        if not tools:
            thinking_log += (
                "I don't have any tools to use. using the LLM model as-is to response. "
            )
            logging.info(f"=====> No tools, not binding")
            llm_with_tools = current_llm.llm
        else:
            thinking_log += "I will now use the tools and the LLM model to respond. "
            logging.info(f"=====> Binding tools: {tools}")
            llm_with_tools = current_llm.llm.bind_tools(
                tools=tools, tool_choice="auto"
            )

    except Exception as e:
        logging.error(f"Error while binding tools: {e}")
        return {
            "messages": [
                {
                    "role": "ai",
                    "content": json.dumps(
                        {
                            "output": "Sorry, failed to answer using blueberry (tools binding)"
                        },
                        indent=4,
                    ),
                }
            ]
        }

    workflow = StateGraph(ReactToolsCallingAgentState)
    workflow.set_entry_point("llm")
    workflow.add_node("llm", call_llm_model_node)
    workflow.add_node(ToolNode(tools))
    workflow.add_edge("tools", "llm")
    workflow.add_conditional_edges(
        "llm",
        tools_condition,
    )
    graph = workflow.compile()

    async def trace_stream(stream):
        """
        Helper function for formatting the stream nicely

        """
        _final_message = None

        async for s in stream:
            message = s["messages"][-1]
            logging.info(message)
            _final_message = message
        return _final_message

    original_chat_messages = execute_tools_with_parameters_chat_prompt_template.invoke(
        chat_history
    )

    try:
        logging.info(f"=====> Invoking the tools react agent")
        recursion_limit = _config.get("tools_react_agent__recursion_limit")
        final_message = asyncio.run (trace_stream(graph.astream(
            {
                "messages": original_chat_messages.to_messages(),
                "_llm": llm_with_tools
            },
            {
                "recursion_limit": recursion_limit,
                "max_execution_time": 120
            },
            stream_mode="values",
        )))
    except Exception as e:
        logging.error(f"Error while streaming to the react agent: {e}")
        return {
            "messages": [
                {
                    "role": "ai",
                    "content": json.dumps(
                        f"Sorry, failed to answer using blueberry (invoke react agent)",
                        indent=4,
                    ),
                }
            ]
        }

    logger.info(
        f"=====> The agentic flow has finished executing the tools with parameters"
    )
    try:
        ai_response = final_message.content

        thinking_log += f"I am done. Returning a response to the user."
        session_thinking_log_as_str = ""
        for state_thinking_log in state["thinking_log"]:
            session_thinking_log_as_str = " ".join(
                [session_thinking_log_as_str, state_thinking_log.content]
            )
        session_thinking_log_as_str = " ".join(
            [session_thinking_log_as_str, thinking_log]
        )

        output_content = f"<think>{session_thinking_log_as_str}</think>\n{ai_response}"
    except Exception as e:
        logging.error(f"Error while json.dumps: {e}")
        output_content = "Sorry, failed to answer using blueberry (json.dumps)"

    logger.info(f"output_content: {output_content}")

    messages = [{"role": "ai", "content": output_content}]
    logging.info(f"=======>>> Node: mcp_tools. ended <<<=======")
    return {"messages": messages, "thinking_log": thinking_log}
