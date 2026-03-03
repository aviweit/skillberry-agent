# Skillberry Agent - Store Communication Pattern

## Overview

The Skillberry agent has been updated to communicate with the Skillberry Store using a pattern similar to the Tau2 LangChain Agent MCP implementation. This document describes the communication architecture and how to use both the new skill-based approach and the legacy tool-list approach.

## Installation

### Required Dependencies

The following packages are required and included in `requirements.txt` and `pyproject.toml`:

1. **langchain-mcp-adapters** (>=0.2.1) - MCP protocol adapter for LangChain
2. **blueberry_tools_service_sdk** - Skillberry Store SDK (installed from git)
3. **langchain** (>=0.3.25) - LangChain framework
4. **langchain_core** (>=0.3.59) - LangChain core components
5. **requests** (>=2.32.3) - HTTP client library

### Installing from requirements.txt

```bash
pip install -r requirements.txt
```

This will install all dependencies including:
- The MCP adapter from PyPI
- The Skillberry Store SDK from the git repository

### Installing from pyproject.toml

```bash
pip install -e .
```

**Note**: The `blueberry_tools_service_sdk` must be installed separately as it's not available on PyPI:

```bash
pip install git+ssh://git@github.ibm.com/Blueberry/blueberry-sdk.git#subdirectory=blueberry_tools_service_sdk
```

### Verifying Installation

```python
# Verify MCP adapter
from langchain_mcp_adapters.client import MultiServerMCPClient
print("MCP adapter installed successfully")

# Verify Skillberry SDK
import blueberry_tools_service_sdk
print("Skillberry SDK installed successfully")

# Verify ToolsService
from utils.tools_service_api import tools_service
print(f"Tools service base URL: {tools_service.get_tools_service_base_url()}")
```

## Communication Architecture

### Entry Points

1. **Initialization** - When the agent starts, it creates or reuses a virtual MCP server
2. **Execution** - The `mcp_tools` node in the LangGraph workflow handles tool execution
3. **Cleanup** - The virtual MCP server is removed when the session ends

### Communication Flow

```
Agent Initialization
    ↓
VirtualMcpServerManager.add_server()
    ↓
ToolsService API Client
    ↓
Skillberry Store (HTTP REST API)
    ├─ Search Skills: GET /search/skills
    ├─ Get Skill Details: GET /skills/{name}
    ├─ Create VMCP Server: POST /vmcp_servers/
    └─ Get Server Details: GET /vmcp_servers/{name}
    ↓
MCP Client (MultiServerMCPClient)
    ↓
Virtual MCP Server (SSE Transport)
    ↓
Tool Execution
```

## Features

### 1. Skill Search and Discovery (Required)

The `ToolsService` class now supports searching for skills in the Skillberry Store:

```python
# Search for skills
results = tools_service.search_skills(
    search_term="airline",
    max_number_of_results=5,
    similarity_threshold=1.0
)

# Get skill details including UUID
skill_data = tools_service.get_skill(skill_name="airline_booking")
skill_uuid = skill_data.get("uuid")

# Find skill UUID by search term (convenience method)
skill_uuid = tools_service.find_skill_uuid_by_search("airline")
```

### 2. Skill-Based VMCP Server Creation (Only Approach)

Virtual MCP servers are created using skill UUIDs:

```python
# Create server with skill UUID
tools_service.add_vmcp_server(
    name="my-server",
    description="Server description",
    skill_uuid="abc-123-def-456",
    skillberry_context={"env_id": "env123", "task_id": "task456"}
)
```

### 3. MCP Tool Retrieval

Tools can be retrieved directly from an MCP server via SSE transport:

```python
# Get tools from MCP server
tools = tools_service.get_mcp_tools(
    port=8001,
    server_name="my-server"
)
```

### 4. VirtualMcpServerManager

The manager uses skill-based approach exclusively:

```python
# Skill-based approach with search term
server = vmsm.add_server(
    skillberry_context=context,
    skill_search_term="airline"
)

# Or with direct UUID
server = vmsm.add_server(
    skillberry_context=context,
    skill_uuid="abc-123-def-456"
)
```

## Configuration

Only the tools service base URL needs to be configured:

```python
config = {
    "tools_service_base_url": "http://localhost:8000"  # Required: Tools service URL
}
```

**Note**: The skill search term is hardcoded as `"airline"` in the agent code, matching the Tau2 LangChain agent pattern. To use a different skill, modify the `search_term` variable in [`agents/mcp_tools.py`](agents/mcp_tools.py:215).

## API Methods Added

### ToolsService Class (`utils/tools_service_api.py`)

#### New Methods:

1. **`search_skills(search_term, max_number_of_results, similarity_threshold)`**
   - Search for skills matching a search term
   - Returns list of matching skills with similarity scores

2. **`get_skill(skill_name)`**
   - Retrieve full skill details including UUID
   - Returns skill object with metadata

3. **`find_skill_uuid_by_search(search_term)`**
   - Convenience method to find skill UUID by search term
   - Returns UUID of first matching skill or None

4. **`get_mcp_tools(port, server_name)`**
   - Retrieve tools from MCP server via SSE transport
   - Returns list of LangChain-compatible tool objects

5. **`get_mcp_prompts(port, server_name)`**
   - Retrieve prompts from MCP server via SSE transport
   - Returns list of prompt objects

#### Updated Methods:

1. **`add_vmcp_server(name, description, tools, skill_uuid, skillberry_context)`**
   - Now supports both `tools` (list) and `skill_uuid` (string) parameters
   - Automatically handles 409 Conflict (server already exists)
   - Uses appropriate endpoint based on parameters

### VirtualMcpServerManager Class (`agents/vmcp_server_manager.py`)

#### Updated Methods:

1. **`add_server(skillberry_context, tools, skill_search_term, skill_uuid)`**
   - Supports three approaches:
     - Skill search: `skill_search_term` parameter
     - Direct skill: `skill_uuid` parameter
     - Tool list: `tools` parameter (backward compatible)
   - Reuses existing servers when found
   - Creates consistent server names based on env_id

## Comparison with Tau2 LangChain Agent

### Similarities:

1. **Skill-based approach**: Both search for skills and create servers with skill UUIDs
2. **Context propagation**: Both pass skillberry_context through HTTP headers
3. **MCP client usage**: Both use MultiServerMCPClient with SSE transport
4. **Server reuse**: Both check for existing servers before creating new ones
5. **Tool retrieval**: Both retrieve tools via MCP protocol
6. **Skill-only**: Both use skill-based approach exclusively (no tool-list support)

### Differences:

1. **Architecture**:
   - Tau2: Agent class manages server lifecycle
   - Skillberry: Separate VirtualMcpServerManager handles servers

2. **Server naming**:
   - Tau2: Fixed name "tau2-vmcp-server"
   - Skillberry: Dynamic name "skillberry-{env_id[:8]}"

3. **Configuration**:
   - Tau2: Hardcoded search term in agent code
   - Skillberry: Configurable via `mcp_skill_search_term` (required)

## Usage Examples

### Example 1: Automatic Skill Search (Default)

```python
from agents.vmcp_server_manager import vmsm

# Create context
skillberry_context = {
    "env_id": "env-123",
    "task_id": "task-456",
    "plugin": "skillberry"
}

# Add server (will automatically search for "airline" skill)
# The search term is hardcoded in mcp_tools.py
server = vmsm.add_server(
    skillberry_context,
    skill_search_term="airline"
)

print(f"Server created: {server.name} on port {server.port}")
print(f"Available tools: {server.tools}")
```

### Example 2: Using Direct Skill UUID

```python
from agents.vmcp_server_manager import vmsm

# If you already have a skill UUID
server = vmsm.add_server(
    skillberry_context,
    skill_uuid="abc-123-def-456"
)
```

## Migration Guide

### Breaking Changes

**The tool-list approach is no longer supported.** All code must be updated to use the skill-based approach.

### Required Changes

1. **Update add_server calls** - Remove `tools` parameter:
```python
# Before (no longer works)
server = vmsm.add_server(skillberry_context, tools=TOOLS+GENERATED_TOOLS)

# After (required)
server = vmsm.add_server(skillberry_context, skill_search_term="airline")
```

2. **Ensure skills exist** - Skills must be registered in the Skillberry Store before use

3. **Change search term** (optional) - To use a different skill, modify the hardcoded `search_term` in [`agents/mcp_tools.py`](agents/mcp_tools.py:215)

## Error Handling

The implementation includes robust error handling:

1. **Server already exists**: Automatically reuses existing server
2. **Skill not found**: Logs warning and creates server without skill
3. **MCP connection errors**: Raises exception with detailed error message
4. **Event loop conflicts**: Handles both sync and async contexts

## Testing

To test the new functionality:

```python
from utils.tools_service_api import tools_service

# Test skill search
results = tools_service.search_skills("airline")
print(f"Found {len(results)} skills")

# Test skill UUID retrieval
uuid = tools_service.find_skill_uuid_by_search("airline")
print(f"Skill UUID: {uuid}")

# Test MCP tools retrieval
tools = tools_service.get_mcp_tools(port=8001)
print(f"Retrieved {len(tools)} tools")
```

## Troubleshooting

### Issue: "No skills found"
- Check that skills are properly indexed in the Skillberry Store
- Verify the search term matches skill names or descriptions
- Try lowering the similarity_threshold

### Issue: "Server already exists (409)"
- This is normal - the system will reuse the existing server
- To force recreation, manually remove the server first

### Issue: "Cannot connect to MCP server"
- Verify the tools service is running
- Check the port number is correct
- Ensure SSE endpoint is accessible at `http://host:port/sse`

## Future Enhancements

Potential improvements for future versions:

1. Support for multiple skills per server
2. Dynamic skill selection based on task context
3. Skill versioning and updates
4. Performance metrics and monitoring
5. Caching of skill search results
6. Automatic skill discovery based on task requirements