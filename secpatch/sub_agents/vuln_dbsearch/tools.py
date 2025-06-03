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

"""This file contains the tools used by the database agent."""

import logging
import os
import re
import json
import psycopg2
from psycopg2 import sql

from google.adk.tools import ToolContext
from google.genai import Client

# --- Environment Variables for PostgreSQL Connection ---
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_DATABASE = os.getenv("PG_DATABASE", "cve_info")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "admindo")
PG_PORT = os.getenv("PG_PORT", "5432")

MAX_NUM_ROWS = 80

# Initialize LLM client (if still needed for NL2SQL generation)
# Ensure GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION are set if using Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1") # Default location

llm_client = None
if project_id:
    llm_client = Client(vertexai=True, project=project_id, location=location)
else:
    logging.warning("GOOGLE_CLOUD_PROJECT not set. LLM client for SQL generation will not be initialized.")

# --- PostgreSQL Table Schema ---
TABLE_SCHEMA_DDL = """
CREATE TABLE vulnerability_info (
    cve_id TEXT PRIMARY KEY,
    affected_library_package_name TEXT,
    vulnerable_versions_found TEXT[], -- Array of strings
    known_fixed_versions TEXT[], -- Array of strings
    initial_affected_code_mentions TEXT[], -- Array of strings
    suggested_patch_details JSONB, -- JSONB to store nested JSON structure
    sources_used TEXT[] -- Array of strings
);

-- Example usage for querying:
-- SELECT cve_id, affected_library_package_name, known_fixed_versions FROM vulnerability_info WHERE cve_id = 'CVE-2022-24999';
-- SELECT * FROM vulnerability_info WHERE affected_library_package_name = 'qs' AND '6.5.2' = ANY(vulnerable_versions_found);
"""

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD,
            port=PG_PORT
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to PostgreSQL: {e}")
        raise

def initial_pg_nl2sql(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Generates an initial PostgreSQL query from a natural language question.

    Args:
        question (str): Natural language question.
        tool_context (ToolContext): The tool context to use for generating the SQL
          query.

    Returns:
        str: A PostgreSQL statement to answer this question.
    """
    if not llm_client:
        return "Error: LLM client not initialized. Cannot generate SQL."

    prompt_template = """
You are a PostgreSQL SQL expert tasked with answering user's questions about a PostgreSQL table by generating SQL queries. Your task is to write a PostgreSQL SQL query that answers the following question using the provided context.

**Guidelines:**

- **Table Referencing:** The primary table is `vulnerability_info`. Refer to columns directly.
- **Array Columns:** Columns like `vulnerable_versions_found`, `known_fixed_versions`, `initial_affected_code_mentions`, and `sources_used` are TEXT arrays. Use PostgreSQL array functions like `ANY` or `@>` for querying these (e.g., `'version' = ANY(known_fixed_versions)`).
- **JSONB Column:** The `suggested_patch_details` column is JSONB. Use PostgreSQL JSONB operators (e.g., `->`, `->>`) to query its contents if needed.
- **Aggregations:**  Use all non-aggregated columns from the `SELECT` statement in the `GROUP BY` clause.
- **SQL Syntax:** Return syntactically and semantically correct SQL for PostgreSQL. Use SQL `AS` statement to assign a new name temporarily to a table column.
- **Column Usage:** Use *ONLY* the column names (column_name) mentioned in the Table Schema. Do *NOT* use any other column names. Associate `column_name` mentioned in the Table Schema only to the `table_name` specified under Table Schema.
- **FILTERS:** You should write query effectively  to reduce and minimize the total rows to be returned. For example, you can use filters (like `WHERE`, `HAVING`, etc. (like 'COUNT', 'SUM', etc.) in the SQL query.
- **LIMIT ROWS:**  The maximum number of rows returned should be less than {MAX_NUM_ROWS}.

**Schema:**

The database structure is defined by the following table schema:

```
{SCHEMA}
```

**Natural language question:**

```
{QUESTION}
```

**Think Step-by-Step:** Carefully consider the schema, question, guidelines, and best practices outlined above to generate the correct BigQuery SQL.

   """

    ddl_schema = tool_context.state["database_settings"]["bq_ddl_schema"]

    prompt = prompt_template.format(
        MAX_NUM_ROWS=MAX_NUM_ROWS, TABLE_SCHEMA_DDL=TABLE_SCHEMA_DDL, QUESTION=question
    )

    response = llm_client.models.generate_content(
        model=os.getenv("BASELINE_NL2SQL_MODEL", "gemini-pro"), # Ensure this model is suitable for SQL generation
        contents=prompt,
        generation_config={"temperature": 0.1},
    )

    sql = response.text
    if sql:
        sql = sql.replace("```sql", "").replace("```", "").strip()

    print("\n sql:", sql)

    tool_context.state["sql_query"] = sql

    return sql


def run_postgresql_validation(
    sql_string: str,
    tool_context: ToolContext,
) -> str:
    """Validates PostgreSQL SQL syntax and functionality.

    This function validates the provided SQL string by attempting to execute it
    against PostgreSQL. It performs the following checks:

    1. **SQL Cleanup:**  Preprocesses the SQL string using a `cleanup_sql`
       function.
    2. **DML/DDL Restriction:**  Rejects any SQL queries containing DML or DDL
       statements (e.g., UPDATE, DELETE, INSERT, CREATE, ALTER) to ensure
       read-only operations.
    3. **Syntax and Execution:** Sends the cleaned SQL to BigQuery for validation.
       If the query is syntactically correct and executable, it retrieves the
       results.
    4. **Result Analysis:**  Checks if the query produced any results. If so, it
       formats the rows of the result set for inspection.

    Args:
        sql_string (str): The SQL query string to validate.
        tool_context (ToolContext): The tool context to use for validation.

    Returns:
        str: A message indicating the validation outcome. This includes:
             - "Valid SQL. Results: ..." if the query is valid and returns data.
             - "Valid SQL. Query executed successfully (no results)." if the query
                is valid but returns no data.
             - "Invalid SQL: ..." if the query is invalid, along with the error
                message from PostgreSQL.
    """

    def cleanup_sql(sql_string):
        """Processes the SQL string to get a printable, valid SQL string."""

        # 1. Remove backslashes escaping double quotes
        sql_string = sql_string.replace('\\"', '"')

        # 2. Remove backslashes before newlines (the key fix for this issue)
        sql_string = sql_string.replace("\\\n", "\n")  # Corrected regex

        # 3. Replace escaped single quotes
        sql_string = sql_string.replace("\\'", "'")

        # 4. Replace escaped newlines (those not preceded by a backslash)
        sql_string = sql_string.replace("\\n", "\n")

        # 5. Add limit clause if not present
        if "limit" not in sql_string.lower():
            sql_string = f"{sql_string.rstrip(';')} LIMIT {MAX_NUM_ROWS};"

        return sql_string

    logging.info("Validating SQL: %s", sql_string)
    sql_string = cleanup_sql(sql_string)
    logging.info("Validating SQL (after cleanup): %s", sql_string)

    final_result = {"query_result": None, "error_message": None}

    # Restrictive check for DML and DDL
    if re.search(
        r"(?i)(update|delete|drop|insert|create|alter|truncate|merge)", sql_string
    ):
        final_result["error_message"] = (
            "Invalid SQL: Contains disallowed DML/DDL operations."
        )
        logging.error(final_result["error_message"])
        return final_result # Return immediately if DML/DDL is detected

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(sql_string)
            if cur.description:  # Check if query returned data (e.g., SELECT)
                colnames = [desc[0] for desc in cur.description]
                fetched_rows = cur.fetchall()
                
                # Ensure results are JSON serializable (e.g., convert datetime)
                # For simplicity, this example assumes basic types or already serializable ones.
                # Add specific type conversions if needed (e.g., for datetime, decimal).
                rows = [dict(zip(colnames, row)) for row in fetched_rows]

                if rows:
                    final_result["query_result"] = rows
                    tool_context.state["query_result"] = rows
                else:
                    final_result["query_result"] = [] # Valid SQL, but no rows returned
                    tool_context.state["query_result"] = []
            else: # For queries that don't return rows (e.g., some valid DDL/DML if not blocked, or SET commands)
                 final_result["query_result"] = "Command executed successfully, no rows returned."

    except psycopg2.Error as e:
        logging.error(f"PostgreSQL execution error: {e}")
        final_result["error_message"] = f"Invalid SQL or execution error: {e}"
    except Exception as e:  # Catch other generic exceptions
        logging.error(f"Unexpected error during SQL validation: {e}")
        final_result["error_message"] = f"Unexpected error: {e}"
    finally:
        if conn:
            conn.close()

    print("\n run_postgresql_validation final_result: \n", final_result)

    return final_result
