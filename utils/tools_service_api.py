import logging
from typing import Dict

from config.config_ui import config
from utils.utils import SKILLBERRY_CONTEXT, flatten_keys

import blueberry_tools_service_sdk


logger = logging.getLogger(__name__)


# TODO: consider to be consistent across all sdk calls to
# raise an Exception/HTTPException during any adk call failures


# class for blueberry-tools-service-sdk
class ToolsService:
    def __init__(self, base_url=None):
        self.base_url = base_url if base_url else tools_service_base_url
        configuration = blueberry_tools_service_sdk.Configuration(host=self.base_url)
        with blueberry_tools_service_sdk.ApiClient(configuration) as api_client:
            self.manifest_api = blueberry_tools_service_sdk.ManifestApi(api_client)
            self.vmcpservers_api = blueberry_tools_service_sdk.VmcpServersApi(api_client)

    def get_tools_service_base_url(self):
        """
        Retrieve the tools service base URL.

        Returns:
            str: The tools service base URL

        """
        return self.base_url

    def check_communication(self):
        """
        Check connectivity status into the tools service.

        Returns:
            bool: whether connectivity succeeded

        """
        logger.info("check_communication called")
        try:
            self.manifest_api.get_manifest_manifests_uid_get("test")

        except blueberry_tools_service_sdk.ApiException as e:
            if e.status == 404:
                pass
            else:
                logger.error(f"Tools service is not reachable: {e}")
                return False
        logger.info("Tools service is up and running.")
        return True

    def get_tool_manifest(self, tool_name: str):
        """
        Retrieve the manifest with the given name using blueberry-tools-service-sdk.

        Parameters:
            tool_name (str): The name of the tool

        Returns:
            dict: the manifest

        """
        logger.info(f"get_manifest called for tool: {tool_name}")
        api_response = self.manifest_api.get_manifest_manifests_uid_get(tool_name)
        return api_response

    def search_tools(
        self,
        tool_name: str,
        tool_description: str,
        max_numer_of_results: int = 3,
        similarity_threshold: float = 1.0,
    ):
        """
        Invoke a tool denoted by tool_name with given parameters using blueberry-tools-service-sdk.

        Parameters:
            tool_name (str): Name of the tool to invoke
            tool_description (str): Description of the tool to invoke
            max_numer_of_results (int): Maximum number of results to return
            similarity_threshold (float): Similarity threshold for the search

        Returns:
            dict: return value result

        Raises:
            Exception: Any failure occurred during execution

        """
        logger.info(f"execute_tool called for tool: {tool_name}")
        response = self.manifest_api.search_manifest_search_manifests_get(
            search_term=f"{tool_description}",  # TODO: search term e.g., f"{tool_name}: {tool_description}"
            max_number_of_results=max_numer_of_results,
            similarity_threshold=similarity_threshold,
        )
        return response

    def execute_tool(self, tool_name: str, parameters: dict, http_headers: dict = None):
        """
        Invoke a tool denoted by tool_name with given parameters using blueberry-tools-service-sdk.

        Parameters:
            tool_name (str): Name of the tool to invoke
            parameters (dict): the parameter to pass (optional)

        Returns:
            dict: return value result

        Raises:
            Exception: Any failure occurred during execution

        """
        logger.info(f"execute_tool called for tool: {tool_name}")

        uid = tool_name

        execute_response = (
            self.manifest_api.execute_manifest_manifests_execute_uid_post(
                uid, parameters
            ) if not http_headers else
            self.manifest_api.execute_manifest_manifests_execute_uid_post_with_http_info(
                uid, parameters, _headers=http_headers
            ).data
        )
        # FIXME: should be const in all places
        return execute_response["return value"]

    def add_vmcp_server(self, name: str, description: str, tools: list,
                        skillberry_context: Dict = None):
        """
        Creates a vmcp server on BTS with given parameters.

        Parameters:
            name (str): Name of vmcp server
            description (str): Description of vmcp server
            tools (list): Tools of vmcp server 
            skillberry_context (dict): The context to be passed (Optional)

        Returns:
            dict: Success message with the server name.

        Raises:
            Exception: Any failure occurred during execution.
        """
        logger.info(f"add_vmcp_server called for name: {name}")

        # TODO: use bts sdk
        import requests
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        if skillberry_context:
            headers.update(
                flatten_keys(
                    {
                        SKILLBERRY_CONTEXT: skillberry_context
                    }
                )
            )

        data = {
            "name": name,
            "description": description,
            "tools": tools
        }
        add_vmcp_server_url = f"{self.get_tools_service_base_url()}/vmcp_servers/add"
        response = requests.post(
            add_vmcp_server_url, headers=headers, json=data)
        response.raise_for_status()

    def get_vmcp_server_details(self, name: str):
        """Get detailed information about a virtual MCP server.

        Retrieves comprehensive details about the specified virtual MCP server,
        including its configuration, port, and available tools.

        Args:
            name: The name of the virtual MCP server.

        Returns:
            dict: Detailed information about the virtual MCP server.

        Raises:
            Exception: Any failure occurred during execution.
        """
        # TODO: use bts sdk
        import requests
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        add_vmcp_server_url = f"{self.get_tools_service_base_url()}/vmcp_servers/{name}"
        response = requests.get(
            add_vmcp_server_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def remove_vmcp_server(self, name: str):
        """Remove a virtual MCP server

        Args:
            name: The name of the virtual MCP server to remove.

        Raises:
            Exception: Any failure occurred during execution.

        """
        # TODO: use bts sdk
        import requests
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        remove_vmcp_server_url = f"{self.get_tools_service_base_url()}/vmcp_servers/{name}"
        response = requests.delete(
            remove_vmcp_server_url, headers=headers)
        response.raise_for_status()
        return response.json()


# Load configuration and set up the tools maker API
tools_service_base_url = config.get("tools_service_base_url")
tools_service = ToolsService(tools_service_base_url)
