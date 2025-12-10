# connect/db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def run_sql(query: str):
    """
    Execute SQL safely and return list[dict] for SELECT or {"status":"success"} for others,
    or {"error": message} on failure.
    """
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            return {"error": "DATABASE_URL not set in environment"}

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)

        if cur.description:  # SELECT
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return rows
        else:
            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success"}
    except Exception as e:
        # return the error message for debugging in dev; sanitize in prod
        return {"error": str(e)}
