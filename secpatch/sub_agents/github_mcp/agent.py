# secpatch/sub_agents/github_mcp/agent.py

from google.adk import Agent

from secpatch.sub_agents.github_mcp.prompt import GITHUB_MCP_PROMPT
from secpatch.tools import git_tool
from secpatch.tools import github_interaction_tools
from secpatch.tools import utility_tools

# Define the model for the agent
MODEL = "gemini-1.5-pro-latest" # Using a powerful model capable of instruction following

# Instantiate the specific utility tools needed by this agent
# We selected these based on the plan: read, write, list, package manager, run tests
mcp_utility_tools = [
    utility_tools.read_file_tool_instance,
    utility_tools.write_file_tool_instance,
    utility_tools.list_directory_tool_instance,
    utility_tools.package_manager_install_tool_instance,
    utility_tools.run_tests_tool_instance,
]

# Create the github_mcp_agent instance
github_mcp_agent = Agent(
    model=MODEL,
    name="github_mcp_agent",
    instruction=GITHUB_MCP_PROMPT,
    output_key="github_mcp_output", # Define an output key for this agent
    tools=[
        *git_tool.git_tools,
        *github_interaction_tools.github_interaction_tools,
        *mcp_utility_tools,
    ],
)

# Potentially, you might want to export the agent instance or a list of agents if needed elsewhere.
# For now, direct import of 'github_mcp_agent' from this module will work.
