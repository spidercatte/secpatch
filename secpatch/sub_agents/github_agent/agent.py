import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# --- Configuration ---
# Your GitHub Personal Access Token
GITHUB_PERSONAL_ACCESS_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
if not GITHUB_PERSONAL_ACCESS_TOKEN:
    raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN environment variable not set for GitHub MCP server.")

# --- Define the Agent with GitHub MCP Toolset ---
# You would typically create this within an async function if managing the MCP server
# process directly, as shown in my previous detailed examples.
# This example is for direct instantiation for clarity, assuming context handling elsewhere.

github_assistant_agent = LlmAgent(
    model="gemini-2.0-flash",
    name='github_assistant_agent',
    instruction=(
        'You are a helpful assistant that can interact with GitHub. '
        'Use the available tools to list repositories, create issues, '
        'manage pull requests, and perform other GitHub-related tasks. '
        'Always ask for necessary details before attempting an action, '
        'e.g., repository owner, repo name, title, body for an issue.'
    ),
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='github-mcp-server', # This is the command to launch the GitHub MCP server
                args=[
                    "stdio" # The GitHub MCP server communicates via stdio
                ],
                env={ # These environment variables are passed to the 'github-mcp-server' process
                    "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_PERSONAL_ACCESS_TOKEN,
                    "GITHUB_TOOLSETS": "repos,issues,pull_requests,code_security" # Specify desired toolsets
                }
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # For example, if you only want to list repos and create issues:
            # tool_filter=['github.repos.list', 'github.issues.create']
        )
    ],
)

# --- How you'd typically use it (within an async context) ---
async def run_github_agent():
    # When you create MCPToolset directly like this, the MCP server process
    # is launched and managed by the ADK framework.
    # The cleanup of this process happens when the agent or its associated tools
    # are garbage collected, or more explicitly, when the program exits.
    # For robust handling, especially if your agent runs for a long time,
    # the AsyncExitStack pattern (as shown in my previous answers) is preferred
    # to ensure the MCP server subprocess is explicitly terminated.

    print("GitHub Assistant Agent is ready!")
    print("Try asking: 'List my repositories.'")
    print("Or: 'Create an issue in octocat/hello-world with title \"Bug found\" and body \"Description of bug.\"'")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        response = await github_assistant_agent.process(user_input)
        print(f"Assistant: {response.text}")

if __name__ == '__main__':
    # Ensure your environment variables are set before running
    # export GITHUB_PERSONAL_ACCESS_TOKEN="YOUR_GITHUB_TOKEN"

    asyncio.run(run_github_agent())  