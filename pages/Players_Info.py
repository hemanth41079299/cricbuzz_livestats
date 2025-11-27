import streamlit as st
import pandas as pd

from utils.db_connection import run_select_query

st.set_page_config(page_title="Players Info", page_icon="👥", layout="wide")


def load_players_with_stats() -> pd.DataFrame:
    """
    Combine basic player info with aggregated batting + bowling stats.
    """
    query = """
        SELECT
            p.player_id,
            p.full_name AS Player,
            p.country AS Country,
            p.playing_role AS Role,
            p.batting_style AS Batting_Style,
            p.bowling_style AS Bowling_Style,
            COALESCE(bat.total_runs, 0) AS Total_Runs,
            COALESCE(bat.innings, 0) AS Innings,
            COALESCE(bat.avg_runs, 0) AS Avg_Runs,
            COALESCE(bowl.total_wickets, 0) AS Total_Wickets,
            COALESCE(bowl.overs_bowled, 0) AS Overs_Bowled,
            COALESCE(bowl.economy, 0) AS Economy
        FROM players p
        LEFT JOIN (
            SELECT
                player_id,
                SUM(runs) AS total_runs,
                COUNT(*) AS innings,
                ROUND(AVG(runs), 2) AS avg_runs
            FROM player_match_batting
            GROUP BY player_id
        ) bat ON bat.player_id = p.player_id
        LEFT JOIN (
            SELECT
                player_id,
                SUM(wickets) AS total_wickets,
                SUM(overs) AS overs_bowled,
                ROUND(SUM(runs_conceded) / NULLIF(SUM(overs), 0), 2) AS economy
            FROM player_match_bowling
            GROUP BY player_id
        ) bowl ON bowl.player_id = p.player_id
        ORDER BY p.full_name;
    """
    rows = run_select_query(query)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def main():
    st.title("👥 Players Directory")
    st.caption(
        "Browse all players stored in the Cricbuzz LiveStats database with basic bio and aggregated stats."
    )

    st.divider()

    df = load_players_with_stats()

    if df.empty:
        st.warning("No players found in the database yet.")
        return

    # ---- Filters ----
    col1, col2, col3 = st.columns(3)

    with col1:
        search_name = st.text_input("Search by player name")

    with col2:
        countries = ["All"] + sorted(df["Country"].dropna().unique().tolist())
        country_filter = st.selectbox("Filter by country", countries)

    with col3:
        roles = ["All"] + sorted(df["Role"].dropna().unique().tolist())
        role_filter = st.selectbox("Filter by role", roles)

    filtered = df.copy()

    if search_name:
        filtered = filtered[filtered["Player"].str.contains(search_name, case=False, na=False)]

    if country_filter != "All":
        filtered = filtered[filtered["Country"] == country_filter]

    if role_filter != "All":
        filtered = filtered[filtered["Role"] == role_filter]

    st.markdown(f"**Total players shown: {len(filtered)}**")

    st.dataframe(
        filtered[
            [
                "Player",
                "Country",
                "Role",
                "Batting_Style",
                "Bowling_Style",
                "Total_Runs",
                "Innings",
                "Avg_Runs",
                "Total_Wickets",
                "Overs_Bowled",
                "Economy",
            ]
        ],
        width="stretch",
        hide_index=True,
    )


if __name__ == "__main__":
    main()
