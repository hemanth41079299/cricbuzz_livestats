import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CRICBUZZ_BASE_URL", "https://cricbuzz-cricket.p.rapidapi.com")
API_KEY = os.getenv("CRICBUZZ_API_KEY")
API_HOST = os.getenv("CRICBUZZ_HOST", "cricbuzz-cricket.p.rapidapi.com")


def _get_headers() -> Dict[str, str]:
    """
    Common headers for all Cricbuzz API calls.
    API key is read from the .env file.
    """
    if not API_KEY:
        raise RuntimeError("CRICBUZZ_API_KEY is not set in .env")

    return {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST,
    }


def call_cricbuzz_api(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generic helper to call Cricbuzz endpoints.

    Examples of paths:
      - 'matches/v1/live'
      - 'mcenter/v1/{matchId}/hscard'
      - 'series/v1/international'
    """
    url = f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    headers = _get_headers()

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Cricbuzz API error for {path}: {e}")
        return {}


# =========================================================
#  WRAPPER FUNCTIONS
# =========================================================

def get_live_matches() -> Dict[str, Any]:
    """
    Wrapper for the live matches endpoint.
    This path is known to work on your key.
    """
    return call_cricbuzz_api("matches/v1/live")


def get_match_scorecard(match_id: int) -> Dict[str, Any]:
    """
    Wrapper for the scorecard endpoint.

    Based on your working example:
      https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/40381/hscard

    So the pattern is:
      mcenter/v1/{matchId}/hscard
    """
    path = f"mcenter/v1/{match_id}/hscard"
    return call_cricbuzz_api(path)


def get_series_list() -> Dict[str, Any]:
    """
    Wrapper for listing international series.
    Adjust if your RapidAPI docs show a different path.
    """
    return call_cricbuzz_api("series/v1/international")


def get_series_matches(series_id: int) -> Dict[str, Any]:
    """
    Wrapper for 'series/get-matches' style endpoint.
    Path may need adjustment based on actual docs.
    """
    return call_cricbuzz_api("series/v1/get-matches", params={"seriesId": series_id})


def get_teams_list() -> Dict[str, Any]:
    """
    Wrapper for listing international teams.
    Adjust path according to actual RapidAPI documentation.
    """
    return call_cricbuzz_api("teams/v1/international")


def get_team_players(team_id: int) -> Dict[str, Any]:
    """
    Wrapper for fetching players in a team.
    Path may need adjustment according to docs.
    """
    return call_cricbuzz_api("teams/v1/team-players", params={"teamId": team_id})


def get_player_info(player_id: int) -> Dict[str, Any]:
    """
    Wrapper for detailed player info.
    """
    return call_cricbuzz_api("players/v1/player-info", params={"playerId": player_id})


def get_stats_records(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper for stats/get-records – currently not used in the app,
    and this endpoint may not be available on your plan.

    Kept here for future extension if needed.
    """
    return call_cricbuzz_api("stats/v1/records", params=params)
