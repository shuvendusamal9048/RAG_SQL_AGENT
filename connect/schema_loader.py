# database/schema_loader.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def load_schema():
    """
    Loads all public tables and their columns from the PostgreSQL database.
    Returns: {"tables": [...], "columns": {"table": [...], ...}}
    On error returns {"error": "message"}
    """
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            return {"error": "DATABASE_URL not set in environment"}

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # fetch tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE';
        """)
        tables = [r["table_name"] for r in cur.fetchall()]

        schema = {"tables": tables, "columns": {}}

        for table in tables:
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table,))
            cols = [r["column_name"] for r in cur.fetchall()]
            schema["columns"][table] = cols

        cur.close()
        conn.close()
        return schema

    except Exception as e:
        return {"error": str(e)}
