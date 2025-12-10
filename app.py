import streamlit as st
from dotenv import load_dotenv
import os
import json
from decimal import Decimal

load_dotenv()


from connect.schema_loader import load_schema
from agents.schema_agent import schema_agent
from agents.sql_agent import generate_sql
from connect.db import run_sql
from agents.synth_agent import generate_natural_answer  # Synthesizer Agent

st.set_page_config(
    page_title="RAG SQL Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("AI SQL Assistant")

# Load schema internally (DO NOT DISPLAY)
schema_data = load_schema()

if "error" in schema_data:
    st.error(f"Error loading database schema: {schema_data['error']}")
    st.stop()

question = st.text_input("Ask a question about your database:", "")

if st.button("Run Query"):
    if not question.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Step 1 — Schema Agent: identifying relevant tables/columns..."):
            schema_result = schema_agent(schema_data, question)


        st.subheader("Schema Agent Output (Relevant Tables & Columns)")
        st.json(schema_result)


        if schema_result.get("error"):
            st.error("Schema Agent failed: " + schema_result["error"])
            st.stop()
        if not schema_result.get("tables"):
            st.warning("No relevant tables found for your question. Please check your question or database schema.")
            st.stop()


        with st.spinner("Step 2 — SQL Agent: generating SQL..."):
            sql_resp = generate_sql(schema_data, question)

        if sql_resp.get("error"):
            st.error(f"SQL generation failed: {sql_resp['error']}")
            if "raw" in sql_resp:
                st.info(f"Raw generated text: {sql_resp['raw']}")
            st.stop()

        sql_query = sql_resp["sql"]
        st.subheader("Generated SQL")
        st.code(sql_query, language="sql")


        with st.spinner("Step 3 — Executing SQL on database..."):
            results = run_sql(sql_query)


        if isinstance(results, dict) and results.get("error"):
            st.error("Database error: " + results["error"])
            natural_answer = f"Database error occurred: {results['error']}"
        else:
            row_count = len(results)
            if row_count == 0:
                st.warning("Query executed successfully but returned no matching records.")
            else:
                st.success(f"Query executed successfully. Returned {row_count} rows.")
                st.dataframe(results)

            # Step 4 — Convert Decimal to float for JSON serialization
            def convert_decimals(obj):
                if isinstance(obj, list):
                    return [convert_decimals(item) for item in obj]
                elif isinstance(obj, dict):
                    return {k: convert_decimals(v) for k, v in obj.items()}
                elif isinstance(obj, Decimal):
                    return float(obj)
                return obj

            results_serializable = convert_decimals(results)


            with st.spinner("Step 4 — Synthesizing natural language answer..."):
                if row_count == 0:
                    natural_answer = "Your query executed successfully but returned no matching records."
                else:
                    natural_answer = generate_natural_answer(
                        query=sql_query,
                        result=results_serializable,  # <- safe for JSON
                        tables=schema_result.get("tables", []),
                        columns=[col for cols in schema_result.get("columns", {}).values() for col in cols]
                    )

        st.subheader("Natural Language Answer")
        st.write(natural_answer)
