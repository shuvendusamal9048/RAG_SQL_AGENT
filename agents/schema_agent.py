
import json
import re
from agents.llm import llm

JSON_EXTRACT_RE = re.compile(r"\{[\s\S]*\}", re.DOTALL)

def _extract_json(text: str):
    """
    Extract the first {...} block and parse JSON, return dict or raise.
    """
    if not text or not isinstance(text, str):
        raise ValueError("Empty response from LLM")

    m = JSON_EXTRACT_RE.search(text)
    if not m:
        raise ValueError("No JSON object found in model response")

    json_text = m.group(0)
    return json.loads(json_text)

def schema_agent(schema_json: dict, question: str):
    try:
        if not isinstance(schema_json, dict) or "tables" not in schema_json:
            return {"tables": [], "columns": {}, "error": "Invalid schema_json passed to schema_agent"}

        prompt = f"""
You are a strict JSON-only generator. Use the database schema provided to decide which tables and columns
are relevant to answer the user's question.

Database schema (JSON):
{json.dumps(schema_json, indent=2)}

User question:
\"\"\"{question}\"\"\"

Return ONLY a JSON object with this exact shape:
{{
  "tables": ["table_name", ...],
  "columns": {{
     "table_name": ["col1","col2", ...],
     ...
  }}
}}

Rules:
- Output JSON ONLY (no explanation, no markdown, no code fences).
- If nothing matches, return {{ "tables": [], "columns": {{}} }}.
- Use table names exactly as present in the schema (case-sensitive).
- Keep column lists minimal — only columns relevant to answer the question.
"""

        resp = llm.invoke(prompt)
        text = getattr(resp, "content", resp)  # support both objects/strings
        parsed = _extract_json(text)
        # validate structure
        tables = parsed.get("tables", [])
        cols = parsed.get("columns", {})
        if not isinstance(tables, list) or not isinstance(cols, dict):
            return {"tables": [], "columns": {}, "error": "Invalid JSON structure from model"}
        return {"tables": tables, "columns": cols}

    except Exception as e:
        return {"tables": [], "columns": {}, "error": str(e)}
