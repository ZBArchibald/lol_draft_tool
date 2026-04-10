import sqlite3

conn = sqlite3.connect("database/riot_data.db")
c = conn.cursor()


c.execute("""
CREATE TABLE IF NOT EXISTS challenger_players (
    puuid TEXT PRIMARY KEY,
    last_processed_match_retrieval_time TIMESTAMP,
    currently_challenger BOOLEAN DEFAULT 1
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS matches (
    match_id TEXT PRIMARY KEY,
    retrieved_at TIMESTAMP,
    processed BOOLEAN DEFAULT 0
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS champion_stats (
    champion_id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()