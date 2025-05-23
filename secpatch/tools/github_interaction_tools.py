# github_interaction_tools.py
import subprocess
import os
from typing import Dict, Any, Optional
from google.adk.tools import FunctionTool


def _run_gh_command(command: list[str], cwd: str = None) -> Dict[str, Any]:
    """Helper function to run a 'gh' CLI command and capture output."""
    # Ensure 'gh' CLI is installed and authenticated if targeting real GitHub
    # Authentication usually happens via 'gh auth login' or GH_TOKEN env var
    env = os.environ.copy()
    # Example: If you need to explicitly pass a token (less secure than gh auth login)
    # env['GH_TOKEN'] = os.getenv('GITHUB_PAT') # Make sure GITHUB_PAT is set in env

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
            env=env
        )
        return {"success": True, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except subprocess.CalledProcessError as e:
        return {"success": False, "stdout": e.stdout.strip(), "stderr": e.stderr.strip(), "error": str(e)}
    except FileNotFoundError:
        return {"success": False, "error": "GitHub CLI ('gh') command not found. Is it installed and in your PATH?"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}


def create_pull_request(
    repo_url: str,
    head_branch: str,
    base_branch: str = "main",
    title: str = "Automated Fix PR",
    body: str = "Automated vulnerability fix by agent.",
    repo_path: Optional[str] = None # Add repo_path if the gh cli needs to be run from inside the repo
) -> Dict[str, Any]:
    """
    Creates a pull request on GitHub for a given repository.
    Requires 'gh' CLI to be installed and authenticated.

    Args:
        repo_url: The URL of the GitHub repository (e.g., "https://github.com/owner/repo").
                  The 'gh' CLI often infers this from the current directory if run inside a repo.
        head_branch: The branch containing the changes to be merged (e.g., "fix-CVE-2023-12345").
        base_branch: The target branch to merge into (e.g., "main", "develop"). Defaults to "main".
        title: The title of the pull request.
        body: The body content of the pull request.
        repo_path: The local path to the repository. 'gh' CLI will be run from here.

    Returns:
        A dictionary indicating success, stdout (likely PR URL), and stderr.
    """
    # The 'gh pr create' command expects to be run within the repository directory
    # or takes a --repo flag. Assuming repo_path is provided.
    command = [
        "gh", "pr", "create",
        "--title", title,
        "--body", body,
        "--head", head_branch,
        "--base", base_branch,
        "--repo", repo_url # Explicitly specify repo for robustness
    ]
    return _run_gh_command(command, cwd=repo_path)


def create_github_issue(
    repo_url: str,
    title: str,
    body: str,
    repo_path: Optional[str] = None # Add repo_path if the gh cli needs to be run from inside the repo
) -> Dict[str, Any]:
    """
    Creates a GitHub issue in the specified repository.
    Requires 'gh' CLI to be installed and authenticated.

    Args:
        repo_url: The URL of the GitHub repository (e.g., "https://github.com/owner/repo").
        title: The title of the issue.
        body: The body content of the issue.
        repo_path: The local path to the repository. 'gh' CLI will be run from here.

    Returns:
        A dictionary indicating success, stdout (likely Issue URL), and stderr.
    """
    command = [
        "gh", "issue", "create",
        "--title", title,
        "--body", body,
        "--repo", repo_url # Explicitly specify repo for robustness
    ]
    return _run_gh_command(command, cwd=repo_path)


# Instantiate the FunctionTools for your agent
create_pull_request_tool_instance = FunctionTool(create_pull_request)
create_github_issue_tool_instance = FunctionTool(create_github_issue)

# You can create a list of all GitHub interaction tools for easy import
github_interaction_tools = [
    create_pull_request_tool_instance,
    create_github_issue_tool_instance,
]