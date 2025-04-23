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

        try:
            response = generate_tool_tools_maker(
                need_to_generate_tool.name,
                need_to_generate_tool.description,
                need_to_generate_tool.examples
            )

            generated_tools.append({
                "name": response["name"],
                "description": response["description"]
            })
        except Exception as e:
            logger.error(f"code_missing_tools: generate_tool for '{name}' failed: {str(e)}")

    if len(generated_tools) > 0:
        thinking_log.append("I just coded ephemeral tools that I will use.")
        tool_descriptions = ""
        for i, tool in enumerate(generated_tools):
            tool_description = tool["description"]
            tool_descriptions += f"{tool_description} "
            if i < len(generated_tools) - 1:
                tool_descriptions += ", and a tool that "
            else:
                tool_descriptions += "."

        thinking_log.append(f"a tool that {tool_descriptions}")

    logging.info(f"=======>>> code_missing_tools. ended <<<=======")

    return {
        "generated_tools": generated_tools,
        "thinking_log": thinking_log
    }
