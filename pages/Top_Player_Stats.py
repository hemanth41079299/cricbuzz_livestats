import streamlit as st
import pandas as pd

from utils.db_connection import run_select_query

st.set_page_config(page_title="Top Player Stats", page_icon="📊", layout="wide")


def get_top_batsmen(limit: int | None = 10) -> pd.DataFrame:
    """
    Top run scorers from our database.
    Uses player_match_batting + players tables.
    """
    limit_clause = f"LIMIT {limit}" if limit is not None else ""
    query = f"""
        SELECT
            p.full_name   AS Player,
            p.country     AS Country,
            SUM(b.runs)   AS Total_Runs,
            COUNT(DISTINCT b.match_id) AS Matches,
            COUNT(*)      AS Innings,
            ROUND(AVG(b.runs), 2) AS Avg_Runs,
            ROUND(AVG(b.strike_rate), 2) AS Avg_SR
        FROM player_match_batting b
        JOIN players p ON p.player_id = b.player_id
        GROUP BY b.player_id, p.full_name, p.country
        ORDER BY Total_Runs DESC
        {limit_clause};
    """
    rows = run_select_query(query)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def get_top_bowlers(limit: int | None = 10) -> pd.DataFrame:
    """
    Top wicket takers from our database.
    Uses player_match_bowling + players tables.
    """
    limit_clause = f"LIMIT {limit}" if limit is not None else ""
    query = f"""
        SELECT
            p.full_name   AS Player,
            p.country     AS Country,
            SUM(b.wickets)        AS Total_Wickets,
            COUNT(DISTINCT b.match_id) AS Matches,
            SUM(b.overs)          AS Overs_Bowled,
            SUM(b.runs_conceded)  AS Runs_Conceded,
            ROUND(
                SUM(b.runs_conceded) / NULLIF(SUM(b.overs), 0),
                2
            ) AS Economy
        FROM player_match_bowling b
        JOIN players p ON p.player_id = b.player_id
        GROUP BY b.player_id, p.full_name, p.country
        ORDER BY Total_Wickets DESC
        {limit_clause};
    """
    rows = run_select_query(query)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def main():
    st.title("📊 Top Player Stats")
    st.caption(
        "Top batting and bowling performers calculated from the MySQL database. "
        "These stats are SQL-driven and keep working even if the API quota is exhausted."
    )

    st.divider()

    # Control how many players to show
    player_limit = st.slider(
        "Number of players to display",
        min_value=5,
        max_value=100,
        step=5,
        value=10,
        help="Shows top N players based on total runs / wickets.",
    )

    tab1, tab2 = st.tabs(["🏏 Batting Records", "🎯 Bowling Records"])

    with tab1:
        st.subheader("🏏 Top Run Scorers")
        df_bat = get_top_batsmen(limit=player_limit)

        if df_bat.empty:
            st.warning("No batting data available in the database yet.")
        else:
            st.dataframe(df_bat, width="stretch", hide_index=True)

    with tab2:
        st.subheader("🎯 Top Wicket Takers")
        df_bowl = get_top_bowlers(limit=player_limit)

        if df_bowl.empty:
            st.warning("No bowling data available in the database yet.")
        else:
            st.dataframe(df_bowl, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
