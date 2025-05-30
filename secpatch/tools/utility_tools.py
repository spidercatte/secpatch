# utility_tools.py
import os
import subprocess
from typing import Dict, Any, List, Optional
from google.adk.tools import FunctionTool
from google.adk.tools import ToolContext


# --- Package Manager Tool ---
def package_manager_install_tool(project_path: str, affected_library_package: str, suggested_fix_version: str, tool_context: ToolContext):
    vuln_websearch_output = tool_context.state.get("vuln_websearch_output")

    if not vuln_websearch_output:
        return {"success": False, "error": "No 'vuln_websearch_output' found in tool_context state."}

    project_path = vuln_websearch_output.get("project_path")
    affected_library_package = vuln_websearch_output.get("affected_library_package")
    suggested_fix_version = vuln_websearch_output.get("suggested_fix_version")

    if not project_path:
        return {"success": False, "error": "No project path specified in vuln_websearch_output."}
    if not affected_library_package:
        return {"success": False, "error": "No affected library package specified."}

    return package_manager_install(project_path, affected_library_package, suggested_fix_version)


def package_manager_install(project_path: str, affected_library_package: str, suggested_fix_version: str = None) -> Dict[str, Any]:
    """
    Attempts to install or upgrade a package using common package managers
    (pip for Python, npm for Node.js).
    It tries to detect the project type based on common files.

    Args:
        project_path: The path to the project root directory.
        affected_library_package: The name of the package to install/upgrade.
        suggested_fix_version: Optional. The specific version to install (e.g., "1.2.3").
                 If None, it tries to install the latest compatible version.

    Returns:
        A dictionary with 'success', 'stdout', 'stderr', and 'error' keys.
    """
    command = []
    env = os.environ.copy() # Important to copy current environment for subprocess

    # Detect project type
    if os.path.exists(os.path.join(project_path, 'requirements.txt')) or \
       os.path.exists(os.path.join(project_path, 'pyproject.toml')):
        # Assume Python project
        cmd_base = "pip"
        if os.path.exists(os.path.join(project_path, 'venv')): # Use venv pip if it exists
            cmd_base = os.path.join(project_path, 'venv', 'bin', 'pip')
        elif os.path.exists(os.path.join(project_path, '.venv')):
             cmd_base = os.path.join(project_path, '.venv', 'bin', 'pip')

        command = [cmd_base, "install", affected_library_package]
        if suggested_fix_version:
            command[2] += f"=={suggested_fix_version}"
        else: # Attempt upgrade to latest if no specific version
            command.append("--upgrade")
    elif os.path.exists(os.path.join(project_path, 'package.json')):
        # Assume Node.js project
        command = ["npm", "install", affected_library_package]
        if suggested_fix_version:
            command[2] += f"@{suggested_fix_version}"
        # npm install <package> or npm update <package>
        # For simplicity, we'll just run install. `npm install` with version handles upgrade.
    elif os.path.exists(os.path.join(project_path, 'pom.xml')):
        # Assume Maven project (dependency updates are more complex, often via plugins)
        # This is a very basic attempt. Real Maven update is usually via `versions:use-latest-releases` or similar.
        print("Warning: Maven dependency update via direct command is complex. Consider using Maven plugins.")
        return {"success": False, "error": "Maven dependency updates require specific plugin goals, not direct package install command via this tool."}
    elif os.path.exists(os.path.join(project_path, 'build.gradle')):
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
            cwd=project_path,
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
def run_tests_tool(project_path: str , tool_context: ToolContext):
    """
    Tool to run tests for the project using common test runners
    (pytest for Python, npm test for Node.js).
    It tries to detect the project type based on common files.
    """

    vuln_websearch_output = tool_context.state.get("vuln_websearch_output")

    if not vuln_websearch_output:
        return {"success": False, "error": "No 'vuln_websearch_output' found in tool_context state."}

    project_path = vuln_websearch_output.get("project_path")
    if not project_path:
        return {"success": False, "error": "No project path specified in vuln_websearch_output."}

    return run_tests(project_path)


def run_tests(project_path: str = ".") -> Dict[str, Any]:
    """
    Attempts to run tests for the project using common test runners
    (pytest for Python, npm test for Node.js).
    It tries to detect the project type based on common files within the project_path.

    Args:
        repo_path: The path to the project root directory. Defaults to current directory.

    Returns:
        A dictionary with 'success', 'stdout', 'stderr', and 'error' keys.
    """
    command = []
    env = os.environ.copy() # Important to copy current environment for subprocess

    # Detect project type
    if os.path.exists(os.path.join(project_path, 'pytest.ini')) or \
       os.path.exists(os.path.join(project_path, 'conftest.py')) or \
       os.path.exists(os.path.join(project_path, 'tests')):
        # Assume Python project with pytest
        cmd_base = "pytest"
        if os.path.exists(os.path.join(project_path, 'venv')): # Use venv pytest if it exists
            cmd_base = os.path.join(project_path, 'venv', 'bin', 'pytest')
        elif os.path.exists(os.path.join(project_path, '.venv')):
            cmd_base = os.path.join(project_path, '.venv', 'bin', 'pytest')

        command = [cmd_base]
    elif os.path.exists(os.path.join(project_path, 'package.json')):
        # Assume Node.js project with 'test' script
        # Check if 'test' script exists in package.json
        try:
            import json
            with open(os.path.join(project_path, 'package.json'), 'r', encoding='utf-8') as f:
                package_json = json.load(f)
                if "scripts" in package_json and "test" in package_json["scripts"]:
                    command = ["npm", "test"]
                else:
                    return {"success": False, "error": "Node.js project found, but no 'test' script in package.json."}
        except json.JSONDecodeError:
            return {"success": False, "error": f"Invalid package.json in {project_path}"}
        except Exception as e:
            return {"success": False, "error": f"Error parsing package.json: {e}"}
    elif os.path.exists(os.path.join(project_path, 'pom.xml')):
        # Assume Maven project
        command = ["mvn", "test"]
    elif os.path.exists(os.path.join(project_path, 'build.gradle')):
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
            cwd=project_path,
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
package_manager_install_tool_instance = FunctionTool(
    func=package_manager_install_tool,
)

run_tests_tool_instance = FunctionTool(
    func=run_tests_tool,
)

# Aggregate them into a list for easy import
utility_tools = [
    package_manager_install_tool_instance,
    run_tests_tool_instance,
]