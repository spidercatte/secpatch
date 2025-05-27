
"""Vuln_fix_agent for fixing vulnerability ."""

from google.adk import Agent
from google.adk.tools import google_search

from secpatch.sub_agents.vuln_fix import prompt
from secpatch.sub_agents.github_mcp.agent import github_mcp_agent
from secpatch.tools import git_tool # Import your custom git_tool.py
from secpatch.tools import utility_tools



MODEL = "gemini-2.5-pro-preview-05-06"


print(f"Type of git_tool.git_tools: {type(git_tool.git_tools)}")
print(f"Type of utility_tools.utility_tools: {type(utility_tools.utility_tools)}")
print(f"Type of google_search: {type(google_search)}")
print(f"Type of prompt.VULN_FIX_PROMPT: {type(prompt.VULN_FIX_PROMPT)}")

vuln_fix_agent = Agent(
    model=MODEL,
    name="vuln_fix_agent",
    instruction=prompt.VULN_FIX_PROMPT,
    output_key="vuln_fix_output",
    tools=[
        google_search, # Still useful for very specific code searches within the fix agent
        *git_tool.git_tools, # Unpack all the git tools
        *utility_tools.utility_tools, # Unpack all the file tools
        github_mcp_agent,
    ],
)