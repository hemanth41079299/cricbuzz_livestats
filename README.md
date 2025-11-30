🏏 Cricbuzz LiveStats
Real-Time Cricket Dashboard • MySQL Analytics • Streamlit Web App

Cricbuzz LiveStats is a real-time cricket analytics platform built using Streamlit, powered by the Cricbuzz API (via RapidAPI) and backed by a MySQL database.

This project pulls:

Live match details

Full scorecards

Player stats

Aggregated batting/bowling data

Series-wise match data

… and gives you a beautiful UI + SQL-based analytics engine.

🌟 Features
⚡ 1. Live Match Dashboard

Live matches with score updates

Venue, match status, format, timing

Full scorecards: batting + bowling breakdown

Multi-series selector

Robust JSON-structure-aware parsing

📊 2. Player Stats & Profile Explorer

Search global players

Player image, team, DOB, role, styles

ICC rankings

Career debut + last played (Tests/ODI/T20)

Full batting table

Full bowling table

🔍 3. SQL Analytics Engine (25+ Queries)

Pre-built analytics queries:

Top run scorers

Venue capacity ranking

Toss decision vs match outcome

All-rounder stats

Player consistency metrics

Yearly trends

Format comparison

Head-to-head analysis

Also includes:

Fully editable SQL editor

Live MySQL execution

Results displayed as DataFrame

🛠️ 4. Full CRUD Operations UI

Insert

Update

Delete

View table

SELECT queries

Automatic table/column metadata detection

Reads schema dynamically from MySQL

🧱 5. Complete Data Pipeline

Your notebook (data_fetch.ipynb) fetches:

Recent matches

Player summaries

Series matches

Top ODI run scorers

Players’ multi-format stats

Combined match metadata

Batting data (from scorecards)

Bowling data (from scorecards)

Batters’ match-wise performance

Bowlers’ venue-based performance

Every section automatically:

Creates SQL table

Inserts/Upserts cleaned data


cricbuzz_livestats-main/
│
├── app.py                           # Main Streamlit home page 
│
├── pages/
│   ├── live_matches.py              # Live match dashboard + scorecards
│   ├── top_stats.py                 # Player profiles + stats explorer
│   ├── sql_queries.py               # Analytics SQL engine (25+ queries)
│   └── crud_operations.py           # Full CRUD system
│
├── utils/
│   ├── api_client.py                # Centralized API client + error handler
│   └── db_connection.py             # All MySQL operations & schema explorer
│
├── notebooks/
│   └── data_fetch.ipynb             # Huge ETL script: fetch → clean → load → MySQL
│
├── assets/                          # Images, icons, logos
├── .env                             # Environment variables (NOT committed)
├── .gitignore                       # Ignore env, cache, IDE files
├── requirements.txt                 # Dependencies
└── README.md


🗄️ Database Schema (Automatically Created)

Your notebook creates all tables dynamically:

Core Tables

players

players_stats

top_odi_runs

venues

combined_matches

series_matches

recent_matches

Batting / Bowling Tables

batting_data

bowling_data

batters_batting_data

bowlers_bowling_venue_data

All tables use:

Proper data types

Correct primary keys

REPLACE INTO → “Upsert” to avoid duplicates


RAPIDAPI_KEY=your_key
RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com

DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=cricbuzz_db


💻 Installation
1️⃣ Clone the repository

git clone https://github.com/hemanth41079299/cricbuzz_livestats.git
cd cricbuzz_livestats

2️⃣ Setup virtual environment
python -m venv env
source env/bin/activate    # macOS/Linux
env\Scripts\activate       # Windows


3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Start MySQL and create DB
CREATE DATABASE cricbuzz_db;


5️⃣ Run ETL (optional)

Open Jupyter → run data_fetch.ipynb

6️⃣ Run the Streamlit app

streamlit run app.py

Go to:
👉 http://localhost:8501 

🧠 How the Code Works
Central API Client

utils/api_client.py

Handles headers

Handles CricbuzzAPIError

Wraps all endpoints

Ensures stable responses

Database Layer

utils/db_connection.py

Schema detection

Fetch/select

Insert/update/delete

Fully parameterized queries

UI Pages

Each page is self-contained and follows the same style:

Beautiful custom CSS

Clean layout

Efficient API calls

Error handling

🚀 Roadmap / Future Improvements

Dockerize app

Add charts (runs timeline, strike-rate distribution)

Add match prediction ML model

Add player comparison tool

Add caching layer (Redis)

Add user login (JWT + SQLite)

👨‍💻 Author

Hemanth Kumar
Real-time dashboard & analytics developer
GitHub: https://github.com/hemanth41079299/cricbuzz_livestats 
