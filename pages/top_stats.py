import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# ---------------- Load API Key ----------------
load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")

if not API_KEY:
    st.error(
        "❌ RAPIDAPI_KEY not found in environment variables.\n\n"
        "Create a .env file in your project root with:\n"
        "RAPIDAPI_KEY=your_key_here"
    )
    st.stop()

API_HOST = "cricbuzz-cricket.p.rapidapi.com"
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
}

# ---------------- Helper: Generic GET ----------------
def api_get(path: str, params: dict | None = None, timeout: int = 10):
    """
    Generic helper to call Cricbuzz API and return JSON.
    """
    url = f"{BASE_URL}{path}"
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error {resp.status_code} for {path}: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request error for {path}: {e}")
    return {}

# ---------------- Helper Functions ----------------
def search_players(query: str):
    """Search players by name."""
    return api_get("/stats/v1/player/search", params={"plrN": query})

def get_player_details(player_id: int):
    """Get full profile of a player."""
    return api_get(f"/stats/v1/player/{player_id}")

def get_player_stats(player_id: int, stat_type: str = "batting"):
    """Fetch batting or bowling stats for a player."""
    return api_get(f"/stats/v1/player/{player_id}/{stat_type}")

def get_player_career(player_id: int):
    """Fetch career debut / last played info for all formats."""
    return api_get(f"/stats/v1/player/{player_id}/career")

def parse_stats_table(stats_json):
    """Convert Cricbuzz stats JSON to a DataFrame."""
    if not stats_json or "headers" not in stats_json or "values" not in stats_json:
        return pd.DataFrame()

    headers = stats_json["headers"]
    rows = [row.get("values", []) for row in stats_json["values"]]
    return pd.DataFrame(rows, columns=headers)

# ---------------- Streamlit UI ----------------
def show_top_stats():
    st.title("📊 Player Stats & Profile")

    # Input Player Name
    player_name = st.text_input("Enter player name (e.g. Kohli, Dhoni, Smith):")

    if not player_name:
        return

    results = search_players(player_name)

    if "player" not in results or not results["player"]:
        st.warning("No players found. Try another name.")
        return

    # Build selection from search results
    player_options = {p["name"]: p for p in results["player"]}
    selected_name = st.selectbox("Select a player:", list(player_options.keys()))
    selected_player = player_options[selected_name]

    player_id = selected_player["id"]
    player_details = get_player_details(player_id)

    tabs = st.tabs(["📌 Profile", "🏏 Batting Stats", "🎯 Bowling Stats"])

    # ---------- PROFILE ----------
    with tabs[0]:
        st.write(f"### {selected_player['name']} ({selected_player.get('teamName', 'N/A')})")
        st.write(f"📅 DOB: {selected_player.get('dob', 'N/A')}")

        # Player image
        img_url = None
        if player_details.get("image"):
            img_url = player_details["image"].replace("http://", "https://")
        elif selected_player.get("faceImageId"):
            img_url = f"https://www.cricbuzz.com/a/img/v1/152x152/i1/c{selected_player['faceImageId']}.jpg"

        if img_url:
            st.image(img_url, width=150)
        else:
            st.image("https://placehold.co/150x150/800000/FFFFFF?text=No+Image", width=150)

        # Basic details
        if player_details:
            st.subheader("Player Details")
            st.write(f"**Role:** {player_details.get('role', 'N/A')}")
            st.write(f"**Batting Style:** {player_details.get('bat', 'N/A')}")
            st.write(f"**Bowling Style:** {player_details.get('bowl', 'N/A')}")
            st.write(f"**Teams:** {player_details.get('teams', 'N/A')}")
            st.write(f"**Birth Place:** {player_details.get('birthPlace', 'N/A')}")

            # ICC Rankings
            rankings = player_details.get("rankings", {})
            if rankings:
                st.subheader("🏆 ICC Rankings")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write("### Batting")
                    bat_rank = rankings.get("bat")
                    if isinstance(bat_rank, dict):
                        for k, v in bat_rank.items():
                            st.write(f"{k}: {v}")
                    else:
                        st.write("No rankings available")

                with col2:
                    st.write("### Bowling")
                    bowl_rank = rankings.get("bowl")
                    if isinstance(bowl_rank, dict):
                        for k, v in bowl_rank.items():
                            st.write(f"{k}: {v}")
                    else:
                        st.write("No rankings available")

                with col3:
                    st.write("### All-Rounder")
                    all_rank = rankings.get("all")
                    if isinstance(all_rank, dict):
                        for k, v in all_rank.items():
                            st.write(f"{k}: {v}")
                    else:
                        st.write("No rankings available")

            # Career Debut Info
            st.subheader("Career Debut Information")
            career_json = get_player_career(player_id)

            if career_json and career_json.get("values"):
                career_rows = []
                for f in career_json["values"]:
                    row_data = [f.get("name"), f.get("debut"), f.get("lastPlayed")]
                    career_rows.append(row_data)

                if career_rows:
                    career_df = pd.DataFrame(career_rows, columns=["Format", "Debut", "Last Played"])
                    st.dataframe(career_df, width="stretch")
                else:
                    st.warning("No career debut information available.")
            else:
                st.warning("No career debut information available.")

            # Link to Cricbuzz profile
            if player_details.get("webURL"):
                st.markdown(f"[🔗 View on Cricbuzz]({player_details['webURL']})")

    # ---------- BATTING STATS ----------
    with tabs[1]:
        st.subheader("Batting Stats")
        batting_stats = get_player_stats(player_id, "batting")
        df_bat = parse_stats_table(batting_stats)
        if not df_bat.empty:
            st.dataframe(df_bat, width="stretch")
        else:
            st.warning("No batting stats available.")

    # ---------- BOWLING STATS ----------
    with tabs[2]:
        st.subheader("Bowling Stats")
        bowling_stats = get_player_stats(player_id, "bowling")
        df_bowl = parse_stats_table(bowling_stats)
        if not df_bowl.empty:
            st.dataframe(df_bowl, width="stretch")
        else:
            st.warning("No bowling stats available.")


# For debugging standalone
if __name__ == "__main__":
    show_top_stats()
