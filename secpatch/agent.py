"""SecPatch: Auto fix vulnerabilities."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from secpatch import prompt
from secpatch.sub_agents.vuln_websearch.agent import vuln_websearch_agent
from secpatch.sub_agents.vuln_fix.agent import vuln_fix_agent
from secpatch.tools import github_interaction_tools


MODEL = "gemini-2.5-pro-preview-05-06"


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
        AgentTool(agent=vuln_websearch_agent), # This agent is responsible for searching CVE information and code locations
        AgentTool(agent=vuln_fix_agent), # This agent is responsible for applying the fixes
        *github_interaction_tools.github_interaction_tools, # Unpacks all tools from github_interaction_tools.py (create_pull_request, create_github_issue),
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



    print("\n--- CVE Fix Coordination Result ---")
    #print(coordination_result)
    print("-----------------------------------")
