import logging

from config import config, config_structure

import blueberry_tools_maker_sdk
from pprint import pprint


logger = logging.getLogger(__name__)


# Load configuration
my_config = config.DynamicConfig(config_structure.CONFIG_STRUCTURE)
tools_maker_base_url = my_config.get("tools_maker_base_url")


def generate_tool_tools_maker(
        tool_name: str,
        tool_description: str,
        tool_examples: str,
        skip_validation: bool = False
    ):
    """
    Request blueberry tools maker to generate a tool with the given name, description and examples using
    blueberry-tools-maker-sdk.

    Parameters:
        tool_name (str): tool name
        tool_description (str): tool description
        tool_examples (str): tool examples
        skip_validation (bool): whether to skip validation process

    Returns:
        bool: whether operation succeed

    """
    logger.info(f"generate_tool_tools_maker called for tool: {tool_name}")

    configuration = blueberry_tools_maker_sdk.Configuration(
        host = tools_maker_base_url
    )

    with blueberry_tools_maker_sdk.ApiClient(configuration) as api_client:
        api_instance = blueberry_tools_maker_sdk.ApiApi(api_client)
        skip_validation = False # bool |  (optional) (default to False)

        try:
            api_response = api_instance.api_generate_tool_generate_tool_tool_name_post(
                tool_name,
                tool_description,
                tool_examples,
                skip_validation=skip_validation
            )
            # TODO: remove print
            print("The response of ApiApi->api_generate_tool_generate_tool_tool_name_post:\n")
            pprint(api_response)
            return True
        except Exception as e:
            print("Exception when calling ApiApi->api_generate_tool_generate_tool_tool_name_post: %s\n" % e)
            return False
