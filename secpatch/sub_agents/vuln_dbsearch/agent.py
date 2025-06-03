# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Database Agent: get data from PostgreSQL database using NL2SQL."""

import os

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from . import tools # tools.py in the same directory
from .prompts import return_instructions_postgresql # prompts.py in the same directory

MODEL = os.getenv("VULN_DBSEARCH_MODEL", "gemini-1.5-flash-preview-0514") # Or your preferred model

def setup_before_agent_call(context: CallbackContext):
    """Sets up necessary state before the agent call, like DDL schema."""
    # If your tools.initial_pg_nl2sql needs the DDL schema from context.state,
    # you would set it up here. However, the modified tools.py now directly uses
    # the TABLE_SCHEMA_DDL constant from tools.py, so this might not be strictly needed
    # for the DDL schema itself, but can be used for other settings.
    if "database_settings" not in context.state:
        context.state["database_settings"] = {}
    # context.state["database_settings"]["pg_ddl_schema"] = tools.TABLE_SCHEMA_DDL # Example

database_agent = Agent(
    model=MODEL,
    name="database_agent",
    instruction=return_instructions_postgresql(),
    tools=[tools.initial_pg_nl2sql, tools.run_postgresql_validation],
    before_agent_callback=setup_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
