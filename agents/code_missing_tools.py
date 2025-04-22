import logging

from config import config, config_structure
from agents.state import State

from utils.tools_maker_api import generate_tool_tools_maker


logger = logging.getLogger(__name__)


def code_missing_tools(state: State):
    thinking_log = []
    logging.info(f"=======>>> code_missing_tools. starts <<<=======")
    need_to_generate_tools = state["need_to_generate_tools"]
    generated_tools = []

    logging.info(f"code_missing_tools: need_to_generate_tools: {need_to_generate_tools}")
    for need_to_generate_tool in need_to_generate_tools:
        name = need_to_generate_tool.name

        # A flag that allows (or disallows) to generate tools dynamically by the agent
        my_config = config.DynamicConfig(config_structure.CONFIG_STRUCTURE)
        generate_tools_dynamically = my_config.get("generate_tools_dynamically")
        if not generate_tools_dynamically:
            thinking_log.append("I am not allowed to code new tools. ")
            logger.info(
                f"!!! generate_tools_dynamically is False: tool {name} will not be generated !!!")
            continue

        # TODO: response code, return values
        generate_tool_tools_maker(
            need_to_generate_tool.name,
            need_to_generate_tool.description,
            need_to_generate_tool.examples
        )

    logging.info(f"=======>>> code_missing_tools. ended <<<=======")
    # update the state with the generated tools

    return {
        "generated_tools": generated_tools,
        "thinking_log": thinking_log
    }
