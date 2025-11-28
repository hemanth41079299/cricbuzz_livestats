import streamlit as st
import pandas as pd
from datetime import datetime

from utils.api_handler import get_live_matches, get_match_scorecard

st.set_page_config(page_title="Live Matches", page_icon="⚡", layout="wide")


@st.cache_data(ttl=60)
def fetch_live_matches_data():
    """
    Call Cricbuzz API and return the raw JSON.
    Cached for 60 seconds so you don’t hammer the API.
    """
    return get_live_matches()


def parse_live_matches(data: dict) -> pd.DataFrame:
    """
    Flatten the Cricbuzz live matches JSON into a clean DataFrame.

    Columns: Match ID, Match Type, Series, Match, Format, Team 1, Team 2,
             Venue, City, Status, Start Time
    """
    rows = []

    if not data:
        return pd.DataFrame()

    for type_block in data.get("typeMatches", []):
        match_type = type_block.get("matchType")

        for series_block in type_block.get("seriesMatches", []):
            series_wrapper = series_block.get("seriesAdWrapper", {})
            series_name = series_wrapper.get("seriesName")
            matches = series_wrapper.get("matches", [])

            for m in matches:
                match_info = m.get("matchInfo", {})
                team1 = match_info.get("team1", {})
                team2 = match_info.get("team2", {})
                venue = match_info.get("venueInfo", {})

                # startDate is usually epoch millis
                start_ms = match_info.get("startDate")
                start_time = None
                if start_ms:
                    try:
                        start_time = datetime.fromtimestamp(int(start_ms) / 1000.0)
                    except Exception:
                        start_time = None

                rows.append(
                    {
                        "Match ID": match_info.get("matchId"),
                        "Match Type": match_type,
                        "Series": match_info.get("seriesName") or series_name,
                        "Match": match_info.get("matchDesc"),
                        "Format": match_info.get("matchFormat"),
                        "Team 1": team1.get("teamSName") or team1.get("teamName"),
                        "Team 2": team2.get("teamSName") or team2.get("teamName"),
                        "Venue": venue.get("ground"),
                        "City": venue.get("city"),
                        "Status": match_info.get("status"),
                        "Start Time": start_time,
                    }
                )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    if "Start Time" in df.columns:
        df = df.sort_values(by="Start Time", ascending=False)

    return df


def render_scorecard(scorecard_data: dict):
    """
    Render scorecard for the mcenter/v1/{matchId}/hscard structure.

    This version is written to match structures like:
      {
        "status": "...",
        "team1": {"name": "...", ...},
        "team2": {"name": "...", ...},
        "venue": {"name": "...", "city": "..."},
        "scorecard": [
            {
                "inningsid": 1,
                "batsman": [ ... ],
                "bowler":  [ ... ],
                "runs": ..., "wickets": ..., "overs": ...
            },
            ...
        ]
      }
    """
    if not scorecard_data:
        st.warning("No scorecard data returned for this match.")
        return

    # ---- Header / match summary ----
    header = scorecard_data.get("matchInfo") or scorecard_data.get("matchinfo") or scorecard_data

    team1 = header.get("team1", {}) or scorecard_data.get("team1", {})
    team2 = header.get("team2", {}) or scorecard_data.get("team2", {})

    team1_name = (
        team1.get("teamName")
        or team1.get("name")
        or team1.get("sname")
        or ""
    )
    team2_name = (
        team2.get("teamName")
        or team2.get("name")
        or team2.get("sname")
        or ""
    )

    status = header.get("status") or scorecard_data.get("status", "N/A")

    venue = (
        header.get("venue")
        or header.get("venueInfo")
        or scorecard_data.get("venue")
        or {}
    )
    ground = venue.get("name") or venue.get("ground") or "N/A"
    city = venue.get("city") or venue.get("location") or ""

    st.markdown("### 🏟️ Match Summary")
    if team1_name or team2_name:
        st.write(f"**{team1_name} vs {team2_name}**")
    st.write(f"**Status:** {status}")
    st.write(f"**Venue:** {ground}, {city}")

    st.divider()

    # ---- Innings / scorecard ----
    innings_list = (
        scorecard_data.get("scorecard")
        or scorecard_data.get("scoreCard")
        or []
    )

    if not innings_list:
        st.info("Scorecard structure not found in API response (no 'scorecard' key).")
        return

    for inn in innings_list:
        innings_no = inn.get("inningsid") or inn.get("inningsId") or ""
        bat_team = (
            inn.get("batteamname")
            or inn.get("batteam", {}).get("name")
            or inn.get("batteam", {}).get("sname")
            or f"Innings {innings_no}"
        )

        runs = inn.get("runs") or inn.get("score")
        wkts = inn.get("wickets")
        overs = inn.get("overs")

        header_line = f"🏏 {bat_team}"
        if runs is not None and wkts is not None and overs is not None:
            header_line += f" — {runs}/{wkts} in {overs} overs"

        st.markdown(f"#### {header_line}")

        # ---------- Batting ----------
        bats = inn.get("batsman") or []
        bat_rows = []
        if isinstance(bats, dict):
            bats_iter = bats.values()
        else:
            bats_iter = bats

        for b in bats_iter:
            bat_rows.append(
                {
                    "Batter": b.get("name"),
                    "Dismissal": b.get("outdec"),
                    "Runs": b.get("runs"),
                    "Balls": b.get("balls"),
                    "4s": b.get("fours"),
                    "6s": b.get("sixes"),
                    "SR": b.get("strkrate"),
                }
            )

        if bat_rows:
            st.markdown("**Batting**")
            st.dataframe(pd.DataFrame(bat_rows), width="stretch", hide_index=True)
        else:
            st.info("No batting details available for this innings.")

        # ---------- Bowling ----------
        bowlers = inn.get("bowler") or []
        bowl_rows = []
        if isinstance(bowlers, dict):
            bowl_iter = bowlers.values()
        else:
            bowl_iter = bowlers

        for bw in bowl_iter:
            bowl_rows.append(
                {
                    "Bowler": bw.get("name"),
                    "Overs": bw.get("overs"),
                    "Maidens": bw.get("maidens"),
                    "Runs": bw.get("runs"),
                    "Wickets": bw.get("wickets"),
                    "Econ": bw.get("econ"),
                }
            )

        if bowl_rows:
            st.markdown("**Bowling**")
            st.dataframe(pd.DataFrame(bowl_rows), width="stretch", hide_index=True)
        else:
            st.info("No bowling details available for this innings.")

        st.divider()


def main():
    st.title("⚡ Live Matches")

    st.caption(
        "Data fetched from the Cricbuzz API (RapidAPI). "
        "This page shows all currently live / recent matches and lets you view a detailed scorecard."
    )

    with st.spinner("Fetching live matches from Cricbuzz..."):
        raw_data = fetch_live_matches_data()
        df = parse_live_matches(raw_data)

    if df.empty:
        st.warning("No live or recent matches available from the API right now.")
        return

    st.subheader("Live & Recent Matches")
    st.dataframe(df, width="stretch", hide_index=True)

    st.divider()

    st.subheader("📋 View Match Scorecard")

    # Build options for dropdown
    options = df["Match ID"].tolist()
    label_map = {
        row["Match ID"]: f"{row['Match ID']} – {row['Series']} – {row['Match']} ({row['Team 1']} vs {row['Team 2']})"
        for _, row in df.iterrows()
    }

    # Preselect some match if you like (e.g., first row)
    default_index = 0
    if 135057 in options:
        default_index = options.index(135057)

    selected_match_id = st.selectbox(
        "Select Match",
        options,
        index=default_index if options else 0,
        format_func=lambda mid: label_map.get(mid, str(mid)),
    )

    if st.button("🔍 Fetch Scorecard"):
        with st.spinner(f"Fetching scorecard for match {selected_match_id}..."):
            scorecard_data = get_match_scorecard(int(selected_match_id))

        render_scorecard(scorecard_data)


if __name__ == "__main__":
    main()


