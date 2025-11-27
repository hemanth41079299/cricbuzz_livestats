# data_ingest_players.py

import time
from typing import Dict, Any, List

from utils.api_handler import (
    get_teams_list,
    get_team_players,
    get_player_info,
)
from utils.db_connection import get_db_connection


# ---------- Generic extractors to handle different JSON shapes ----------

def extract_teams(teams_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Try multiple known shapes to pull out a flat list of team objects.
    Adjust this if you see a different structure when you print teams_data.
    """
    teams: List[Dict[str, Any]] = []

    if not isinstance(teams_data, dict):
        return teams

    # Case 1: simple { "teams": [ ... ] }
    if isinstance(teams_data.get("teams"), list):
        teams.extend(teams_data["teams"])

    # Case 2: { "teamTypes": [ { "teamType": "...", "teams": [ ... ] }, ... ] }
    if isinstance(teams_data.get("teamTypes"), list):
        for block in teams_data["teamTypes"]:
            if isinstance(block, dict) and isinstance(block.get("teams"), list):
                teams.extend(block["teams"])

    # Case 3: { "list": [ { "teams": [ ... ] }, ... ] }
    if isinstance(teams_data.get("list"), list):
        for block in teams_data["list"]:
            if isinstance(block, dict) and isinstance(block.get("teams"), list):
                teams.extend(block["teams"])

    return teams


def extract_players_from_team(team_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Try multiple shapes to pull a players list from team-players endpoint.
    """
    # Case 1: root "players"
    if isinstance(team_data.get("players"), list):
        return team_data["players"]

    # Case 2: { "squad": { "players": [ ... ] } }
    squad = team_data.get("squad")
    if isinstance(squad, dict) and isinstance(squad.get("players"), list):
        return squad["players"]

    # Case 3: { "player": [ ... ] }
    if isinstance(team_data.get("player"), list):
        return team_data["player"]

    return []


# ---------- Mapper & upsert -----------------------------------------------

def map_player_from_api(api_player: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map raw player JSON from Cricbuzz into the columns of our `players` table.

    IMPORTANT:
      - After first run, print a sample api_player and tweak key names below
        to match exactly what your API returns.
    """
    return {
        "player_id": api_player.get("id") or api_player.get("playerId"),
        "full_name": api_player.get("name") or api_player.get("fullName"),
        "country": api_player.get("country", "Unknown"),
        "playing_role": api_player.get("role") or api_player.get("playingRole"),
        "batting_style": api_player.get("battingStyle") or api_player.get("batStyle"),
        "bowling_style": api_player.get("bowlingStyle") or api_player.get("bowlStyle"),
        "date_of_birth": api_player.get("dob") or api_player.get("dateOfBirth"),
    }


def upsert_player(cur, player: Dict[str, Any]) -> None:
    sql = """
        INSERT INTO players (
            player_id,
            full_name,
            country,
            playing_role,
            batting_style,
            bowling_style,
            date_of_birth
        ) VALUES (
            %(player_id)s,
            %(full_name)s,
            %(country)s,
            %(playing_role)s,
            %(batting_style)s,
            %(bowling_style)s,
            %(date_of_birth)s
        )
        ON DUPLICATE KEY UPDATE
            full_name = VALUES(full_name),
            country = VALUES(country),
            playing_role = VALUES(playing_role),
            batting_style = VALUES(batting_style),
            bowling_style = VALUES(bowling_style),
            date_of_birth = VALUES(date_of_birth);
    """
    cur.execute(sql, player)


# ---------- Ingestion logic -----------------------------------------------

def ingest_players_for_team(team_id: int, team_name: str) -> int:
    print(f"\n=== Fetching players for team {team_name} (ID={team_id}) ===")
    team_data = get_team_players(team_id)

    players_list = extract_players_from_team(team_data)
    print(f"  → Found {len(players_list)} players in team API response")

    if not players_list:
        return 0

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    count = 0

    for p in players_list:
        pid = p.get("id") or p.get("playerId")
        if not pid:
            continue

        info = get_player_info(int(pid))

        # Many Cricbuzz endpoints wrap as {"playerInfo": {...}}
        if isinstance(info, dict) and "playerInfo" in info:
            info = info["playerInfo"]

        # Debug once for the first player of the first team:
        if count == 0:
            print("  Sample player raw info:")
            print({k: info.get(k) for k in list(info.keys())[:10]})

        player_row = map_player_from_api(info)
        if not player_row["player_id"]:
            continue

        upsert_player(cur, player_row)
        count += 1

        # Be gentle with the API
        time.sleep(0.3)

    conn.commit()
    cur.close()
    conn.close()

    print(f"  → Inserted/updated {count} players for {team_name}.")
    return count


def ingest_all_teams():
    teams_data = get_teams_list()
    teams = extract_teams(teams_data)

    print(f"Total teams detected in API response: {len(teams)}")
    if not teams:
        print("No teams found – please print teams_data and check its structure.")
        # Uncomment for debugging:
        # import json
        # print(json.dumps(teams_data, indent=2))
        return

    total_players = 0

    for t in teams:
        tid = t.get("id") or t.get("teamId")
        name = t.get("name") or t.get("teamName") or str(tid)
        if not tid:
            continue

        total_players += ingest_players_for_team(int(tid), name)
        time.sleep(0.5)

    print(f"\n✅ Done. Total players processed: {total_players}")


if __name__ == "__main__":
    ingest_all_teams()
