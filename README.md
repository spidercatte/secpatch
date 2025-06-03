# SecPatch

## Overview

<!-- TODO: Refine this overview to accurately describe SecPatch's mission and value proposition. -->
SecPatch is an AI-driven agent designed to streamline and enhance the security patching lifecycle for software systems. It addresses the critical challenge of timely and effective vulnerability remediation by automating and assisting in the identification of vulnerabilities, discovery of relevant patches, analysis of patch impacts, and guidance through the deployment process.

Key capabilities include:

1.  **Vulnerability Identification:** Ingests data from various sources (e.g., CVE databases, security advisories, vulnerability scan reports) to pinpoint security weaknesses in target systems or software.
2.  **Patch Discovery and Assessment:** Leverages specialized tools and knowledge bases to find appropriate security patches for identified vulnerabilities, assessing their relevance and potential side effects.
3.  **Impact Analysis:** Analyzes the potential impact of applying a patch, considering factors like system stability, dependencies, and operational risk.
4.  **Deployment Guidance:** Offers recommendations and can assist in orchestrating the patch deployment process, potentially integrating with existing patch management infrastructure.

SecPatch aims to provide security teams and system administrators with actionable intelligence and automation to reduce their systems' exposure to threats, improve their security posture, and manage the patching process more efficiently.

## Agent Details

The key features of SecPatch include:

| Feature | Description |
| --- | --- |
| **Interaction Type** | Conversational |
| **Complexity**  | Medium <!-- TODO: Adjust if SecPatch is simpler or more complex --> |
| **Agent Type**  | Multi Agent |
| **Components**  | Tools: Vulnerability Databases (e.g., NVD), Patch Information Systems, Code Analysis (optional), Configuration Management (optional) <!-- TODO: List actual components/tools used --> |
| **Vertical**  | Cybersecurity / Software Security |


### Agent architecture:

This diagram shows the detailed architecture of the agents and tools used
to implement this workflow.
<!-- TODO: Replace with actual SecPatch architecture diagram and update path if necessary -->
<img src="secpatch-architecture.png" alt="SecPatch Agent Architecture" width="800"/>

## Setup and Installation

1.  **Prerequisites**

    *   Python 3.11+
    *   Poetry
        *   For dependency management and packaging. Please follow the
            instructions on the official
            [Poetry website](https://python-poetry.org/docs/) for installation.

        ```bash
        pip install poetry
        ```

    * A project on Google Cloud Platform
    * Google Cloud CLI
        *   For installation, please follow the instruction on the official
            [Google Cloud website](https://cloud.google.com/sdk/docs/install).

2.  **Installation**

    ```bash
    # Clone this repository.
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/academic-research
    # Install the package and dependencies.
    poetry install
    ```

3.  **Configuration**

    *   Set up Google Cloud credentials.

        *   You may set the following environment variables in your shell, or in
            a `.env` file instead.

        ```bash
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT=<your-project-id>
        export GOOGLE_CLOUD_LOCATION=<your-project-location>
        export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>  # Only required for deployment on Agent Engine
        ```

    *   Authenticate your GCloud account.

        ```bash
        gcloud auth application-default login
        gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
        ```

## Running the Agent

**Using `adk`**

ADK provides convenient ways to bring up agents locally and interact with them.
You may talk to the agent using the CLI:

```bash
adk run secpatch
```

Or on a web interface:

```bash
 adk web
```

The command `adk web` will start a web server on your machine and print the URL.
You may open the URL, select "secpatch" as the agent, and start a conversation" in the top-left drop-down menu, and
a chatbot interface will appear on the right. The conversation is initially
blank. Here are some example json cve issue as an input to agent:


```
{
        "cve_id": "CVE-2022-24999", # The CVE ID we found for qs library
        "repository_url": "https://github.com/spidercatte/vulnerable-node-app"
    }
```

Sampled responses of these requrests are shown below in the [Example
Interaction](#example-interaction) section.

```
Okay, I will start by gathering information about the CVE using the Vulnerability Web Search agent.

```

### Example Interaction

Below is an example interaction with the Academic Research. Note that the exact output
of the agent may be different every time. Not that the user provides a pdf with the seminal paper to analyze

TBD

```


```

## Running Tests

For running tests and evaluation, install the extra dependencies:

```bash
poetry install --with dev
```

Then the tests and evaluation can be run from the `secpatch` directory using
the `pytest` module:

```bash
python3 -m pytest tests
python3 -m pytest eval
```

`tests` runs the agent on a sample request, and makes sure that every component
is functional. `eval` is a demonstration of how to evaluate the agent, using the
`AgentEvaluator` in ADK. It sends a couple requests to the agent and expects
that the agent's responses match a pre-defined response reasonablly well.


## Deployment

The SecPatch agent can be deployed to Vertex AI Agent Engine using the following
commands:

```bash
poetry install --with deployment
python3 deployment/deploy.py --create
```

When the deployment finishes, it will print a line like this:

```
Created remote agent: projects/<PROJECT_NUMBER>/locations/<PROJECT_LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>
```

If you forgot the AGENT_ENGINE_ID, you can list existing agents using:

```bash
python3 deployment/deploy.py --list
```

The output will be like:

```
All remote agents:

123456789 ("academic_research")
- Create time: 2025-05-10 09:33:46.188760+00:00
- Update time: 2025-05-10 09:34:32.763434+00:00

```

You may interact with the deployed agent using the `test_deployment.py` script
```bash
$ export USER_ID=<any string>
$ python3 deployment/test_deployment.py --resource_id=${AGENT_ENGINE_ID} --user_id=${USER_ID}
Found agent with resource ID: ...
Created session for user ID: ...
Type 'quit' to exit.
Input: What can you do?
Response: Hello! I'm SecPatch, your AI Security Patching Assistant. I can help you identify vulnerabilities in your systems, find appropriate patches, analyze their impact, and guide you through the patching process.

How can I assist you today? For example, you can ask me to check a specific software or system for vulnerabilities.
```

To delete the deployed agent, you may run the following command:

```bash
python3 deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

## Customization

<!-- TODO: Update this based on SecPath -->
The SecPatch can be customized to better suit your requirements. For example:

 1. Use 

 