# RAG_SQL_AGENT

An AI-powered  RAG SQL assistant that allows users to ask natural language questions about a PostgreSQL database. The system generates SQL queries, executes them, and provides results along with natural language explanations.

1. Set up a virtual environment
  python -m venv .venv
  .venv\Scripts\activate

2.Install dependencies
  pip install -r requirements.txt

3.Configure environment variables
  DATABASE_URL=You have to put your Own Database URL
  GEMINI_API_KEY= You have to put your Own API Key

4. Run the Streamlit app
   streamlit run app.py

  Agents Overview
  1. Schema Agent : -

  Identifies relevant tables and columns from the database schema for a user query.

  Input: Database schema JSON, user question

  Output: JSON with relevant tables and columns

  2. SQL Agent 

  Generates valid SQL queries using the schema and user question.

  Handles aggregations, joins, and simple temporal phrases.

  Output: JSON containing the SQL statement

  3. Synthesizer Agent 

  Generates natural language explanations from SQL query results.

  Converts numeric types (Decimal) to JSON-friendly formats.

  Provides user-friendly answers even if no records are returned.


  Usage Example :-
  Q - What is the salary of employee Arjun Mehta?
  
  Schema Agent → finds employees table and salary column

  SQL Agent → generates:

  SELECT salary FROM employees WHERE name ILIKE 'Arjun Mehta';


  DB executes query → returns 55000

  Synthesizer Agent → outputs:

  The salary of Arjun Mehta is 55000.
