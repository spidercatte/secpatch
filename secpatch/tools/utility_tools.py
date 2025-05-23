# utility_tools.py
import os
import subprocess
from typing import Dict, Any, List
from google.adk.tools import FunctionTool

# --- File System Tools ---

def read_file(file_path: str) -> Dict[str, Any]:
    """
    Reads the content of a specified file.

    Args:
        file_path: The full path to the file to read.

    Returns:
        A dictionary with 'success', 'content', and 'error' keys.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "content": content, "error": None}
    except FileNotFoundError:
        return {"success": False, "content": None, "error": f"File not found: {file_path}"}
    except Exception as e:
        return {"success": False, "content": None, "error": f"Error reading file {file_path}: {e}"}

def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Writes content to a specified file, overwriting existing content.
    Creates the file if it doesn't exist, and creates parent directories if necessary.

    Args:
        file_path: The full path to the file to write to.
        content: The string content to write to the file.

    Returns:
        A dictionary with 'success', 'message', and 'error' keys.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"Successfully wrote to {file_path}", "error": None}
    except Exception as e:
        return {"success": False, "message": None, "error": f"Error writing to file {file_path}: {e}"}

def list_directory(path: str = ".") -> Dict[str, Any]:
    """
    Lists the contents (files and directories) of a specified path.

    Args:
        path: The path to the directory to list. Defaults to the current working directory.

    Returns:
        A dictionary with 'success', 'contents' (list of strings), and 'error' keys.
    """
    try:
        contents = os.listdir(path)
        return {"success": True, "contents": contents, "error": None}
    except FileNotFoundError:
        return {"success": False, "contents": None, "error": f"Directory not found: {path}"}
    except Exception as e:
        return {"success": False, "contents": None, "error": f"Error listing directory {path}: {e}"}

# --- Package Manager Tool ---

def package_manager_install(repo_path: str, package_name: str, version: str = None) -> Dict[str, Any]:
    """
    Attempts to install or upgrade a package using common package managers
    (pip for Python, npm for Node.js).
    It tries to detect the project type based on common files.

    Args:
        repo_path: The path to the project root directory.
        package_name: The name of the package to install/upgrade.
        version: Optional. The specific version to install (e.g., "1.2.3").
                 If None, it tries to install the latest compatible version.

    Returns:
        A dictionary with 'success', 'stdout', 'stderr', and 'error' keys.
    """
    command = []
    env = os.environ.copy() # Important to copy current environment for subprocess

    # Detect project type
    if os.path.exists(os.path.join(repo_path, 'requirements.txt')) or \
       os.path.exists(os.path.join(repo_path, 'pyproject.toml')):
        # Assume Python project
        cmd_base = "pip"
        if os.path.exists(os.path.join(repo_path, 'venv')): # Use venv pip if it exists
            cmd_base = os.path.join(repo_path, 'venv', 'bin', 'pip')
        elif os.path.exists(os.path.join(repo_path, '.venv')):
             cmd_base = os.path.join(repo_path, '.venv', 'bin', 'pip')

        command = [cmd_base, "install", package_name]
        if version:
            command[2] += f"=={version}"
        else: # Attempt upgrade to latest if no specific version
            command.append("--upgrade")
    elif os.path.exists(os.path.join(repo_path, 'package.json')):
        # Assume Node.js project
        command = ["npm", "install", package_name]
        if version:
            command[2] += f"@{version}"
        # npm install <package> or npm update <package>
        # For simplicity, we'll just run install. `npm install` with version handles upgrade.
    elif os.path.exists(os.path.join(repo_path, 'pom.xml')):
        # Assume Maven project (dependency updates are more complex, often via plugins)
        # This is a very basic attempt. Real Maven update is usually via `versions:use-latest-releases` or similar.
        print("Warning: Maven dependency update via direct command is complex. Consider using Maven plugins.")
        return {"success": False, "error": "Maven dependency updates require specific plugin goals, not direct package install command via this tool."}
    elif os.path.exists(os.path.join(repo_path, 'build.gradle')):
        # Assume Gradle project
        # Similar to Maven, direct command-line updates are not standard.
        print("Warning: Gradle dependency update via direct command is complex. Consider using Gradle plugins.")
        return {"success": False, "error": "Gradle dependency updates typically require build.gradle modifications or specific tasks."}
    else:
        return {"success": False, "error": "Could not determine project type (Python/Node.js) for package manager."}

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_path,
            env=env # Pass the environment to subprocess
        )
        return {"success": True, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except subprocess.CalledProcessError as e:
        return {"success": False, "stdout": e.stdout.strip(), "stderr": e.stderr.strip(), "error": str(e)}
    except FileNotFoundError:
        return {"success": False, "error": f"Package manager command not found: {command[0]}. Is it installed and in your PATH?"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred during package install: {str(e)}"}


# --- Test Runner Tool ---

def run_tests(repo_path: str = ".") -> Dict[str, Any]:
    """
    Attempts to run tests for the project using common test runners
    (pytest for Python, npm test for Node.js).
    It tries to detect the project type based on common files.

    Args:
        repo_path: The path to the project root directory. Defaults to current directory.

    Returns:
        A dictionary with 'success', 'stdout', 'stderr', and 'error' keys.
    """
    command = []
    env = os.environ.copy() # Important to copy current environment for subprocess

    # Detect project type
    if os.path.exists(os.path.join(repo_path, 'pytest.ini')) or \
       os.path.exists(os.path.join(repo_path, 'conftest.py')) or \
       os.path.exists(os.path.join(repo_path, 'tests')):
        # Assume Python project with pytest
        cmd_base = "pytest"
        if os.path.exists(os.path.join(repo_path, 'venv')): # Use venv pytest if it exists
            cmd_base = os.path.join(repo_path, 'venv', 'bin', 'pytest')
        elif os.path.exists(os.path.join(repo_path, '.venv')):
            cmd_base = os.path.join(repo_path, '.venv', 'bin', 'pytest')

        command = [cmd_base]
    elif os.path.exists(os.path.join(repo_path, 'package.json')):
        # Assume Node.js project with 'test' script
        # Check if 'test' script exists in package.json
        try:
            import json
            with open(os.path.join(repo_path, 'package.json'), 'r', encoding='utf-8') as f:
                package_json = json.load(f)
                if "scripts" in package_json and "test" in package_json["scripts"]:
                    command = ["npm", "test"]
                else:
                    return {"success": False, "error": "Node.js project found, but no 'test' script in package.json."}
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid package.json in {repo_path}"}
        except Exception as e:
            return {"success": False, "error": f"Error parsing package.json: {e}"}
    elif os.path.exists(os.path.join(repo_path, 'pom.xml')):
        # Assume Maven project
        command = ["mvn", "test"]
    elif os.path.exists(os.path.join(repo_path, 'build.gradle')):
        # Assume Gradle project
        command = ["gradle", "test"]
    else:
        return {"success": False, "error": "Could not determine project type for running tests."}

    if not command:
        return {"success": False, "error": "No suitable test command determined for this project."}

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False, # Do not check=True here, as tests failing should not raise an exception
            cwd=repo_path,
            env=env
        )
        if result.returncode != 0:
            return {"success": False, "stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "error": f"Tests failed with exit code {result.returncode}"}
        else:
            return {"success": True, "stdout": result.stdout.strip(), "stderr": result.stderr.strip(), "error": None}
    except FileNotFoundError:
        return {"success": False, "error": f"Test runner command not found: {command[0]}. Is it installed and in your PATH?"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred during test run: {str(e)}"}


# Instantiate the FunctionTools
read_file_tool_instance = FunctionTool(read_file)
write_file_tool_instance = FunctionTool(write_file)
list_directory_tool_instance = FunctionTool(list_directory)
package_manager_install_tool_instance = FunctionTool(package_manager_install)
run_tests_tool_instance = FunctionTool(run_tests)

# Aggregate them into a list for easy import
utility_tools = [
    read_file_tool_instance,
    write_file_tool_instance,
    list_directory_tool_instance,
    package_manager_install_tool_instance,
    run_tests_tool_instance,
]