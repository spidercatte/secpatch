
"""Vuln_websearch_agent for finding CVEs using search tools."""

from google.adk import Agent
from google.adk.tools import google_search

from secpatch.sub_agents.vuln_websearch import prompt
from secpatch.tools import types

MODEL = "gemini-2.0-flash"


vuln_websearch_agent = Agent(
    model=MODEL,
    name="vuln_websearch_agent",
    instruction=prompt.VULN_WEBSEARCH_PROMPT,
    output_key="vuln_websearch_output",
    tools=[google_search],
)
