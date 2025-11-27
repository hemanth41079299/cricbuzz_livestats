import streamlit as st
import pandas as pd

from utils.db_connection import run_select_query
from utils.sql_queries import SQL_QUERIES

st.set_page_config(page_title="SQL Analytics", page_icon="🧮", layout="wide")


def main():
    st.title("🧮 SQL Analytics")
    st.caption(
        "Run pre-built SQL queries on the cricket database. "
        "These queries correspond to the project questions (Beginner / Intermediate / Advanced)."
    )

    st.divider()

    # --- Sidebar / controls for level + question selection ---
    levels = sorted({q["level"] for q in SQL_QUERIES})
    selected_level = st.selectbox("Difficulty Level", levels, index=0)

    level_questions = [q for q in SQL_QUERIES if q["level"] == selected_level]

    question_labels = [f'{q["id"]} – {q["title"]}' for q in level_questions]
    selected_label = st.selectbox("Select Question", question_labels, index=0)

    # Find the selected query object
    selected_query = level_questions[question_labels.index(selected_label)]

    st.subheader(f'{selected_query["id"]} – {selected_query["title"]}')
    st.write(selected_query["description"])

    st.markdown("**SQL Query:**")
    st.code(selected_query["sql"].strip(), language="sql")

    run_btn = st.button("▶ Run Query")

    if run_btn:
        with st.spinner("Running SQL query..."):
            rows = run_select_query(selected_query["sql"])
            if not rows:
                st.warning("Query executed successfully, but returned no rows.")
                return

            df = pd.DataFrame(rows)
            st.markdown("**Result:**")
            st.dataframe(df, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
