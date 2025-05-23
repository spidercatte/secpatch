# git_tool.py
import subprocess
from typing import Dict, Any
from google.adk.tools import FunctionTool


def _run_git_command(command: list[str], cwd: str = None) -> Dict[str, Any]:
    """Helper function to run a git command and capture output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return {"success": True, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except subprocess.CalledProcessError as e:
        return {"success": False, "stdout": e.stdout.strip(), "stderr": e.stderr.strip(), "error": str(e)}
    except FileNotFoundError:
        return {"success": False, "error": "Git command not found. Is Git installed and in your PATH?"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

def git_clone(repo_url: str, directory: str = None) -> Dict[str, Any]:
    """
    Clones a Git repository from the given URL into the specified directory.

    Args:
        repo_url: The URL of the Git repository to clone.
        directory: Optional. The directory to clone the repository into. If None,
                   it will clone into a directory named after the repository.
    Returns:
        A dictionary indicating success, stdout, and stderr.
    """
    command = ["git", "clone", repo_url]
    if directory:
        command.append(directory)
    return _run_git_command(command)

def git_pull(repo_path: str = ".") -> Dict[str, Any]:
    """
    Pulls changes from the remote repository into the current branch.

    Args:
        repo_path: The path to the local Git repository. Defaults to the current directory.
    Returns:
        A dictionary indicating success, stdout, and stderr.
    """
    command = ["git", "pull"]
    return _run_git_command(command, cwd=repo_path)

def git_add(repo_path: str = ".", files: str = ".") -> Dict[str, Any]:
    """
    Adds specified files to the Git staging area.

    Args:
        repo_path: The path to the local Git repository. Defaults to the current directory.
        files: A space-separated string of files or directories to add. Use "." for all changes.
    Returns:
        A dictionary indicating success, stdout, and stderr.
    """
    command = ["git", "add"] + files.split()
    return _run_git_command(command, cwd=repo_path)

def git_commit(repo_path: str = ".", message: str = "Automated commit by agent") -> Dict[str, Any]:
    """
    Commits staged changes with a given commit message.

    Args:
        repo_path: The path to the local Git repository. Defaults to the current directory.
        message: The commit message.
    Returns:
        A dictionary indicating success, stdout, and stderr.
    """
    command = ["git", "commit", "-m", message]
    return _run_git_command(command, cwd=repo_path)

def git_push(repo_path: str = ".") -> Dict[str, Any]:
    """
    Pushes committed changes to the remote repository.

    Args:
        repo_path: The path to the local Git repository. Defaults to the current directory.
    Returns:
        A dictionary indicating success, stdout, and stderr.
    """
    command = ["git", "push"]
    return _run_git_command(command, cwd=repo_path)

def git_checkout(repo_path: str = ".", branch_name: str = "main", create_new: bool = False) -> Dict[str, Any]:
    """
    Switches to a specified branch or creates a new one.

    Args:
        repo_path: The path to the local Git repository. Defaults to the current directory.
        branch_name: The name of the branch to checkout.
        create_new: If True, creates a new branch with the given name and switches to it.
    Returns:
        A dictionary indicating success, stdout, and stderr.
    """
    command = ["git", "checkout"]
    if create_new:
        command.append("-b")
    command.append(branch_name)
    return _run_git_command(command, cwd=repo_path)

def git_status(repo_path: str = ".") -> Dict[str, Any]:
    """
    Shows the working tree status.

    Args:
        repo_path: The path to the local Git repository. Defaults to the current directory.
    Returns:
        A dictionary indicating success, stdout, and stderr.
    """
    command = ["git", "status"]
    return _run_git_command(command, cwd=repo_path)




# Instantiate the FunctionTools for your agent
git_clone_tool = FunctionTool(git_clone)
git_pull_tool = FunctionTool(git_pull)
git_add_tool = FunctionTool(git_add)
git_commit_tool = FunctionTool(git_commit)
git_push_tool = FunctionTool(git_push)
git_checkout_tool = FunctionTool(git_checkout)
git_status_tool = FunctionTool(git_status)

# You can create a list of all Git tools to pass to your agent
git_tools = [
    git_clone_tool,
    git_pull_tool,
    git_add_tool,
    git_commit_tool,
    git_push_tool,
    git_checkout_tool,
    git_status_tool,
]