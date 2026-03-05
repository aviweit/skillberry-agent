import logging
from typing import Dict, List, Optional
import uuid

from data_model.virtual_mcp_server import VirtualMcpServer
from utils.skillberry_api import skillberry_api


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
        # Single server instance (singleton pattern)
        self.server: Optional[VirtualMcpServer] = None
        self.server_skill_uuid: Optional[str] = None

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
            ValueError: If neither skill_search_term nor skill_uuid is provided, or if
                       an existing server with a different UUID is found

        """
        env_id = skillberry_context["env_id"]
        name = f"skillberry-singleton"
        logger.info(f"Adding vmcp_server: '{name}'")

        # Resolve skill_uuid if needed
        resolved_skill_uuid = skill_uuid
        if not resolved_skill_uuid and skill_search_term:
            logger.info(f"Searching for skill with search term: '{skill_search_term}'")
            resolved_skill_uuid = skillberry_api.find_skill_uuid_by_search(skill_search_term)
            
            if resolved_skill_uuid:
                logger.info(f"Found skill UUID: {resolved_skill_uuid} for search term: '{skill_search_term}'")
            else:
                logger.warning(f"No skill found for search term: '{skill_search_term}', creating vmcp server without skill")
        
        if not resolved_skill_uuid and not skill_search_term:
            raise ValueError("Either skill_search_term or skill_uuid must be provided")

        # Check if singleton server already exists
        if self.server is not None:
            logger.info(f"Found existing singleton vmcp_server: '{self.server.name}'")
            
            # Check if existing server has different skill_uuid
            if self.server_skill_uuid and resolved_skill_uuid and self.server_skill_uuid != resolved_skill_uuid:
                raise ValueError(
                    f"VMCP server '{self.server.name}' already exists with skill_uuid '{self.server_skill_uuid}', "
                    f"but requested skill_uuid is '{resolved_skill_uuid}'. "
                    f"Please remove the existing server first or use the same skill_uuid."
                )
            
            logger.info(f"Reusing existing singleton vmcp_server: '{self.server.name}' with skill_uuid: {self.server_skill_uuid}")
            return self.server

        # Check if server already exists in backend
        vmcp_server_info = None
        try:
            vmcp_server_info = skillberry_api.get_vmcp_server_details(name=name)
            logger.info(f"Found existing vmcp_server in backend: '{name}'")
            
            # Check if existing server has different skill_uuid
            existing_skill_uuid = vmcp_server_info.get("skill_uuid")
            if existing_skill_uuid and resolved_skill_uuid and existing_skill_uuid != resolved_skill_uuid:
                raise ValueError(
                    f"VMCP server '{name}' already exists with skill_uuid '{existing_skill_uuid}', "
                    f"but requested skill_uuid is '{resolved_skill_uuid}'. "
                    f"Please remove the existing server first or use the same skill_uuid."
                )
            
            logger.info(f"Reusing existing vmcp_server from backend: '{name}' with skill_uuid: {existing_skill_uuid}")
        except ValueError:
            # Re-raise ValueError for UUID mismatch
            raise
        except Exception as e:
            logger.info(f"No existing vmcp_server found in backend (or error checking): {e}")
            logger.info(f"Will create new vmcp_server: '{name}'")

        # If server doesn't exist, create it
        if vmcp_server_info is None:
            # Create vmcp server with skill_uuid
            logger.info(f"Creating vmcp_server '{name}' with skill_uuid: {resolved_skill_uuid}")
            skillberry_api.add_vmcp_server(
                name=name,
                description=f"Skillberry MCP Server (singleton)",
                skill_uuid=resolved_skill_uuid,
                skillberry_context=skillberry_context
            )
            
            logger.info(f"VMCP server created")
            
            # Get full server details including runtime information
            logger.info(f"Getting vmcp_server details for: '{name}'")
            vmcp_server_info = skillberry_api.get_vmcp_server_details(name=name)
            logger.info(f"Retrieved vmcp_server_info: {vmcp_server_info}")

        server = VirtualMcpServer(**vmcp_server_info)

        logger.info(f"Storing singleton server '{name}'")
        self.server = server
        self.server_skill_uuid = resolved_skill_uuid

        logger.info(f"Added and started singleton vmcp_server: {name} on port {server.port}")
        return server

    def remove_server(self, skillberry_context: Dict):
        """
        Remove the singleton virtual MCP server

        Args:
            skillberry_context: The context of the MCP server

        Raises:
            ValueError: If the virtual MCP server is not found.
        """
        name = f"skillberry-singleton"

        if self.server is not None:
            logger.info(f"Removing singleton vmcp_server: {name} on port {self.server.port}")
            skillberry_api.remove_vmcp_server(name=name)
            logger.info(f"Removed singleton vmcp_server: {name}")

            # Clear singleton references
            self.server = None
            self.server_skill_uuid = None
        else:
            raise ValueError(f"No singleton server found to remove")

    def get_server(self, skillberry_context: Dict) -> VirtualMcpServer:
        """
        Get the singleton virtual MCP server.

        Args:
            skillberry_context: The context of the MCP server

        Returns:
            VirtualMcpServer: The virtual MCP server instance.

        Raises:
            KeyError: If no server exists

        """
        if self.server is None:
            raise KeyError("No singleton server exists")
        
        return self.server


# FIXME: make this singleton concurrent robust (and inside function) -
# consider to use threading.RLock() around servers manipulation functions
vmsm = VirtualMcpServerManager()
