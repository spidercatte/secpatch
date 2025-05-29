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

"""Common data schema and types for travel-concierge agents."""

from typing import Optional, Union, List, Literal # Added List and Literal

from google.genai import types
from pydantic import BaseModel, Field


# Convenient declaration for controlled generation.
json_response_config = types.GenerateContentConfig(
    response_mime_type="application/json"
)

class VulnerabilitySearchResult(BaseModel):
    """
    Represents detailed information about a CVE, including affected packages,
    vulnerable versions, fixed versions, code mentions, and sources.
    """
    cve_id: str = Field(description="The CVE identifier (e.g., CVE-XXXX-YYYY).")
    affected_library_package_name: str = Field(description="The name of the affected library or package.")
    vulnerable_versions_found: List[str] = Field(
        description="A list of version strings explicitly identified as vulnerable."
    )
    known_fixed_versions: List[str] = Field(
        description="A list of all version strings identified as containing the fix."
    )
    initial_affected_code_mentions: List[str] = Field(
        description="A list of strings mentioning affected code locations (e.g., file paths, function names)."
    )
    suggested_patch_details: Optional[dict] = Field(
        default=None,
        description=(
            "Optional details about the suggested patch, including a description, "
            "diff content, replacement snippets, and instructions for manual application."
        )
    )
    sources_used: List[str] = Field(
        description="A list of URLs for the sources used to gather this information."
    )


class VulnFixOutcome(BaseModel):
    """
    Represents the outcome of a vulnerability fix attempt by the vuln_fix_agent.
    """
    cve_id: str = Field(description="The CVE identifier that was processed.")
    repository_url: str = Field(description="The URL of the repository targeted for the fix.")
    attempt_number: int = Field(description="The attempt number for this specific fix execution, as provided by the coordinator.")
    suggested_fix_version: Optional[str] = Field(default=None, description="The version suggested for the fix. Can be null if not applicable or if latest was attempted.")
    fix_status: Literal["success", "failure"] = Field(description="The overall status of the fix attempt.")
    error_message: Optional[str] = Field(default=None, description="Error message if the fix_status is 'failure' or if there are warnings.")
    branch_name: Optional[str] = Field(default=None, description="The name of the branch created and pushed if the fix was successful or partially pushed.")
    project_path: str = Field(description="The local project path used for the fix attempt.")


