# pages/crud_operations.py

import os
import streamlit as st
from dotenv import load_dotenv

from utils.db_connection import (
    get_mysql_schema,
    fetch_table,
    get_table_columns,
    run_select,
    insert_row,
    delete_rows,
    execute_update,
)

# ---------------------------------
# Load DB credentials from .env
# ---------------------------------
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def _ensure_schema_state():
    """Initialize schema in session_state if missing."""
    if "schema" not in st.session_state:
        st.session_state["schema"] = None
    return st.session_state["schema"]


def show_crud_operations():
    st.title("🛠️ CRUD Operations")
    st.caption("Create, Read, Update, Delete records from your Cricbuzz MySQL database.")

    schema = _ensure_schema_state()

    # -------------------------------
    # 0) Show how connection is handled
    # -------------------------------
    st.header("🔌 MySQL Connection")

    # Tell the user we are using .env
    st.info(
        f"""
Database connection details are loaded securely from your `.env` file:

- Host: `{DB_HOST}`
- User: `{DB_USER}`
- Password: **hidden**
        
You can change these by editing `.env` (DB_HOST, DB_USER, DB_PASSWORD).
"""
    )

    # Safety check – if .env not set properly, stop early
    if DB_HOST is None or DB_USER is None:
        st.error("❌ DB_HOST / DB_USER not set in `.env`. Please configure them.")
        return

    if st.button("Connect & Discover Databases"):
        try:
            schema = get_mysql_schema(DB_HOST, DB_USER, DB_PASSWORD)
            st.session_state["schema"] = schema
            st.success(f"✅ Connected. Found {len(schema)} database(s).")
        except Exception as e:
            st.error(f"❌ Failed to connect / discover schema: {e}")
            return

    schema = st.session_state.get("schema")
    st.divider()

    # -------------------------------
    # 2) Choose database & table
    # -------------------------------
    if not schema:
        st.info("Connect first to load schema information.")
        return

    st.header("📂 Select Database & Table")

    dbs = sorted(schema.keys())
    if not dbs:
        st.warning("No user databases found.")
        return

    default_db = "cricbuzz_db" if "cricbuzz_db" in dbs else dbs[0]
    database = st.selectbox(
        "Choose Database",
        dbs,
        index=max(0, dbs.index(default_db)),
    )

    tables = sorted(schema[database]["tables"].keys()) if database else []
    if not tables:
        st.warning("No tables found in this database.")
        return

    priority_tables = [
        "players",
        "recent_matches",
        "series_matches",
        "top_odi_runs",
        "venues",
        "players_stats",
        "combined_matches",
        "batting_data",
        "bowling_data",
        "batters_batting_data",
        "bowlers_bowling_venue_data",
    ]

    default_table = next((t for t in priority_tables if t in tables), tables[0])
    table = st.selectbox(
        "Choose Table",
        tables,
        index=max(0, tables.index(default_table)),
    )

    st.divider()

    # -------------------------------
    # 3) View / Read Table
    # -------------------------------
    st.subheader("📖 View Table Data")

    limit = st.number_input(
        "Rows to load",
        min_value=1,
        max_value=10_000,
        value=200,
        step=50,
    )

    if st.button("📥 Load Data"):
        try:
            df, sql = fetch_table(DB_HOST, DB_USER, DB_PASSWORD, database, table, int(limit))
            st.code(sql, language="sql")
            st.dataframe(df, width="stretch")
            st.session_state["last_df"] = df
        except Exception as e:
            st.error(f"❌ Read failed: {e}")

    # -------------------------------
    # 4) Custom SELECT
    # -------------------------------
    with st.expander("🔎 Run Custom SELECT"):
        st.caption("Only `SELECT` queries are allowed here (read-only).")
        custom_sql = st.text_area(
            "Write your SELECT query:",
            height=130,
            placeholder="SELECT * FROM players LIMIT 50;",
        )

        if st.button("▶️ Run SELECT"):
            sql = custom_sql.strip()
            if not sql:
                st.warning("Please enter a SELECT query.")
            elif not sql.lower().startswith("select"):
                st.error("Only SELECT queries are allowed in this section.")
            else:
                try:
                    df = run_select(DB_HOST, DB_USER, DB_PASSWORD, database, sql)
                    st.dataframe(df, width="stretch")
                except Exception as e:
                    st.error(f"❌ Query failed: {e}")

    st.divider()

    # -------------------------------
    # 5) Insert Row
    # -------------------------------
    st.subheader("➕ Insert Row")

    try:
        cols_meta = get_table_columns(DB_HOST, DB_USER, DB_PASSWORD, database, table)
    except Exception as e:
        st.error(f"Failed to fetch column metadata: {e}")
        cols_meta = []

    if not cols_meta:
        st.info("No column metadata found for this table.")
    else:
        with st.form("add_row_form", clear_on_submit=True):
            st.caption("Fill values for columns (leave blank for auto-increment / nullable fields).")
            inputs = {}

            for col in cols_meta:
                name = col["name"]
                dtype = col["type"]
                extra = (col.get("extra") or "").lower()

                # Skip auto-increment columns
                if "auto_increment" in extra:
                    st.text_input(f"{name} ({dtype}) [auto]", value="", disabled=True)
                    continue

                val = st.text_input(f"{name} ({dtype})", value="")
                inputs[name] = None if val.strip() == "" else val

            submitted = st.form_submit_button("✅ Insert Row")
            if submitted:
                clean = {k: v for k, v in inputs.items() if v is not None}
                if not clean:
                    st.warning("No values provided to insert.")
                else:
                    try:
                        affected, sql = insert_row(DB_HOST, DB_USER, DB_PASSWORD, database, table, clean)
                        st.code(sql, language="sql")
                        st.success(f"Inserted {affected} row(s).")
                    except Exception as e:
                        st.error(f"❌ Insert failed: {e}")

    st.divider()

    # -------------------------------
    # 6) Delete Row(s)
    # -------------------------------
    st.subheader("🗑️ Delete Row(s)")

    with st.form("delete_form"):
        st.caption("Provide a safe WHERE clause. Example: `player_id = 576`")
        where_clause = st.text_input("WHERE condition", placeholder="player_id = 576")
        delete_ok = st.form_submit_button("⚠️ Delete")

        if delete_ok:
            where = where_clause.strip()
            if not where:
                st.warning("WHERE clause cannot be empty for delete.")
            else:
                try:
                    affected, sql = delete_rows(DB_HOST, DB_USER, DB_PASSWORD, database, table, where)
                    st.code(sql, language="sql")
                    st.success(f"Deleted {affected} row(s).")
                except Exception as e:
                    st.error(f"❌ Delete failed: {e}")

    st.divider()

    # -------------------------------
    # 7) Update Row(s)
    # -------------------------------
    st.subheader("📝 Update Rows")

    with st.form("update_form"):
        st.caption("Example SET: `runs = 120, strike_rate = 150.0`")
        set_part = st.text_input("SET clause", placeholder="runs = 120, strike_rate = 150.0")

        st.caption("Example WHERE: `player_id = 576 AND match_id = 100283`")
        where_part = st.text_input("WHERE clause", placeholder="player_id = 576 AND match_id = 100283")

        upd = st.form_submit_button("✏️ Run Update")

        if upd:
            set_sql = set_part.strip()
            where_sql = where_part.strip()

            if not set_sql or not where_sql:
                st.warning("Both SET and WHERE clauses are required.")
            else:
                try:
                    affected, sql = execute_update(
                        DB_HOST, DB_USER, DB_PASSWORD, database, table, set_sql, where_sql
                    )
                    st.code(sql, language="sql")
                    st.success(f"Updated {affected} row(s).")
                except Exception as e:
                    st.error(f"❌ Update failed: {e}")


if __name__ == "__main__":
    show_crud_operations()
