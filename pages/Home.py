import streamlit as st
import pandas as pd

from utils.db_connection import run_select_query

# -------------------------------------------------
# Streamlit page config
# -------------------------------------------------
st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
)


# -------------------------------------------------
# Small helper to fetch a single numeric value
# -------------------------------------------------
def get_single_value(sql: str, default: int | float = 0) -> int | float:
    rows = run_select_query(sql)
    if not rows:
        return default
    # take first row's first value
    first_row = rows[0]
    if not first_row:
        return default
    val = list(first_row.values())[0]
    return val if val is not None else default


# -------------------------------------------------
# Header / intro
# -------------------------------------------------
st.title("🏏 Cricbuzz LiveStats – Home")

st.markdown(
    """
Welcome to **Cricbuzz LiveStats** – a mini analytics platform built on:

- **MySQL** for storing teams, players, matches, venues and scorecards  
- **Cricbuzz API (RapidAPI)** for live matches and detailed scorecards  
- **Streamlit** for interactive dashboards and SQL analytics  

Use the sidebar to navigate:
- **Live Matches** – real-time data from Cricbuzz API  
- **Match Scorecard** – detailed batting & bowling cards  
- **Top Player Stats** – SQL-based batting & bowling leaders  
- **Players Directory** – all players stored in your database  
- **CRUD Operations** – manage master data  
- **SQL Analytics Lab** – run predefined SQL questions  
"""
)

st.divider()

# -------------------------------------------------
# High-level metrics
# -------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_series = get_single_value("SELECT COUNT(*) AS c FROM series;")
total_matches = get_single_value("SELECT COUNT(*) AS c FROM matches;")
total_teams = get_single_value("SELECT COUNT(*) AS c FROM teams;")
total_players = get_single_value("SELECT COUNT(*) AS c FROM players;")

col1.metric("Series in DB", int(total_series))
col2.metric("Matches in DB", int(total_matches))
col3.metric("Teams", int(total_teams))
col4.metric("Players", int(total_players))

st.caption(
    "These numbers come directly from your MySQL database and will grow as you insert more data."
)

st.divider()

# -------------------------------------------------
# Recent matches overview
# -------------------------------------------------
st.subheader("🧾 Recent Matches Snapshot")

recent_matches_sql = """
    SELECT
        m.match_id,
        s.series_name,
        m.match_format,
        m.match_date,
        t1.team_name AS team1,
        t2.team_name AS team2,
        v.venue_name,
        v.city,
        CASE
            WHEN w.team_name IS NOT NULL THEN w.team_name
            ELSE 'No Result / Tie'
        END AS winner
    FROM matches m
    JOIN series s ON s.series_id = m.series_id
    JOIN teams t1 ON t1.team_id = m.team1_id
    JOIN teams t2 ON t2.team_id = m.team2_id
    JOIN venues v ON v.venue_id = m.venue_id
    LEFT JOIN teams w ON w.team_id = m.match_winner_team_id
    ORDER BY m.match_date DESC
    LIMIT 10;
"""

recent_rows = run_select_query(recent_matches_sql)

if recent_rows:
    df_recent = pd.DataFrame(recent_rows)
    st.dataframe(df_recent, width="stretch", hide_index=True)
else:
    st.info("No matches found in the database yet. Add some sample data to see them here.")

st.divider()

# -------------------------------------------------
# Quick navigation tips
# -------------------------------------------------
st.subheader("🚀 Where to go next")

st.markdown(
    """
- Go to **⚡ Live Matches** to see current / recent fixtures from the Cricbuzz API.  
- Open **📊 Top Player Stats** to view batting & bowling leaders from your MySQL data.  
- Use **👥 Players Directory** to browse all players you’ve stored.  
- Try **🧮 SQL Analytics** to run the predefined 25 SQL questions against your schema.  
- Manage master data in **🛠 CRUD Operations**.
"""
)

st.success("App is ready. Use the sidebar to explore each module.")
