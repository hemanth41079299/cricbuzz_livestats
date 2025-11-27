import streamlit as st
import pandas as pd

from utils.db_connection import run_select_query

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide"
)


def get_count(query: str) -> int:
    """
    Helper to run a COUNT(*) query and safely return 0 if no rows.
    """
    rows = run_select_query(query)
    if not rows:
        return 0
    # rows is a list of dicts like [{'c': 2}]
    return int(rows[0].get("c", 0))


st.title("🏏 Cricbuzz LiveStats – Home")

st.markdown(
    """
Welcome to **Cricbuzz LiveStats** – a cricket analytics dashboard built with:

- 🐍 **Python**
- 🗄️ **MySQL** for structured cricket data
- 🌐 **Cricbuzz API (RapidAPI)** for live and recent match info
- 📊 **Streamlit** for the interactive web UI

### What you’ll find in this app

- **⚡ Live Matches** – view current / recent matches from the Cricbuzz API  
- **📊 Top Player Stats** – batting & bowling records using API + SQL  
- **🧮 SQL Analytics** – run pre-built SQL queries on your cricket database  
- **🛠️ CRUD Operations** – practice Create / Read / Update / Delete on players & matches  
"""
)

st.divider()

# --- Quick DB summary cards ---
col1, col2, col3, col4 = st.columns(4)

matches_count = get_count("SELECT COUNT(*) AS c FROM matches;")
series_count = get_count("SELECT COUNT(*) AS c FROM series;")
teams_count = get_count("SELECT COUNT(*) AS c FROM teams;")
players_count = get_count("SELECT COUNT(*) AS c FROM players;")

col1.metric("Matches in DB", matches_count)
col2.metric("Series", series_count)
col3.metric("Teams", teams_count)
col4.metric("Players (profiled)", players_count)

st.info(
    "Right now the database is using **sample data** for development and testing. "
    "In later steps, we’ll add scripts to pull live data from the Cricbuzz API "
    "and insert it into MySQL for deeper analytics."
)
