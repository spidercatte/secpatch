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

"""Test cases for the Academic Research."""

import textwrap
import unittest

import dotenv
import pytest
from academic_research.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


class TestAgents(unittest.TestCase):
    """Basic test for the agent academic research."""

    def test_happy_path(self):
        """Runs the agent on a simple input and expects a normal response."""
        user_input = textwrap.dedent(
            """
            Double check this:
            Question: who are you
            Answer: Hello! I am an AI Research Assistant.
        """
        ).strip()

        runner = InMemoryRunner(agent=root_agent)
        session = runner.session_service.create_session(
            app_name=runner.app_name, user_id="test_user"
        )
        content = UserContent(parts=[Part(text=user_input)])
        events = list(
            runner.run(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content,
            )
        )
        response = events[-1].content.parts[0].text

        # The answer in the input is wrong, so we expect the agent to provided a
        # revised answer, and the correct answer should mention research.
        self.assertIn("research", response.lower())
