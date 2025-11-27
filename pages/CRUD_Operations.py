import streamlit as st
import pandas as pd

from utils.db_connection import run_select_query, run_modify_query

st.set_page_config(page_title="CRUD Operations", page_icon="🛠️", layout="wide")


def load_players():
    rows = run_select_query(
        """
        SELECT player_id, full_name, country, playing_role, batting_style, bowling_style
        FROM players
        ORDER BY full_name;
        """
    )
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def load_matches():
    rows = run_select_query(
        """
        SELECT
            m.match_id,
            s.series_name,
            m.match_format,
            m.match_date,
            t1.team_name AS team1,
            t2.team_name AS team2
        FROM matches m
        JOIN series s ON m.series_id = s.series_id
        JOIN teams t1 ON m.team1_id = t1.team_id
        JOIN teams t2 ON m.team2_id = t2.team_id
        ORDER BY m.match_date DESC;
        """
    )
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def main():
    st.title("🛠️ CRUD Operations")
    st.caption(
        "Create, Read, Update and Delete records in the cricket database. "
        "This page demonstrates form-based CRUD for **Players** and **Matches**."
    )

    tab1, tab2 = st.tabs(["👤 Players", "🏏 Matches"])

    # ------------------------ PLAYERS TAB ------------------------
    with tab1:
        st.subheader("👤 Manage Players")

        players_df = load_players()

        st.markdown("### Existing Players")
        if players_df.empty:
            st.info("No players found in the database yet.")
        else:
            st.dataframe(players_df, width="stretch", hide_index=True)

        st.divider()

        action = st.radio(
            "Select Action",
            ["Add New Player", "Update Player", "Delete Player"],
            horizontal=True,
        )

        # Shared lists for selects
        player_ids = players_df["player_id"].tolist() if not players_df.empty else []
        player_name_map = {
            row["player_id"]: row["full_name"] for _, row in players_df.iterrows()
        } if not players_df.empty else {}

        # ---------- ADD ----------
        if action == "Add New Player":
            st.markdown("#### ➕ Add New Player")

            col1, col2 = st.columns(2)
            with col1:
                new_id = st.number_input("Player ID (unique)", min_value=1, step=1)
                full_name = st.text_input("Full Name")
                country = st.text_input("Country", value="India")
            with col2:
                role = st.text_input("Playing Role (e.g., Batsman, Bowler)")
                bat_style = st.text_input("Batting Style (e.g., Right-hand bat)")
                bowl_style = st.text_input("Bowling Style (e.g., Right-arm fast)")

            if st.button("💾 Save Player"):
                if not full_name or not country:
                    st.error("Full Name and Country are required.")
                else:
                    try:
                        rows_affected = run_modify_query(
                            """
                            INSERT INTO players
                                (player_id, full_name, country, playing_role, batting_style, bowling_style)
                            VALUES
                                (%s, %s, %s, %s, %s, %s);
                            """,
                            (int(new_id), full_name, country, role, bat_style, bowl_style),
                        )
                        if rows_affected > 0:
                            st.success(f"Player '{full_name}' added successfully.")
                        else:
                            st.warning("Player was not added. Check input values.")
                    except Exception as e:
                        st.error(f"Error inserting player: {e}")

        # ---------- UPDATE ----------
        elif action == "Update Player":
            st.markdown("#### ✏️ Update Player")

            if not player_ids:
                st.info("No players available to update.")
            else:
                selected_id = st.selectbox(
                    "Select Player to Update",
                    player_ids,
                    format_func=lambda pid: f"{pid} – {player_name_map.get(pid, '')}",
                )

                # Pre-fill existing data
                existing = players_df[players_df["player_id"] == selected_id].iloc[0]

                col1, col2 = st.columns(2)
                with col1:
                    full_name = st.text_input("Full Name", value=existing["full_name"])
                    country = st.text_input("Country", value=existing["country"])
                with col2:
                    role = st.text_input("Playing Role", value=existing["playing_role"] or "")
                    bat_style = st.text_input("Batting Style", value=existing["batting_style"] or "")
                    bowl_style = st.text_input("Bowling Style", value=existing["bowling_style"] or "")

                if st.button("💾 Update Player"):
                    try:
                        rows_affected = run_modify_query(
                            """
                            UPDATE players
                            SET full_name = %s,
                                country = %s,
                                playing_role = %s,
                                batting_style = %s,
                                bowling_style = %s
                            WHERE player_id = %s;
                            """,
                            (full_name, country, role, bat_style, bowl_style, int(selected_id)),
                        )
                        if rows_affected > 0:
                            st.success("Player updated successfully.")
                        else:
                            st.warning("No changes were made.")
                    except Exception as e:
                        st.error(f"Error updating player: {e}")

        # ---------- DELETE ----------
        elif action == "Delete Player":
            st.markdown("#### 🗑️ Delete Player")

            if not player_ids:
                st.info("No players available to delete.")
            else:
                selected_id = st.selectbox(
                    "Select Player to Delete",
                    player_ids,
                    format_func=lambda pid: f"{pid} – {player_name_map.get(pid, '')}",
                )

                if st.button("🚨 Confirm Delete"):
                    try:
                        rows_affected = run_modify_query(
                            "DELETE FROM players WHERE player_id = %s;",
                            (int(selected_id),),
                        )
                        if rows_affected > 0:
                            st.success("Player deleted successfully.")
                        else:
                            st.warning("Player not found or already deleted.")
                    except Exception as e:
                        st.error(f"Error deleting player: {e}")

    # ------------------------ MATCHES TAB ------------------------
    with tab2:
        st.subheader("🏏 Manage Matches")

        matches_df = load_matches()

        st.markdown("### Existing Matches")
        if matches_df.empty:
            st.info("No matches found in the database yet.")
        else:
            st.dataframe(matches_df, width="stretch", hide_index=True)

        st.divider()

        match_action = st.radio(
            "Select Action",
            ["Add New Match", "Delete Match"],
            horizontal=True,
        )

        # Basic support tables
        series_rows = run_select_query("SELECT series_id, series_name FROM series ORDER BY series_name;")
        teams_rows = run_select_query("SELECT team_id, team_name FROM teams ORDER BY team_name;")
        venues_rows = run_select_query("SELECT venue_id, venue_name FROM venues ORDER BY venue_name;")

        series_map = {r["series_id"]: r["series_name"] for r in series_rows}
        team_map = {r["team_id"]: r["team_name"] for r in teams_rows}
        venue_map = {r["venue_id"]: r["venue_name"] for r in venues_rows}

        if match_action == "Add New Match":
            st.markdown("#### ➕ Add New Match")

            col1, col2 = st.columns(2)
            with col1:
                match_id = st.number_input("Match ID (unique)", min_value=1, step=1)
                match_date = st.date_input("Match Date")
                match_format = st.selectbox("Format", ["TEST", "ODI", "T20I"])

            with col2:
                series_id = st.selectbox(
                    "Series",
                    list(series_map.keys()) if series_map else [],
                    format_func=lambda sid: series_map.get(sid, str(sid)),
                )
                venue_id = st.selectbox(
                    "Venue",
                    list(venue_map.keys()) if venue_map else [],
                    format_func=lambda vid: venue_map.get(vid, str(vid)),
                )

            col3, col4 = st.columns(2)
            with col3:
                team1_id = st.selectbox(
                    "Team 1",
                    list(team_map.keys()) if team_map else [],
                    format_func=lambda tid: team_map.get(tid, str(tid)),
                )
            with col4:
                team2_id = st.selectbox(
                    "Team 2",
                    list(team_map.keys()) if team_map else [],
                    format_func=lambda tid: team_map.get(tid, str(tid)),
                )

            if st.button("💾 Save Match"):
                if team1_id == team2_id:
                    st.error("Team 1 and Team 2 must be different.")
                else:
                    try:
                        rows_affected = run_modify_query(
                            """
                            INSERT INTO matches
                                (match_id, series_id, venue_id, match_date,
                                 match_format, team1_id, team2_id)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s);
                            """,
                            (
                                int(match_id),
                                int(series_id) if series_map else None,
                                int(venue_id) if venue_map else None,
                                match_date,
                                match_format,
                                int(team1_id),
                                int(team2_id),
                            ),
                        )
                        if rows_affected > 0:
                            st.success("Match added successfully.")
                        else:
                            st.warning("Match was not added. Check input values.")
                    except Exception as e:
                        st.error(f"Error inserting match: {e}")

        else:  # Delete Match
            st.markdown("#### 🗑️ Delete Match")

            if matches_df.empty:
                st.info("No matches available to delete.")
            else:
                match_ids = matches_df["match_id"].tolist()
                match_label_map = {
                    row["match_id"]: f'{row["match_id"]} – {row["series_name"]} ({row["team1"]} vs {row["team2"]})'
                    for _, row in matches_df.iterrows()
                }
                selected_mid = st.selectbox(
                    "Select Match to Delete",
                    match_ids,
                    format_func=lambda mid: match_label_map.get(mid, str(mid)),
                )

                if st.button("🚨 Confirm Delete Match"):
                    try:
                        rows_affected = run_modify_query(
                            "DELETE FROM matches WHERE match_id = %s;",
                            (int(selected_mid),),
                        )
                        if rows_affected > 0:
                            st.success("Match deleted successfully.")
                        else:
                            st.warning("Match not found or already deleted.")
                    except Exception as e:
                        st.error(f"Error deleting match: {e}")


if __name__ == "__main__":
    main()
