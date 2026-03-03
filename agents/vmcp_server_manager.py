import logging
from typing import Dict, List, Optional
import uuid

from data_model.virtual_mcp_server import VirtualMcpServer
from utils.tools_service_api import tools_service


logger = logging.getLogger(__name__)


class VirtualMcpServerManager:
    """
    Manages virtual MCP servers for the Skillberry Agent.

    This class provides functionality to create, manage, and remove virtual MCP servers.
    Supports both tool-list and skill-based approaches.
    """

    def __init__(self):
        """
        Initialize the virtual MCP server manager.

        """
        # env_id -> server map
        self.servers: Dict[str, VirtualMcpServer] = {}

    def add_server(
        self,
        skillberry_context: Dict,
        skill_search_term: Optional[str] = None,
        skill_uuid: Optional[str] = None
    ) -> VirtualMcpServer:
        """
        Add a new virtual MCP server using skill-based approach.

        Args:
            skillberry_context: The context of the MCP server
            skill_search_term: Search term to find a skill (Optional)
            skill_uuid: UUID of the skill to use (Optional)

        Returns:
            VirtualMcpServer: The created virtual MCP server instance.

        Raises:
            ValueError: If neither skill_search_term nor skill_uuid is provided

        """
        env_id = skillberry_context["env_id"]
        name = f"skillberry-{env_id[:8]}"
        logger.info(f"Adding vmcp_server: '{name}'")

        # Check if server already exists
        vmcp_server_info = None
        try:
            vmcp_server_info = tools_service.get_vmcp_server_details(name=name)
            logger.info(f"Found existing vmcp_server: '{name}', reusing it")
        except Exception as e:
            logger.info(f"No existing vmcp_server found (or error checking): {e}")
            logger.info(f"Will create new vmcp_server: '{name}'")

        # If server doesn't exist, create it
        if vmcp_server_info is None:
            # Skill-based approach only
            if not skill_uuid and skill_search_term:
                logger.info(f"Searching for skill with search term: '{skill_search_term}'")
                skill_uuid = tools_service.find_skill_uuid_by_search(skill_search_term)
                
                if skill_uuid:
                    logger.info(f"Found skill UUID: {skill_uuid} for search term: '{skill_search_term}'")
                else:
                    logger.warning(f"No skill found for search term: '{skill_search_term}', creating vmcp server without skill")
            
            if not skill_uuid and not skill_search_term:
                raise ValueError("Either skill_search_term or skill_uuid must be provided")
            
            # Create vmcp server with skill_uuid
            logger.info(f"Creating vmcp_server '{name}' with skill_uuid: {skill_uuid}")
            tools_service.add_vmcp_server(
                name=name,
                description=f"Skillberry MCP Server for env_id {env_id}",
                skill_uuid=skill_uuid,
                skillberry_context=skillberry_context
            )
            
            logger.info(f"VMCP server created")
            
            # Get full server details including runtime information
            logger.info(f"Getting vmcp_server details for: '{name}'")
            vmcp_server_info = tools_service.get_vmcp_server_details(name=name)
            logger.info(f"Retrieved vmcp_server_info: {vmcp_server_info}")

        server = VirtualMcpServer(**vmcp_server_info)

        logger.info(f"Add Mapping {env_id} <-> server '{name}'")
        self.servers[env_id] = server

        logger.info(f"Added and started vmcp_server: {name} on port {server.port} for env_id {env_id}")
        return server

    def remove_server(self, skillberry_context: Dict):
        """
        Remove a virtual MCP server and delete it from servers list

        Args:
            skillberry_context: The context of the MCP server

        Raises:
            ValueError: If the virtual MCP server is not found.
        """
        env_id = skillberry_context["env_id"]

        if env_id in self.servers:
            server = self.servers[env_id]
            name = server.name
            logger.info(f"Removing vmcp_server: '{name}'")
            tools_service.remove_vmcp_server(name)

            logger.info(f"Remove Mapping {env_id} <-> server '{name}'")
            del self.servers[env_id]
        else:
            raise ValueError(f"Mapping {env_id} <-> server not found")

    def get_server(self, skillberry_context: Dict) -> VirtualMcpServer:
        """
        Get detailed information about a virtual MCP server.

        Args:
            skillberry_context: The context of the MCP server

        Returns:
            VirtualMcpServer: The virtual MCP server instance.

        """
        env_id = skillberry_context["env_id"]

        return self.servers[env_id]


# FIXME: make this singleton concurrent robust (and inside function) -
# consider to use threading.RLock() around servers manipulation functions
vmsm = VirtualMcpServerManager()
