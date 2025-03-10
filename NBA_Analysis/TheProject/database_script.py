import sqlite3
import pandas as pd
from datetime import datetime, date

DB_NAME = 'player_data.db'
DB_PATH = "Data/DATABASE"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def setup_database():
    conn = connect_db()
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS PLAYER_REGISTRY (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PLAYER_NAME TEXT NOT NULL,
            LAST_UPDATED DATE NOT NULL,
            UNIQUE(player_name)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS PLAYER_STATS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PLAYER_ID INTEGER NOT NULL,
            DATE TEXT NOT NULL,
            LOCATION TEXT,
            OPPONENT TEXT,
            FG INTEGER,
            FGA INTEGER,
            FG_PERCENT REAL,
            3P INTEGER,
            3PA INTEGER,
            3P_PERCENT REAL,
            FT INTEGER,
            FTA INTEGER,
            FT_PERCENT REAL,
            ORB INTEGER,
            DRB INTEGER,
            TRB INTEGER,
            AST INTEGER,
            STL INTEGER,
            BLK INTEGER,
            TOV INTEGER,
            PTS INTEGER,
            FOREIGN KEY (player_id) REFERENCES player_registry(id),
            UNIQUE(player_id, DATE)
        )
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_player_stats_player_id ON player_stats(player_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_player_stats_game_date ON player_stats(game_date)")

        conn.commit()
    except Exception as e:
        print(f'Error setting up database: {e}')
        conn.rollback()
    finally:
        conn.close()


def save_to_db(df: pd.DataFrame, player_name: str, year: int = 2025) -> bool:
    """Saves the player DataFrame to the database.
    Args:
        df: DataFrame containing player game data
        player_name: Name of the player
        year: Year/season of the data
    Returns:
        bool: True if successful, False otherwise
    """
    if df is None or df.empty:
        print(f"No data provided for {player_name} ({year})")
        return False

    today = date.today().isoformat()

    try:
        setup_database()
        conn = connect_db()

        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO PLAYER_REGISTRY WHERE PLAYER_NAME (player_name, last_updated", (player_name,))
        )

        
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

def fetch_player_data(player_name, year):
    """Fetches player data from the database as a DataFrame."""
    table_name = f"{player_name.replace(' ', '_')}_{year}"
    
    conn = connect_db()
    query = f"SELECT * FROM {table_name}"
    
    try:
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"Error fetching data for {player_name}: {e}")
        df = None
    
    conn.close()
    return df
    