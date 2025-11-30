# pages/live_matches.py

import streamlit as st
import pandas as pd
from datetime import datetime

# Use the centralized API client
from utils.api_client import (
    get_live_matches,
    get_match_scorecard,
    CricbuzzAPIError,
)


# -------------------------------
# Helper: Time Conversion
# -------------------------------
def format_time(epoch_ms):
    """Convert epoch ms to human readable date."""
    if not epoch_ms:
        return "N/A"
    try:
        return datetime.fromtimestamp(int(epoch_ms) / 1000).strftime(
            "%d %b %Y, %I:%M %p"
        )
    except Exception:
        return "N/A"


# -------------------------------
# Helper: Render Scorecard
# -------------------------------
def show_innings_scorecard(match_id: str):
    """Display full batting + bowling scorecard using centralized API."""
    try:
        data = get_match_scorecard(match_id)
    except CricbuzzAPIError as e:
        st.error(str(e))
        return

    if not data:
        st.warning("No response received from the Cricbuzz API for this match.")
        return

    # Try multiple possible keys that Cricbuzz might use for innings/scorecards
    innings_list = (
        data.get("scorecard")          # common key
        or data.get("scoreCard")       # camelCase variant
        or data.get("innings")         # sometimes direct innings list
        or data.get("scoreCards")      # another possible naming
    )

    if not innings_list:
        st.warning(
            "No detailed scorecard is available for this match (no innings data found).\n\n"
            "Below is the raw API response to inspect the structure."
        )
        with st.expander("Raw scorecard JSON (debug)"):
            st.json(data)
        return

    # Normalize dict → list, if needed
    if isinstance(innings_list, dict):
        innings_list = list(innings_list.values())

    for i, innings in enumerate(innings_list, start=1):
        # Team name can have different keys
        bat_team_name = (
            innings.get("batteamname")
            or innings.get("batTeamName")
            or innings.get("batTeamShortName")
            or innings.get("batTeam")
            or ""
        )

        st.subheader(f"📊 Inning {i} – {bat_team_name}")

        # ---------------- Batting ----------------
        batsmen_list = []

        # Some responses: innings["batsman"] = list
        if isinstance(innings.get("batsman"), list):
            batsmen_source = innings["batsman"]
        # Others: innings["batsmenData"] = dict of playerId -> stats
        elif isinstance(innings.get("batsmenData"), dict):
            batsmen_source = innings["batsmenData"].values()
        else:
            batsmen_source = []

        for batsman in batsmen_source:
            batsmen_list.append(
                {
                    "Name": batsman.get("name") or batsman.get("batName", ""),
                    "Runs": batsman.get("runs") or batsman.get("r", 0),
                    "Balls": batsman.get("balls") or batsman.get("b", 0),
                    "4s": batsman.get("fours") or batsman.get("4s", 0),
                    "6s": batsman.get("sixes") or batsman.get("6s", 0),
                    "SR": batsman.get("strkrate") or batsman.get("sr", 0),
                    "Out": batsman.get("outdec") or batsman.get("howOut", ""),
                }
            )

        if batsmen_list:
            st.write("### 🏏 Batting")
            st.dataframe(pd.DataFrame(batsmen_list), width="stretch")
        else:
            st.info("No batting details found for this innings.")

        # ---------------- Bowling ----------------
        bowlers_list = []

        # Some responses: innings["bowler"] = list
        if isinstance(innings.get("bowler"), list):
            bowlers_source = innings["bowler"]
        # Others: innings["bowlersData"] = dict of playerId -> stats
        elif isinstance(innings.get("bowlersData"), dict):
            bowlers_source = innings["bowlersData"].values()
        else:
            bowlers_source = []

        for bowler in bowlers_source:
            bowlers_list.append(
                {
                    "Name": bowler.get("name") or bowler.get("bowlName", ""),
                    "Overs": bowler.get("overs") or bowler.get("ov", 0),
                    "Runs": bowler.get("runs") or bowler.get("r", 0),
                    "Wickets": bowler.get("wickets") or bowler.get("w", 0),
                    "Maidens": bowler.get("maidens") or bowler.get("m", 0),
                    "Economy": bowler.get("economy") or bowler.get("econ", 0),
                }
            )

        if bowlers_list:
            st.write("### 🎯 Bowling")
            st.dataframe(pd.DataFrame(bowlers_list), width="stretch")
        else:
            st.info("No bowling details found for this innings.")

        st.markdown("---")


# -------------------------------
# MAIN PAGE
# -------------------------------
def show_live_matches():
    st.title("⚡ Live Cricket Matches")

    # Fetch Live Matches
    try:
        data = get_live_matches()
    except CricbuzzAPIError as e:
        st.error(str(e))
        return

    if not data:
        st.warning("No live matches right now.")
        return

    # -------------------------------
    # Build list of series → matches
    # -------------------------------
    series_options = {}
    for type_match in data.get("typeMatches", []):
        match_type = type_match.get("matchType", "UNKNOWN").upper()
        for series in type_match.get("seriesMatches", []):
            wrapper = series.get("seriesAdWrapper", {})
            matches = wrapper.get("matches")

            if not matches:
                continue

            series_name = wrapper.get("seriesName", "Unnamed Series")
            key = f"{series_name} ({match_type})"
            series_options[key] = matches

    if not series_options:
        st.warning("No active series found.")
        return

    selected_series = st.selectbox(
        "Select a Live Series",
        list(series_options.keys()),
    )

    matches = series_options[selected_series]

    # -------------------------------
    # Display each match in the series
    # -------------------------------
    for match in matches:
        info = match.get("matchInfo", {})
        score = match.get("matchScore", {})

        team1_info = info.get("team1", {})
        team2_info = info.get("team2", {})

        team1 = team1_info.get("teamName", "Team 1")
        team2 = team2_info.get("teamName", "Team 2")

        team1_short = team1_info.get("teamSName", "")
        team2_short = team2_info.get("teamSName", "")

        match_id = info.get("matchId", "")

        # ---------- Header ----------
        st.subheader(f"🆚 {team1} vs {team2}")

        st.write(
            f"**Match:** {info.get('matchDesc', '')} "
            f"({info.get('matchFormat', '')})"
        )
        st.write(f"**Status:** {info.get('status', '')}")
        st.write(f"**State:** {info.get('stateTitle', '')}")

        # ---------- Venue ----------
        venue = info.get("venueInfo", {})
        st.write(
            f"**Venue:** {venue.get('ground', '')}, "
            f"{venue.get('city', '')}"
        )
        st.write(f"**Start:** {format_time(info.get('startDate'))}")
        st.write(f"**End:** {format_time(info.get('endDate'))}")

        # ---------- Score (Team 1) ----------
        t1_inn = score.get("team1Score", {}).get("inngs1", {})
        if t1_inn:
            st.success(
                f"{team1_short}: {t1_inn.get('runs', 0)}/"
                f"{t1_inn.get('wickets', 0)} in "
                f"{t1_inn.get('overs', 0)} overs"
            )

        # ---------- Score (Team 2) ----------
        t2_inn = score.get("team2Score", {}).get("inngs1", {})
        if t2_inn:
            st.success(
                f"{team2_short}: {t2_inn.get('runs', 0)}/"
                f"{t2_inn.get('wickets', 0)} in "
                f"{t2_inn.get('overs', 0)} overs"
            )

        # ---------- View Scorecard Button ----------
        if match_id:
            if st.button(
                f"📑 View Scorecard – {team1_short} vs {team2_short}",
                key=f"btn_{match_id}",
            ):
                show_innings_scorecard(match_id)

        st.markdown("---")


# Debug mode (if run directly)
if __name__ == "__main__":
    show_live_matches()
