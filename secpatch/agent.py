"""SecPatch: Auto fix vulnerabilities."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from secpatch import prompt
from secpatch.sub_agents.vuln_websearch.agent import vuln_websearch_agent
from secpatch.sub_agents.vuln_fix.agent import vuln_fix_agent
#from secpatch.sub_agents.vuln_dbsearch.agent import database_agent # Import the database_agent
from secpatch.tools.mcp_tool import toolbox_tools # Import the MCP toolsets



MODEL = "gemini-2.0-flash" # Or latest available Flash modeli

vuln_fix_coordinator = LlmAgent(
    name="vuln_fix_coordinator",
    model=MODEL,
    description=(
        "Orchestrates the end-to-end process of fixing CVEs in projects. "
        "This involves analyzing vulnerability information, assessing fix recommendations, "
        "and coordinating sub-agents to search for CVE details, apply code fixes (including dependency upgrades, "
        "testing, and Git operations), manage fix attempts, and handle Pull Request creation or issue reporting."
    ),
    instruction=prompt.VULN_FIX_COORDINATOR_PROMPT,
    output_key="fix_coordination_result", # Renamed for clarity
    tools=[
        *toolbox_tools, # Add the Toolbox tools for database operations.
        #AgentTool(agent=database_agent), # This agent is responsible for querying vulnerability info from a database
        AgentTool(agent=vuln_websearch_agent), # This agent is responsible for searching CVE information and code locations
        AgentTool(agent=vuln_fix_agent), # This agent is responsible for applying the fixes,
    ],
)

root_agent = vuln_fix_coordinator

if __name__ == "__main__":

    print("Initializing the CVE Fix Coordination process...")

    # Input for the coordinator
    initial_cve_input = {
        "cve_id": "CVE-2022-24999", # The CVE ID we found for qs library
        "repository_url": "https://github.com/spidercatte/vulnerable-node-app"
    }

    print(f"Attempting to fix CVE: {initial_cve_input['cve_id']} in {initial_cve_input['repository_url']}")

    async def main():
        # Assuming vuln_fix_coordinator.process is an async method
        coordination_result = await vuln_fix_coordinator.process(initial_cve_input)
        print("\n--- CVE Fix Coordination Result ---")
        print(coordination_result.output["fix_coordination_result"]) # Access the output using the output_key
        print("-----------------------------------")

    asyncio.run(main())
