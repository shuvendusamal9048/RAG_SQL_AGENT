# agents/sql_agent.py
import json
import re
from agents.llm import llm

SQL_START_RE = re.compile(r"(SELECT|WITH|INSERT|UPDATE|DELETE|CREATE|DROP)\b", re.IGNORECASE)
SQL_EXTRACT_RE = re.compile(r"(SELECT|WITH|INSERT|UPDATE|DELETE|CREATE|DROP)[\s\S]*", re.IGNORECASE)

def _clean_sql_text(text: str) -> str:

    if not isinstance(text, str):
        text = str(text)


    text = text.replace("```sql", "").replace("```", "")

    text = text.strip()

    m = SQL_EXTRACT_RE.search(text)
    if m:
        return m.group(0).strip()
    return text

def generate_sql(schema_json: dict, question: str):
    """
    Use LLM to generate SQL given schema and question.
    Returns {"sql": "..."} or {"error": "..."}
    """
    try:
        prompt = f"""
You are an expert PostgreSQL SQL generator. Use the provided database schema and generate a valid SQL statement
that answers the user's question. Use proper joins when multiple tables are required.
Return ONLY the SQL statement. Do NOT include markdown, backticks, or explanation.

Schema:
{json.dumps(schema_json, indent=2)}

Question:
\"\"\"{question}\"\"\"

Requirements:
- Use table names exactly as in the schema.
- Handle aggregations (SUM, COUNT, AVG), GROUP BY where necessary.
- Handle simple temporal phrases like "last month", "last year", "Q1 2023".
- When returning columns, avoid SELECT * unless question requests "all columns".
- Output a single SQL statement (or a WITH... SELECT).
"""

        resp = llm.invoke(prompt)
        text = getattr(resp, "content", resp)
        sql_text = _clean_sql_text(text)

        if not SQL_START_RE.match(sql_text):
            return {"error": "Generated text does not appear to be valid SQL", "raw": sql_text}

        return {"sql": sql_text}

    except Exception as e:
        return {"error": str(e)}
