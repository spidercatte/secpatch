
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters # Import MCPToolset
import os # For GITHUB_PERSONAL_ACCESS_TOKEN

from secpatch.sub_agents.vuln_fix import prompt
from secpatch.tools import git_tool # Import your custom git_tool.py
from secpatch.tools import utility_tools



MODEL = "gemini-2.5-pro-preview-05-06"

# --- GitHub MCP Toolset Configuration (similar to github_assistant_agent.py) ---
GITHUB_PERSONAL_ACCESS_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
if not GITHUB_PERSONAL_ACCESS_TOKEN:
    raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN environment variable not set for GitHub MCP server.")

github_mcp_server_command = "/Users/catbalajadia/Downloads/google_hack/github-mcp-server/cmd/github-mcp-server/github-mcp-server"

# Higher-order function to execute a tool with proper cleanup
async def execute_tool(tool, args):
    """Execute a single tool and handle cleanup."""
    try:
        result = await tool.run_async(args=args, tool_context=None)
        return (True, result, None)  # Success, result, no error
    except Exception as e:
        return (False, None, str(e))  # Failed, no result, error message


# Function to try tools sequentially until one succeeds
async def try_tools_sequentially(tools, args, exit_stack):
    """Try each tool in sequence until one succeeds."""
    errors = []
    
    for tool in tools:
        success, result, error = await execute_tool(tool, args)
        if success:
            return result
        errors.append(f"Tool '{tool.name}' failed: {error}")
    
    if errors:
        return f"All tools failed: {'; '.join(errors)}"
    return "No tools available"


# Create a higher-order function that handles connection and resource management
def create_mcp_tool_executor(command, args=None, env=None, tool_filter=None):
    """Create a function that connects to an MCP server and executes tools."""
    async def mcp_tool_executor(**kwargs):
        # Connect to MCP server
        tools, exit_stack = await MCPToolset.from_server(
            connection_params=StdioServerParameters(
                command=command,
                args=args or [],
                env=env or {},
            ),
            # Optional: Filter which tools from the MCP server are exposed
            tool_filter=tool_filter or [],
        )
        
        try:
            # Try all tools until one succeeds
            return await try_tools_sequentially(tools, kwargs, exit_stack)
        finally:
            # Always cleanup
            await exit_stack.aclose()
    
    return mcp_tool_executor


# Create our YouTube search function
github_tools = create_mcp_tool_executor(
    command=github_mcp_server_command,
    args=["stdio"],
    env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_PERSONAL_ACCESS_TOKEN,
        "GITHUB_TOOLSETS": "repos,issues,pull_requests,code_security"  # Specify desired toolsets
    }
)

TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/temp")  # Define the target folder path for file operations
# Create our YouTube search function
file_tools = create_mcp_tool_executor(
    command='npx',
    args=[
        '-y',  # Arguments for the command
        '@modelcontextprotocol/server-filesystem',
        os.path.abspath(TARGET_FOLDER_PATH),
    ],
    tool_filter=[
        'read_file',
        'read_multiple_files',
        'list_directory',
        'directory_tree',
        'search_files',
        'get_file_info',
        'list_allowed_directories',
    ],
)
