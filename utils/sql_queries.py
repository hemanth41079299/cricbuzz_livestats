# utils/sql_queries.py
#
# Contains 25 SQL queries mapped to the GUVI Cricbuzz LiveStats project questions.
# Levels: Beginner (1–8), Intermediate (9–16), Advanced (17–25).

SQL_QUERIES = [
    # ===================== BEGINNER (1–8) =====================

    {
        "id": "Q1",
        "level": "Beginner",
        "title": "Players from India with role and styles",
        "description": "Find all players who represent India. Show full name, playing role, batting style, and bowling style.",
        "sql": """
            SELECT
                full_name AS Player,
                playing_role AS Role,
                batting_style AS Batting_Style,
                bowling_style AS Bowling_Style
            FROM players
            WHERE country = 'India'
            ORDER BY full_name;
        """,
    },
    {
        "id": "Q2",
        "level": "Beginner",
        "title": "Recent matches with teams and venue",
        "description": "Show matches played in the last 7 days with match, both teams, venue, city and match date.",
        "sql": """
            SELECT
                m.match_id,
                s.series_name,
                m.match_format,
                m.match_date,
                m.match_desc AS Match_Desc,
                t1.team_name AS Team1,
                t2.team_name AS Team2,
                v.venue_name,
                v.city
            FROM matches m
            JOIN series s ON m.series_id = s.series_id
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            JOIN venues v ON m.venue_id = v.venue_id
            WHERE m.match_date >= (CURDATE() - INTERVAL 7 DAY)
            ORDER BY m.match_date DESC;
        """,
    },
    {
        "id": "Q3",
        "level": "Beginner",
        "title": "Top 10 ODI run scorers",
        "description": "List the top 10 highest run scorers in ODI cricket with total runs, batting average, and number of centuries.",
        "sql": """
            SELECT
                p.full_name AS Player,
                p.country AS Country,
                SUM(b.runs) AS Total_Runs,
                ROUND(AVG(b.runs), 2) AS Batting_Avg,
                SUM(CASE WHEN b.runs >= 100 THEN 1 ELSE 0 END) AS Centuries
            FROM player_match_batting b
            JOIN players p ON p.player_id = b.player_id
            JOIN matches m ON m.match_id = b.match_id
            WHERE m.match_format = 'ODI'
            GROUP BY b.player_id, p.full_name, p.country
            ORDER BY Total_Runs DESC
            LIMIT 10;
        """,
    },
    {
        "id": "Q4",
        "level": "Beginner",
        "title": "Venues with capacity > 30,000",
        "description": "Display all cricket venues that have a seating capacity of more than 30,000 spectators.",
        "sql": """
            SELECT
                venue_name,
                city,
                country,
                capacity
            FROM venues
            WHERE capacity > 30000
            ORDER BY capacity DESC;
        """,
    },
    {
        "id": "Q5",
        "level": "Beginner",
        "title": "Matches won by each team",
        "description": "Calculate how many matches each team has won.",
        "sql": """
            SELECT
                t.team_name AS Team,
                COUNT(*) AS Matches_Won
            FROM matches m
            JOIN teams t ON m.match_winner_team_id = t.team_id
            GROUP BY t.team_name
            ORDER BY Matches_Won DESC;
        """,
    },
    {
        "id": "Q6",
        "level": "Beginner",
        "title": "Players per playing role",
        "description": "Count how many players belong to each playing role.",
        "sql": """
            SELECT
                playing_role AS Role,
                COUNT(*) AS Player_Count
            FROM players
            GROUP BY playing_role
            ORDER BY Player_Count DESC;
        """,
    },
    {
        "id": "Q7",
        "level": "Beginner",
        "title": "Highest individual score by format",
        "description": "Find the highest individual batting score achieved in each cricket format.",
        "sql": """
            WITH ranked AS (
                SELECT
                    m.match_format AS Format,
                    p.full_name AS Player,
                    b.runs AS Runs,
                    ROW_NUMBER() OVER (
                        PARTITION BY m.match_format
                        ORDER BY b.runs DESC
                    ) AS rn
                FROM player_match_batting b
                JOIN matches m ON b.match_id = m.match_id
                JOIN players p ON b.player_id = p.player_id
            )
            SELECT
                Format,
                Player,
                Runs AS Highest_Score
            FROM ranked
            WHERE rn = 1
            ORDER BY Format;
        """,
    },
    {
        "id": "Q8",
        "level": "Beginner",
        "title": "Series started in 2024",
        "description": "Show all cricket series that started in the year 2024 with host country, match type, start date, and total planned matches.",
        "sql": """
            SELECT
                series_name,
                host_country,
                match_type,
                start_date,
                total_matches_planned
            FROM series
            WHERE YEAR(start_date) = 2024
            ORDER BY start_date;
        """,
    },

    # ===================== INTERMEDIATE (9–16) =====================

    {
        "id": "Q9",
        "level": "Intermediate",
        "title": "All-rounders with 1000+ runs and 50+ wickets (by format)",
        "description": "Find all-rounder players who have 1000+ runs AND 50+ wickets in the same format.",
        "sql": """
            WITH bat AS (
                SELECT
                    b.player_id,
                    m.match_format AS Format,
                    SUM(b.runs) AS total_runs
                FROM player_match_batting b
                JOIN matches m ON m.match_id = b.match_id
                GROUP BY b.player_id, m.match_format
            ),
            bowl AS (
                SELECT
                    w.player_id,
                    m.match_format AS Format,
                    SUM(w.wickets) AS total_wickets
                FROM player_match_bowling w
                JOIN matches m ON m.match_id = w.match_id
                GROUP BY w.player_id, m.match_format
            )
            SELECT
                p.full_name AS Player,
                p.country,
                b.Format,
                b.total_runs,
                w.total_wickets
            FROM bat b
            JOIN bowl w
                ON b.player_id = w.player_id
               AND b.Format = w.Format
            JOIN players p ON p.player_id = b.player_id
            WHERE b.total_runs > 1000
              AND w.total_wickets > 50
            ORDER BY b.total_runs DESC;
        """,
    },
    {
        "id": "Q10",
        "level": "Intermediate",
        "title": "Last 20 completed matches with result",
        "description": "Get details of the last 20 matches: match, teams, winner, victory margin & type, venue.",
        "sql": """
            SELECT
                m.match_id,
                s.series_name,
                m.match_format,
                m.match_date,
                t1.team_name AS Team1,
                t2.team_name AS Team2,
                tw.team_name AS Winner,
                m.result_margin,
                m.result_margin_type,
                v.venue_name,
                v.city
            FROM matches m
            JOIN series s ON m.series_id = s.series_id
            JOIN teams t1 ON m.team1_id = t1.team_id
            JOIN teams t2 ON m.team2_id = t2.team_id
            LEFT JOIN teams tw ON m.match_winner_team_id = tw.team_id
            JOIN venues v ON m.venue_id = v.venue_id
            ORDER BY m.match_date DESC
            LIMIT 20;
        """,
    },
    {
        "id": "Q11",
        "level": "Intermediate",
        "title": "Player performance across formats",
        "description": "For players with at least 2 formats, show total Test/ODI/T20I runs and overall average.",
        "sql": """
            WITH bat AS (
                SELECT
                    p.player_id,
                    p.full_name,
                    p.country,
                    SUM(CASE WHEN m.match_format = 'TEST' THEN b.runs ELSE 0 END) AS Test_Runs,
                    SUM(CASE WHEN m.match_format = 'ODI' THEN b.runs ELSE 0 END) AS ODI_Runs,
                    SUM(CASE WHEN m.match_format = 'T20I' THEN b.runs ELSE 0 END) AS T20I_Runs,
                    ROUND(AVG(b.runs), 2) AS Overall_Avg
                FROM player_match_batting b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                GROUP BY p.player_id, p.full_name, p.country
            )
            SELECT *
            FROM bat
            WHERE ( (Test_Runs > 0) + (ODI_Runs > 0) + (T20I_Runs > 0) ) >= 2
            ORDER BY Overall_Avg DESC;
        """,
    },
    {
        "id": "Q12",
        "level": "Intermediate",
        "title": "Team home vs away performance",
        "description": "Analyze each international team's wins when playing at home vs away.",
        "sql": """
            SELECT
                t.team_name AS Team,
                CASE WHEN v.country = t.country THEN 'Home' ELSE 'Away' END AS Home_Away,
                COUNT(*) AS Matches_Played,
                SUM(CASE WHEN m.match_winner_team_id = t.team_id THEN 1 ELSE 0 END) AS Matches_Won
            FROM matches m
            JOIN teams t
                ON t.team_id IN (m.team1_id, m.team2_id)
            JOIN venues v ON v.venue_id = m.venue_id
            GROUP BY t.team_name, Home_Away
            ORDER BY t.team_name, Home_Away;
        """,
    },
    {
        "id": "Q13",
        "level": "Intermediate",
        "title": "Big batting partnerships (100+ runs)",
        "description": "Find consecutive batting-position partnerships with combined runs >= 100 in same innings.",
        "sql": """
            SELECT
                i.match_id,
                i.innings_number AS Innings,
                p1.full_name AS Batter1,
                p2.full_name AS Batter2,
                (b1.runs + b2.runs) AS Partnership_Runs
            FROM player_match_batting b1
            JOIN player_match_batting b2
                ON b1.match_id = b2.match_id
               AND b1.innings_id = b2.innings_id
               AND b2.batting_position = b1.batting_position + 1
            JOIN innings i ON i.innings_id = b1.innings_id
            JOIN players p1 ON p1.player_id = b1.player_id
            JOIN players p2 ON p2.player_id = b2.player_id
            WHERE (b1.runs + b2.runs) >= 100
            ORDER BY Partnership_Runs DESC;
        """,
    },
    {
        "id": "Q14",
        "level": "Intermediate",
        "title": "Bowling performance by venue",
        "description": "For bowlers with >=3 matches at a venue and avg ≥4 overs/match, show wickets and economy.",
        "sql": """
            WITH bow_agg AS (
                SELECT
                    w.player_id,
                    v.venue_name,
                    COUNT(DISTINCT w.match_id) AS Matches_Played,
                    SUM(w.overs) AS Total_Overs,
                    SUM(w.runs_conceded) AS Runs_Conceded,
                    SUM(w.wickets) AS Total_Wickets
                FROM player_match_bowling w
                JOIN matches m ON m.match_id = w.match_id
                JOIN venues v ON v.venue_id = m.venue_id
                GROUP BY w.player_id, v.venue_name
            )
            SELECT
                p.full_name AS Bowler,
                bow_agg.venue_name,
                bow_agg.Matches_Played,
                bow_agg.Total_Wickets,
                ROUND(bow_agg.Runs_Conceded / NULLIF(bow_agg.Total_Overs, 0), 2) AS Avg_Economy
            FROM bow_agg
            JOIN players p ON p.player_id = bow_agg.player_id
            WHERE bow_agg.Matches_Played >= 3
              AND bow_agg.Total_Overs / bow_agg.Matches_Played >= 4
            ORDER BY Bowler, bow_agg.venue_name;
        """,
    },
    {
        "id": "Q15",
        "level": "Intermediate",
        "title": "Players in close matches",
        "description": "For close matches (margin <50 runs or <5 wickets), show players' avg runs and wins.",
        "sql": """
            WITH close_matches AS (
                SELECT match_id
                FROM matches
                WHERE is_close_match = 1
            ),
            player_match_result AS (
                SELECT
                    b.player_id,
                    b.match_id,
                    b.runs,
                    CASE WHEN m.match_winner_team_id = b.team_id THEN 1 ELSE 0 END AS Won
                FROM player_match_batting b
                JOIN matches m ON m.match_id = b.match_id
                JOIN close_matches cm ON cm.match_id = b.match_id
            )
            SELECT
                p.full_name AS Player,
                COUNT(DISTINCT pm.match_id) AS Close_Matches_Played,
                ROUND(AVG(pm.runs), 2) AS Avg_Runs_In_Close,
                SUM(pm.Won) AS Close_Matches_Won_While_Batting
            FROM player_match_result pm
            JOIN players p ON p.player_id = pm.player_id
            GROUP BY p.player_id, p.full_name
            ORDER BY Avg_Runs_In_Close DESC;
        """,
    },
    {
        "id": "Q16",
        "level": "Intermediate",
        "title": "Yearly batting performance since 2020",
        "description": "For matches since 2020, show each player's avg runs and strike rate per year (>=5 matches).",
        "sql": """
            WITH yearly AS (
                SELECT
                    p.player_id,
                    p.full_name,
                    YEAR(m.match_date) AS Year,
                    COUNT(DISTINCT m.match_id) AS Matches_Played,
                    ROUND(AVG(b.runs), 2) AS Avg_Runs,
                    ROUND(AVG(b.strike_rate), 2) AS Avg_SR
                FROM player_match_batting b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                WHERE m.match_date >= '2020-01-01'
                GROUP BY p.player_id, p.full_name, YEAR(m.match_date)
            )
            SELECT *
            FROM yearly
            WHERE Matches_Played >= 5
            ORDER BY Year DESC, full_name;
        """,
    },

    # ===================== ADVANCED (17–25) =====================

    {
        "id": "Q17",
        "level": "Advanced",
        "title": "Does winning the toss help?",
        "description": "Percentage of matches won by the toss-winning team, broken down by toss decision.",
        "sql": """
            SELECT
                toss_decision AS Toss_Decision,
                COUNT(*) AS Total_Matches,
                SUM(CASE WHEN toss_winner_team_id = match_winner_team_id THEN 1 ELSE 0 END) AS Toss_Winner_Wins,
                ROUND(
                    100.0 * SUM(CASE WHEN toss_winner_team_id = match_winner_team_id THEN 1 ELSE 0 END) / COUNT(*),
                    2
                ) AS Win_Percentage
            FROM matches
            WHERE toss_winner_team_id IS NOT NULL
              AND toss_decision IS NOT NULL
            GROUP BY toss_decision;
        """,
    },
    {
        "id": "Q18",
        "level": "Advanced",
        "title": "Most economical limited-overs bowlers",
        "description": "ODI & T20I bowlers with >=10 matches and >=2 overs/match; show wickets & economy.",
        "sql": """
            WITH bow AS (
                SELECT
                    w.player_id,
                    m.match_format,
                    COUNT(DISTINCT w.match_id) AS Matches_Played,
                    SUM(w.overs) AS Total_Overs,
                    SUM(w.runs_conceded) AS Runs_Conceded,
                    SUM(w.wickets) AS Total_Wickets
                FROM player_match_bowling w
                JOIN matches m ON m.match_id = w.match_id
                WHERE m.match_format IN ('ODI', 'T20I')
                GROUP BY w.player_id, m.match_format
            )
            SELECT
                p.full_name AS Bowler,
                p.country,
                bow.match_format AS Format,
                bow.Matches_Played,
                bow.Total_Wickets,
                ROUND(bow.Runs_Conceded / NULLIF(bow.Total_Overs, 0), 2) AS Economy
            FROM bow
            JOIN players p ON p.player_id = bow.player_id
            WHERE bow.Matches_Played >= 10
              AND bow.Total_Overs / bow.Matches_Played >= 2
            ORDER BY Format, Economy ASC, Total_Wickets DESC;
        """,
    },
    {
        "id": "Q19",
        "level": "Advanced",
        "title": "Consistent batsmen (low std dev)",
        "description": "Avg runs and stddev of runs since 2022 for players with >=5 innings and >=10 balls/inn.",
        "sql": """
            WITH stats AS (
                SELECT
                    p.player_id,
                    p.full_name,
                    p.country,
                    AVG(b.runs) AS Avg_Runs,
                    STDDEV_SAMP(b.runs) AS Runs_StdDev,
                    AVG(b.balls_faced) AS Avg_Balls,
                    COUNT(*) AS Innings
                FROM player_match_batting b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                WHERE m.match_date >= '2022-01-01'
                GROUP BY p.player_id, p.full_name, p.country
            )
            SELECT *
            FROM stats
            WHERE Innings >= 5
              AND Avg_Balls >= 10
            ORDER BY Runs_StdDev ASC;
        """,
    },
    {
        "id": "Q20",
        "level": "Advanced",
        "title": "Matches & batting average by format",
        "description": "For players with >=20 total matches, show match counts and batting average per format.",
        "sql": """
            WITH fmt AS (
                SELECT
                    p.player_id,
                    p.full_name,
                    m.match_format,
                    COUNT(DISTINCT m.match_id) AS Matches_Played,
                    ROUND(AVG(b.runs), 2) AS Batting_Avg
                FROM player_match_batting b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                GROUP BY p.player_id, p.full_name, m.match_format
            ),
            tot AS (
                SELECT
                    player_id,
                    SUM(Matches_Played) AS Total_Matches
                FROM fmt
                GROUP BY player_id
            )
            SELECT
                f.full_name AS Player,
                f.match_format AS Format,
                f.Matches_Played,
                f.Batting_Avg
            FROM fmt f
            JOIN tot t ON t.player_id = f.player_id
            WHERE t.Total_Matches >= 20
            ORDER BY Player, Format;
        """,
    },
    {
        "id": "Q21",
        "level": "Advanced",
        "title": "Composite player performance ranking",
        "description": "Combine batting, bowling, and fielding into a single weighted score and rank players.",
        "sql": """
            WITH bat AS (
                SELECT
                    p.player_id,
                    m.match_format AS Format,
                    SUM(b.runs) AS runs_scored,
                    AVG(b.runs) AS batting_average,
                    AVG(b.strike_rate) AS strike_rate
                FROM player_match_batting b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                GROUP BY p.player_id, m.match_format
            ),
            bowl AS (
                SELECT
                    p.player_id,
                    m.match_format AS Format,
                    SUM(w.wickets) AS wickets_taken,
                    CASE WHEN SUM(w.wickets) > 0
                         THEN SUM(w.runs_conceded) / SUM(w.wickets)
                         ELSE NULL
                    END AS bowling_average,
                    CASE WHEN SUM(w.overs) > 0
                         THEN SUM(w.runs_conceded) / SUM(w.overs)
                         ELSE NULL
                    END AS economy_rate
                FROM player_match_bowling w
                JOIN players p ON p.player_id = w.player_id
                JOIN matches m ON m.match_id = w.match_id
                GROUP BY p.player_id, m.match_format
            ),
            field AS (
                SELECT
                    p.player_id,
                    SUM(f.catches) AS catches,
                    SUM(f.stumpings) AS stumpings
                FROM player_match_fielding f
                JOIN players p ON p.player_id = f.player_id
                GROUP BY p.player_id
            )
            SELECT
                p.full_name AS Player,
                p.country,
                COALESCE(bat.Format, bowl.Format) AS Format,
                bat.runs_scored,
                bat.batting_average,
                bat.strike_rate,
                bowl.wickets_taken,
                bowl.bowling_average,
                bowl.economy_rate,
                field.catches,
                field.stumpings,
                (
                    COALESCE(bat.runs_scored, 0) * 0.01
                    + COALESCE(bat.batting_average, 0) * 0.5
                    + COALESCE(bat.strike_rate, 0) * 0.3
                ) AS Batting_Points,
                (
                    COALESCE(bowl.wickets_taken, 0) * 2
                    + (50 - COALESCE(bowl.bowling_average, 50)) * 0.5
                    + ((6 - COALESCE(bowl.economy_rate, 6)) * 2)
                ) AS Bowling_Points,
                (
                    COALESCE(
                        COALESCE(bat.runs_scored, 0) * 0.01
                        + COALESCE(bat.batting_average, 0) * 0.5
                        + COALESCE(bat.strike_rate, 0) * 0.3,
                        0
                    )
                    +
                    COALESCE(
                        COALESCE(bowl.wickets_taken, 0) * 2
                        + (50 - COALESCE(bowl.bowling_average, 50)) * 0.5
                        + ((6 - COALESCE(bowl.economy_rate, 6)) * 2),
                        0
                    )
                    +
                    (COALESCE(field.catches, 0) + COALESCE(field.stumpings, 0))
                ) AS Total_Score
            FROM players p
            LEFT JOIN bat ON bat.player_id = p.player_id
            LEFT JOIN bowl ON bowl.player_id = p.player_id
            LEFT JOIN field ON field.player_id = p.player_id
            WHERE COALESCE(bat.runs_scored, 0) > 0
               OR COALESCE(bowl.wickets_taken, 0) > 0
            ORDER BY Total_Score DESC;
        """,
    },
    {
        "id": "Q22",
        "level": "Advanced",
        "title": "Head-to-head team records (last 3 years)",
        "description": "For team pairs with >=5 matches in last 3 years, show matches, wins, and win percentages.",
        "sql": """
            WITH h2h AS (
                SELECT
                    LEAST(m.team1_id, m.team2_id) AS Team_A_Id,
                    GREATEST(m.team1_id, m.team2_id) AS Team_B_Id,
                    m.match_id,
                    m.match_winner_team_id,
                    m.result_margin,
                    m.match_date
                FROM matches m
                WHERE m.match_date >= (CURDATE() - INTERVAL 3 YEAR)
            ),
            agg AS (
                SELECT
                    Team_A_Id,
                    Team_B_Id,
                    COUNT(*) AS Matches_Played,
                    SUM(CASE WHEN match_winner_team_id = Team_A_Id THEN 1 ELSE 0 END) AS Team_A_Wins,
                    SUM(CASE WHEN match_winner_team_id = Team_B_Id THEN 1 ELSE 0 END) AS Team_B_Wins,
                    AVG(CASE WHEN match_winner_team_id = Team_A_Id THEN result_margin END) AS Avg_Margin_Team_A,
                    AVG(CASE WHEN match_winner_team_id = Team_B_Id THEN result_margin END) AS Avg_Margin_Team_B
                FROM h2h
                GROUP BY Team_A_Id, Team_B_Id
            )
            SELECT
                ta.team_name AS Team_A,
                tb.team_name AS Team_B,
                agg.Matches_Played,
                agg.Team_A_Wins,
                agg.Team_B_Wins,
                ROUND(100.0 * agg.Team_A_Wins / agg.Matches_Played, 2) AS Team_A_Win_Perc,
                ROUND(100.0 * agg.Team_B_Wins / agg.Matches_Played, 2) AS Team_B_Win_Perc,
                agg.Avg_Margin_Team_A,
                agg.Avg_Margin_Team_B
            FROM agg
            JOIN teams ta ON ta.team_id = agg.Team_A_Id
            JOIN teams tb ON tb.team_id = agg.Team_B_Id
            WHERE agg.Matches_Played >= 5
            ORDER BY agg.Matches_Played DESC;
        """,
    },
    {
        "id": "Q23",
        "level": "Advanced",
        "title": "Recent form and momentum (last 10 innings)",
        "description": "For each player, compare last 5 vs last 10 innings and categorize form.",
        "sql": """
            WITH ranked AS (
                SELECT
                    b.player_id,
                    p.full_name,
                    m.match_date,
                    b.runs,
                    b.strike_rate,
                    ROW_NUMBER() OVER (
                        PARTITION BY b.player_id
                        ORDER BY m.match_date DESC
                    ) AS rn
                FROM player_match_batting b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
            ),
            last10 AS (
                SELECT * FROM ranked WHERE rn <= 10
            ),
            last5 AS (
                SELECT * FROM ranked WHERE rn <= 5
            ),
            agg10 AS (
                SELECT
                    player_id,
                    AVG(runs) AS Avg_Last10_Runs,
                    AVG(strike_rate) AS Avg_Last10_SR,
                    SUM(CASE WHEN runs >= 50 THEN 1 ELSE 0 END) AS Fifties_Last10,
                    STDDEV_SAMP(runs) AS StdDev_Last10
                FROM last10
                GROUP BY player_id
            ),
            agg5 AS (
                SELECT
                    player_id,
                    AVG(runs) AS Avg_Last5_Runs
                FROM last5
                GROUP BY player_id
            )
            SELECT
                p.full_name AS Player,
                COALESCE(a5.Avg_Last5_Runs, 0) AS Avg_Last5_Runs,
                COALESCE(a10.Avg_Last10_Runs, 0) AS Avg_Last10_Runs,
                COALESCE(a10.Avg_Last10_SR, 0) AS Avg_Last10_SR,
                COALESCE(a10.Fifties_Last10, 0) AS Fifties_Last10,
                COALESCE(a10.StdDev_Last10, 0) AS Runs_StdDev,
                CASE
                    WHEN a10.Avg_Last10_Runs >= 60 AND a10.StdDev_Last10 <= 15 THEN 'Excellent Form'
                    WHEN a10.Avg_Last10_Runs >= 40 THEN 'Good Form'
                    WHEN a10.Avg_Last10_Runs >= 25 THEN 'Average Form'
                    ELSE 'Poor Form'
                END AS Form_Category
            FROM agg10 a10
            JOIN players p ON p.player_id = a10.player_id
            LEFT JOIN agg5 a5 ON a5.player_id = a10.player_id;
        """,
    },
    {
        "id": "Q24",
        "level": "Advanced",
        "title": "Best batting partnerships",
        "description": "For pairs of consecutive batsmen with >=5 partnerships, show avg, 50+ counts, and success rate.",
        "sql": """
            WITH partner_innings AS (
                SELECT
                    b1.player_id AS player1_id,
                    b2.player_id AS player2_id,
                    b1.match_id,
                    b1.innings_id,
                    (b1.runs + b2.runs) AS Partnership_Runs
                FROM player_match_batting b1
                JOIN player_match_batting b2
                    ON b1.match_id = b2.match_id
                   AND b1.innings_id = b2.innings_id
                   AND b2.batting_position = b1.batting_position + 1
            ),
            norm AS (
                SELECT
                    LEAST(player1_id, player2_id) AS p1,
                    GREATEST(player1_id, player2_id) AS p2,
                    match_id,
                    innings_id,
                    Partnership_Runs
                FROM partner_innings
            ),
            agg AS (
                SELECT
                    p1,
                    p2,
                    COUNT(*) AS Partnerships_Played,
                    AVG(Partnership_Runs) AS Avg_Partnership,
                    SUM(CASE WHEN Partnership_Runs >= 50 THEN 1 ELSE 0 END) AS FiftyPlus_Count,
                    MAX(Partnership_Runs) AS Highest_Partnership
                FROM norm
                GROUP BY p1, p2
            )
            SELECT
                pA.full_name AS Player1,
                pB.full_name AS Player2,
                Partnerships_Played,
                ROUND(Avg_Partnership, 2) AS Avg_Partnership,
                FiftyPlus_Count,
                Highest_Partnership,
                ROUND(100.0 * FiftyPlus_Count / Partnerships_Played, 2) AS Success_Rate_Percent
            FROM agg
            JOIN players pA ON pA.player_id = agg.p1
            JOIN players pB ON pB.player_id = agg.p2
            WHERE Partnerships_Played >= 5
            ORDER BY Avg_Partnership DESC;
        """,
    },
    {
        "id": "Q25",
        "level": "Advanced",
        "title": "Quarterly time-series of batting performance",
        "description": "Track each player's quarterly avg runs & SR; show players with >=6 quarters of data.",
        "sql": """
            WITH per_quarter AS (
                SELECT
                    p.player_id,
                    p.full_name,
                    YEAR(m.match_date) AS Year,
                    QUARTER(m.match_date) AS Quarter,
                    CONCAT(YEAR(m.match_date), '-Q', QUARTER(m.match_date)) AS Year_Quarter,
                    COUNT(DISTINCT m.match_id) AS Matches_Played,
                    AVG(b.runs) AS Avg_Runs,
                    AVG(b.strike_rate) AS Avg_SR
                FROM player_match_batting b
                JOIN players p ON p.player_id = b.player_id
                JOIN matches m ON m.match_id = b.match_id
                GROUP BY p.player_id, p.full_name, Year, Quarter
            ),
            filtered AS (
                SELECT *
                FROM per_quarter
                WHERE Matches_Played >= 3
            ),
            span AS (
                SELECT
                    player_id,
                    COUNT(*) AS Quarters_Count
                FROM filtered
                GROUP BY player_id
            )
            SELECT
                f.player_id,
                f.full_name AS Player,
                f.Year_Quarter,
                f.Matches_Played,
                ROUND(f.Avg_Runs, 2) AS Avg_Runs,
                ROUND(f.Avg_SR, 2) AS Avg_SR
            FROM filtered f
            JOIN span s ON s.player_id = f.player_id
            WHERE s.Quarters_Count >= 6
            ORDER BY f.full_name, f.Year, f.Quarter;
        """,
    },
]
