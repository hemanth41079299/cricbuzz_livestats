import streamlit as st
import sys
import os

# Page configuration
st.set_page_config(
    page_title="🏏 Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for a beautiful, modern theme ---
st.markdown(
    """
<style>
    /* App background - soft cream */
    .stApp {
        background-color: #fffaf0;  /* Floral White */
        color: #333333;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Main header with a rich maroon-gold gradient */
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #800000, #B22222); /* DarkRed to FireBrick */
        color: #FFD700; /* Gold text */
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.25);
        margin-bottom: 2rem;
        font-family: 'Georgia', serif;
    }

    /* Feature Cards - white with golden icon & subtle shadow */
    .feature-card {
        background: #fff;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: #FFD700; /* Gold accent */
    }

    /* Metric Cards - white with gold metric */
    .metric-card {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        padding: 1rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #B8860B; /* Dark Goldenrod */
    }
    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
    }

    /* Buttons styling - maroon to red gradient with gold text */
    div.stButton > button {
        background: linear-gradient(135deg, #B22222, #800000); /* FireBrick to DarkRed */
        color: #FFD700; /* Gold text */
        border: none;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: background 0.3s, transform 0.2s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #800000, #B22222); /* reverse gradient on hover */
        transform: translateY(-2px);
        color: #FFF8DC; /* lighter gold on hover */
    }

    /* Sidebar styling - match app background */
    .css-1d391kg {
        background-color: #fffaf0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Add current directory to path so local modules can be imported if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def show_home():
    st.markdown(
        """
    <div class="main-header">
        <h1>🏏 Cricbuzz LiveStats</h1>
        <p>Real-Time Cricket Insights & SQL-Based Analytics</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Feature cards section
    st.subheader("✨ Explore the Dashboard's Key Features")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon">⚡</div>'
            '<h4>Live Matches</h4><p>Real-time scores, updates, and match details.</p></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon">📊</div>'
            '<h4>Top Stats</h4><p>Leaderboards for top batsmen and bowlers.</p></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon">🔍</div>'
            '<h4>SQL Analytics</h4><p>Run advanced SQL queries for deep insights.</p></div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            '<div class="feature-card"><div class="feature-icon">🛠️</div>'
            '<h4>CRUD Operations</h4><p>Add, update, and manage your own cricket data.</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # System Architecture Section
    st.subheader("🖼️ System Architecture at a Glance")

    with st.expander("🔌 API Integration (Cricbuzz → Python)"):
        st.code(
            """
from utils.api_client import get_live_matches

# Fetch live match data from Cricbuzz via RapidAPI
live_data = get_live_matches()

# Example: print match IDs and team short names
for match in live_data.get("matches", []):
    info = match.get("matchInfo", {})
    team1 = info.get("team1", {}).get("teamSName")
    team2 = info.get("team2", {}).get("teamSName")
    print(info.get("matchId"), team1, "vs", team2)
        """,
            language="python",
        )

    with st.expander("🗄️ Database Schema (Core Tables)"):
        st.code(
            """
CREATE TABLE players (
    player_id INT PRIMARY KEY,
    full_name VARCHAR(100),
    team_id INT,
    role VARCHAR(50),
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50)
);

CREATE TABLE matches (
    match_id INT PRIMARY KEY,
    series_id INT,
    series_name VARCHAR(200),
    match_desc VARCHAR(50),
    format VARCHAR(10),
    start_date DATETIME,
    end_date DATETIME,
    venue_id INT,
    team1_id INT,
    team2_id INT,
    winner_team_id INT,
    status VARCHAR(50)
);
        """,
            language="sql",
        )

    with st.expander("📂 Project Structure (High Level)"):
        st.code(
            """
cricbuzz_livestats/
├── app.py                  # Main Streamlit app (this file)
├── utils/
│   ├── api_client.py       # Cricbuzz API wrapper (Python extraction layer)
│   ├── db_connection.py    # Database connection helpers
│   └── db_schema.py        # Table creation scripts
├── pages/
│   ├── live_matches.py     # ⚡ Live Matches page
│   ├── top_stats.py        # 📊 Top Player Stats page
│   ├── sql_queries.py      # 🔍 SQL Analytics (25+ SQL queries)
│   └── crud_operations.py  # 🛠️ CRUD operations on DB
└── notebooks/
    └── 01_api_experiments.ipynb  # Jupyter experiments with API & data
        """,
            language="text",
        )

    st.markdown("---")

    # Project Statistics
    st.subheader("📊 Project Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            '<div class="metric-card"><div class="metric-value">12</div>'
            '<div class="metric-label">📁 Total Project Files</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<div class="metric-card"><div class="metric-value">7</div>'
            '<div class="metric-label">🐍 Python Libraries Used</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="metric-card"><div class="metric-value">25</div>'
            '<div class="metric-label">🔍 Planned SQL Analytics Queries</div></div>',
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            '<div class="metric-card"><div class="metric-value">14</div>'
            '<div class="metric-label">🗄️ Database Tables (Target)</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # About section – shows clearly it's your project
    st.subheader("👨‍💻 About This Project")
    st.markdown(
        """
**Cricbuzz LiveStats** is a personal learning project by **Hemanth Kumar**.

- **Goal:** Build a real-time cricket dashboard with proper API handling and SQL-based analytics  
- **Stack:** Python, Streamlit, SQL, Cricbuzz API (via RapidAPI)  
- **Flow:** Cricbuzz API ➝ Python extraction ➝ SQL database ➝ Streamlit pages  

Use the page tabs (top) to explore:
- ⚡ Live Matches – real-time match data  
- 📊 Top Stats – batting & bowling leaderboards  
- 🔍 SQL Analytics – advanced queries on the cricket database  
- 🛠️ CRUD Operations – full Create/Read/Update/Delete on match & player data  
"""
    )

def main():
    # Simple sidebar branding only – no extra navigation
    with st.sidebar:
        st.markdown("### 🏏 Cricbuzz LiveStats")
        st.caption("Real-time cricket insights & SQL analytics")

    show_home()

if __name__ == "__main__":
    main()
