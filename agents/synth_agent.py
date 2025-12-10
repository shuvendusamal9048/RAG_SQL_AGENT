
from agents.llm import llm
import json


def generate_natural_answer(query, result, tables, columns):

    try:
        prompt = f"""
You are an intelligent assistant. Based on the SQL query, its result, and relevant schema information,
generate a clear and concise natural language answer for a user.

SQL Query: {query}
Result: {json.dumps(result, indent=2)}
Relevant Tables: {tables}
Relevant Columns: {columns}

Provide a clear, user-friendly answer in plain English. Do not include code or JSON.
"""
        resp = llm.invoke(prompt)
        answer = getattr(resp, "content", resp)  # support object/string response
        return answer.strip()
    except Exception as e:
        return f"Error generating natural language answer: {str(e)}"
