import asyncio
import logging
from typing import Any, Dict, List, Optional

from config.config_ui import config
from utils.utils import SKILLBERRY_CONTEXT, flatten_keys, extract_base_url

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

    def search_skills(
        self,
        search_term: str,
        max_number_of_results: int = 5,
        similarity_threshold: float = 1.0,
    ):
        """
        Search for skills matching the given search term.

        Parameters:
            search_term (str): Search term to find matching skills
            max_number_of_results (int): Maximum number of results to return
            similarity_threshold (float): Similarity threshold for the search

        Returns:
            list: List of matching skills with name and similarity score

        Raises:
            Exception: Any failure occurred during execution

        """
        logger.info(f"search_skills called with search_term: '{search_term}', max_results: {max_number_of_results}, threshold: {similarity_threshold}")
        
        import requests
        params = {
            "search_term": search_term,
            "max_number_of_results": max_number_of_results,
            "similarity_threshold": similarity_threshold,
        }
        response = requests.get(f"{self.base_url}/search/skills", params=params)
        response.raise_for_status()
        results = response.json()
        logger.info(f"search_skills returned {len(results)} results: {results}")
        return results

    def get_skill(self, skill_name: str):
        """
        Retrieve the skill with the given name.

        Parameters:
            skill_name (str): The name of the skill

        Returns:
            dict: The skill object with full details including UUID

        Raises:
            Exception: Any failure occurred during execution

        """
        logger.info(f"get_skill called for skill: {skill_name}")
        
        import requests
        response = requests.get(f"{self.base_url}/skills/{skill_name}")
        response.raise_for_status()
        skill_data = response.json()
        logger.info(f"get_skill returned skill with UUID: {skill_data.get('uuid')}, name: {skill_data.get('name')}")
        logger.debug(f"Full skill data: {skill_data}")
        return skill_data

    def find_skill_uuid_by_search(self, search_term: str) -> Optional[str]:
        """
        Find a skill UUID by searching for a skill matching the search term.
        Returns the UUID of the first matching skill, or None if no match found.

        Parameters:
            search_term (str): Search term to find matching skill

        Returns:
            str or None: UUID of the first matching skill, or None if not found

        """
        logger.info(f"find_skill_uuid_by_search called with search_term: '{search_term}'")
        try:
            # Search for skills matching the term
            search_results = self.search_skills(search_term, max_number_of_results=1)
            
            if not search_results:
                logger.warning(f"No skills found matching search term: '{search_term}'")
                return None
            
            # Get the first matching skill name
            first_match = search_results[0]
            skill_name = first_match.get("filename")
            similarity_score = first_match.get("similarity_score", 0.0)
            
            logger.info(f"Found matching skill: '{skill_name}' with similarity score: {similarity_score}")
            
            # Get the full skill details to retrieve UUID
            skill_data = self.get_skill(skill_name)
            skill_uuid = skill_data.get("uuid")
            
            logger.info(f"Retrieved skill UUID: {skill_uuid} for skill: '{skill_name}'")
            return skill_uuid
            
        except Exception as e:
            logger.error(f"Error finding skill UUID for search term '{search_term}': {e}")
            return None

    def add_vmcp_server(self, name: str, description: str,
                        skill_uuid: Optional[str] = None,
                        skillberry_context: Optional[Dict] = None):
        """
        Creates a vmcp server on BTS with given parameters using skill-based approach.

        Parameters:
            name (str): Name of vmcp server
            description (str): Description of vmcp server
            skill_uuid (str): UUID of the skill to expose via the vmcp server (Optional)
            skillberry_context (dict): The context to be passed (Optional)

        Returns:
            dict: Success message with the server name, uuid, and port.

        Raises:
            Exception: Any failure occurred during execution.
        """
        logger.info(f"add_vmcp_server called for name: {name}, skill_uuid: {skill_uuid}")

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

        # Build query parameters for skill-based approach
        params = {}
        if name:
            params["name"] = name
        if description:
            params["description"] = description
        if skill_uuid:
            params["skill_uuid"] = skill_uuid
        
        # Use skill-based endpoint
        add_vmcp_server_url = f"{self.get_tools_service_base_url()}/vmcp_servers/"
        response = requests.post(
            add_vmcp_server_url, headers=headers, params=params)
        
        # If server already exists (409 Conflict), get its details instead
        if response.status_code == 409:
            logger.info(f"VMCP server '{name}' already exists, retrieving existing server details")
            try:
                existing_server = self.get_vmcp_server_details(name=name)
                logger.info(f"Reusing existing VMCP server: {existing_server}")
                return existing_server
            except Exception as e:
                logger.error(f"Failed to retrieve existing server '{name}': {e}")
                response.raise_for_status()  # Raise the original 409 error
        
        response.raise_for_status()
        return response.json()

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

    def get_mcp_tools(self, port: int, server_name: str = "tau2-tools") -> List[Any]:
        """Get tools from an MCP server via SSE transport.

        Args:
            port: The port number where the MCP server is running
            server_name: Name identifier for the MCP server (default: "tau2-tools")

        Returns:
            list: List of tools available from the MCP server

        Raises:
            Exception: Any failure occurred during execution.

        """
        logger.info(f"get_mcp_tools called for port: {port}, server_name: {server_name}")
        
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            # Construct the MCP server URL
            mcp_server_base_url = f"{extract_base_url(self.base_url)}:{port}"
            logger.info(f"Connecting to MCP server at: {mcp_server_base_url}/sse")
            
            # Create MCP client
            client = MultiServerMCPClient(
                {
                    server_name: {
                        "url": f"{mcp_server_base_url}/sse",
                        "transport": "sse",
                    }
                }
            )
            
            # Get tools from the MCP server
            # Check if we're already in an event loop (e.g., FastAPI context)
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context - run in a thread to avoid event loop conflict
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, client.get_tools())
                    tools = future.result()
            except RuntimeError:
                # No event loop running - safe to use asyncio.run()
                tools = asyncio.run(client.get_tools())
            
            logger.info(f"Retrieved {len(tools)} tools from MCP server: {[getattr(t, 'name', 'unknown') for t in tools]}")
            
            return tools
            
        except Exception as e:
            logger.error(f"Error getting MCP tools from port {port}: {e}")
            raise

    def get_mcp_prompts(self, port: int, server_name: str = "tau2-tools") -> List[Any]:
        """Get prompts from an MCP server via SSE transport.

        Args:
            port: The port number where the MCP server is running
            server_name: Name identifier for the MCP server (default: "tau2-tools")

        Returns:
            list: List of prompts available from the MCP server

        Raises:
            Exception: Any failure occurred during execution.

        """
        logger.info(f"get_mcp_prompts called for port: {port}, server_name: {server_name}")
        
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            # Construct the MCP server URL
            mcp_server_base_url = f"{extract_base_url(self.base_url)}:{port}"
            logger.info(f"Connecting to MCP server at: {mcp_server_base_url}/sse")
            
            # Create MCP client
            client = MultiServerMCPClient(
                {
                    server_name: {
                        "url": f"{mcp_server_base_url}/sse",
                        "transport": "sse",
                    }
                }
            )
            
            # Get prompts from the MCP server
            prompts = asyncio.run(client.get_prompts())
            logger.info(f"Retrieved {len(prompts)} prompts from MCP server: {[getattr(p, 'name', 'unknown') for p in prompts]}")
            
            return prompts
            
        except Exception as e:
            logger.error(f"Error getting MCP prompts from port {port}: {e}")
            raise


# Load configuration and set up the tools maker API
tools_service_base_url = config.get("tools_service_base_url")
tools_service = ToolsService(tools_service_base_url)
