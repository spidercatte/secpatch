from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters # Import MCPToolset
import os # For GITHUB_PERSONAL_ACCESS_TOKEN

from secpatch.sub_agents.vuln_fix import prompt
from secpatch.tools import git_tool # Import your custom git_tool.py
from secpatch.tools import utility_tools


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


# Create a higher-order function that handles connection and resource management
def create_mcp_tool_executor(command, args=None, env=None):
    """
    Create a function that connects to an MCP server and executes a specific tool
    identified by 'tool_name'.
    """
    async def mcp_tool_executor(**kwargs):
        # kwargs is expected to contain 'tool_name' and 'args' for that tool
        # e.g., tool_name="repos_clone_repository", args={"owner": "...", "repo": "..."}

        tool_to_execute_name = kwargs.get("tool_name")
        # Default tool_arguments to an empty dictionary if 'args' key is missing or None.
        # This allows the call to proceed to the MCP tool, which can then validate
        # if an empty args dict is acceptable or if specific arguments are missing.
        tool_arguments = kwargs.get("args", {})

        if not tool_to_execute_name:
            return "Error: 'tool_name' not provided to MCP tool executor."
        # The explicit check for `tool_arguments is None` is less critical now,
        # as it defaults to {}. If the LLM explicitly passes args=None,
        # tool_arguments would become None, and the original check might be useful.
        # However, with the default to {}, this path is less likely.

        # Connect to MCP server
        mcp_tools = []
        exit_stack = None
        try:
            mcp_tools, exit_stack = await MCPToolset.from_server(
                connection_params=StdioServerParameters(
                    command=command,
                    args=args or [],
                    env=env or {},
                ),
            )
            
            selected_tool = next((t for t in mcp_tools if t.name == tool_to_execute_name), None)
            
            if not selected_tool:
                available_tool_names = [t.name for t in mcp_tools]
                return f"Error: Tool '{tool_to_execute_name}' not found in MCP server. Available tools: {available_tool_names}"

            # Execute the selected tool with its specific arguments
            success, result, error_msg = await execute_tool(selected_tool, tool_arguments)
            if success:
                return result
            else:
                return f"Tool '{selected_tool.name}' failed: {error_msg}"
        except Exception as e:
            # Catch exceptions during connection, tool finding, or execution if not caught by execute_tool
            return f"Error in MCP tool executor: {str(e)}"
        finally:
            if exit_stack:
                await exit_stack.aclose()
    
    return mcp_tool_executor


# Create our GitHub MCP tool executor
github_mcp_tools = create_mcp_tool_executor(
    command=github_mcp_server_command,
    args=["stdio"],
    env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_PERSONAL_ACCESS_TOKEN,
        "GITHUB_TOOLSETS": "repos,issues,pull_requests,code_security"  # Specify desired toolsets
    }
)

# Determine the root directory of the 'secpatch' project dynamically.
# Assumes mcp_tool.py is at <project_root_dir>/secpatch_package/tools/mcp_tool.py
# To get to <project_root_dir> (e.g., /Users/catbalajadia/Downloads/google_hack/secpatch),
# we go up two levels from the directory of mcp_tool.py.
_current_file_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.abspath(os.path.join(_current_file_dir, "..", ".."))

# MCP_TEMP_DIR is the directory that the file system MCP server will be rooted in.
# This is where temporary project clones and files will be handled by file_mcp_tools.
MCP_TEMP_DIR = os.path.join(PROJECT_ROOT_DIR, "temp")

# Ensure this temp directory exists
os.makedirs(MCP_TEMP_DIR, exist_ok=True)

# Create our file system MCP tool executor
file_mcp_tools = create_mcp_tool_executor(
    command='npx',
    args=[
        '-y',  # Arguments for the command
        '@modelcontextprotocol/server-filesystem',
        MCP_TEMP_DIR, # This path is now dynamically determined and absolute
    ],
)

__all__ = ["github_mcp_tools", "file_mcp_tools"]
