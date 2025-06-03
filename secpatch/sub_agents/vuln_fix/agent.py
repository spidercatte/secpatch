"""Vuln_fix_agent for fixing vulnerability ."""

from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters # Import MCPToolset
import os # For GITHUB_PERSONAL_ACCESS_TOKEN

from secpatch.sub_agents.vuln_fix import prompt
from secpatch.tools.utility_tools import package_manager_install_tool_instance, run_tests_tool_instance, clear_temp_directory_tool_instance
from secpatch.tools.mcp_tool import github_mcp_tools, file_mcp_tools
from secpatch.tools.git_tool import git_tools  # Import your custom git_tool.py
from secpatch.tools import types


#MODEL = "gemini-2.5-pro-preview-05-06"
MODEL ="gemini-2.0-flash"
#MODEL = "gemini-1.5-flash-preview-0514" # Or latest available Flash model

vuln_fix_agent = Agent(
    model=MODEL,
    name="vuln_fix_agent",
    instruction=prompt.VULN_FIX_PROMPT,
    output_key="vuln_fix_output",
    #output_schema=types.Itinerary,
    #generate_content_config=types.json_response_config,
    tools=[
        github_mcp_tools, # Add the GitHub MCP toolset
        file_mcp_tools, # Add the file system MCP toolset
        *git_tools, # Add the git toolset
        package_manager_install_tool_instance, # Add package manager install tool
        run_tests_tool_instance, # Add test runner tool
        clear_temp_directory_tool_instance, # Add tool to clear temp directory
    ],
)