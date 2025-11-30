# utils/api_client.py

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"


class CricbuzzAPIError(RuntimeError):
    """Custom exception for Cricbuzz API errors."""
    pass


def _get_headers() -> Dict[str, str]:
    """
    Build RapidAPI headers from environment variables.
    Expects:
      RAPIDAPI_KEY
      RAPIDAPI_HOST
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    api_host = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")

    if not api_key:
        raise CricbuzzAPIError(
            "RAPIDAPI_KEY not found in environment variables. "
            "Create a .env file in your project root with:\n"
            "RAPIDAPI_KEY=<your_key>\n"
            "RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com"
        )

    return {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
    }


def _request(
    path: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Low-level helper to call a Cricbuzz endpoint.

    :param path: API path, e.g. '/matches/v1/live'
    :param params: Optional query parameters
    :param timeout: Timeout in seconds
    :return: Parsed JSON response as dict
    :raises CricbuzzAPIError: for network / HTTP issues
    """
    url = f"{BASE_URL}{path}"
    headers = _get_headers()

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
    except requests.exceptions.RequestException as e:
        raise CricbuzzAPIError(f"Network error calling Cricbuzz API: {e}") from e

    if resp.status_code != 200:
        # Try to include any error message from the response body
        try:
            body = resp.json()
        except Exception:
            body = resp.text

        raise CricbuzzAPIError(
            f"Cricbuzz API returned HTTP {resp.status_code} for {path}. "
            f"Response: {body}"
        )

    try:
        return resp.json()
    except ValueError as e:
        raise CricbuzzAPIError(f"Failed to parse JSON from Cricbuzz API: {e}") from e


# -----------------------------------------------------------------------------
# Public helper functions for specific endpoints
# -----------------------------------------------------------------------------


def get_international_series() -> Dict[str, Any]:
    """
    Fetch list of international series.

    Endpoint example from RapidAPI:
      GET /series/v1/international
    """
    return _request("/series/v1/international")


def get_live_matches() -> Dict[str, Any]:
    """
    Fetch all current live matches.

    Endpoint example from RapidAPI:
      GET /matches/v1/live
    """
    return _request("/matches/v1/live")


def get_match_scorecard(match_id: str | int) -> Dict[str, Any]:
    """
    Fetch detailed scorecard / match center info for a specific match.

    :param match_id: Cricbuzz matchId (int or str)
    Endpoint example from RapidAPI:
      GET /mcenter/v1/{match_id}
    """
    path = f"/mcenter/v1/{match_id}"
    return _request(path)


def get_series_matches(series_id: str | int) -> Dict[str, Any]:
    """
    Fetch matches for a specific series, if you decide to use it later.

    Endpoint example (may vary based on RapidAPI docs):
      GET /series/v1/{series_id}
    """
    path = f"/series/v1/{series_id}"
    return _request(path)


# -----------------------------------------------------------------------------
# Simple manual test when running this file directly
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    # Basic smoke tests – useful when running:
    #   python -m utils.api_client
    try:
        print("Testing get_live_matches() ...")
        live = get_live_matches()
        matches = live.get("matches", [])
        print(f"Found {len(matches)} live match entries")

        if matches:
            first = matches[0].get("matchInfo", {})
            print("Example matchId:", first.get("matchId"))
            print("Teams:", first.get("team1", {}).get("teamSName"),
                  "vs",
                  first.get("team2", {}).get("teamSName"))
    except CricbuzzAPIError as e:
        print("CricbuzzAPIError:", e)
