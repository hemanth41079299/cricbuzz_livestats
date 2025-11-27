import os
from typing import Optional, List, Dict, Any

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load variables from .env file (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
load_dotenv()


def get_db_connection():
    """
    Create and return a MySQL connection object.
    Returns None if connection fails.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "Cricbuzz_livestats"),
        )

        if conn.is_connected():
            return conn

    except Error as e:
        print("❌ Error while connecting to MySQL:", e)

    return None


def run_select_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Run a SELECT query and return rows as a list of dictionaries.
    This is useful for Streamlit tables and SQL Analytics page.
    """
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("Database connection failed. Check .env settings and MySQL server.")

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()


def run_modify_query(query: str, params: Optional[tuple] = None) -> int:
    """
    Run INSERT / UPDATE / DELETE queries.
    Returns number of affected rows.
    """
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("Database connection failed. Check .env settings and MySQL server.")

    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()
