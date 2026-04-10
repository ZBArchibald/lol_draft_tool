###This program sets up the database and should only be ran once when the application is initialized.

import sqlite3

conn = sqlite3.connect("data/riot_data.db")
c = conn.cursor()

# create the challenger_players table to store the player universally unique identitifiers (puuids) of challenger players, the last time their match data was retrieved, and whether or not they are currently challenger.
c.execute("""
CREATE TABLE IF NOT EXISTS challenger_players (
    puuid TEXT PRIMARY KEY,
    last_processed_match_retrieval_time TIMESTAMP,
    currently_challenger BOOLEAN DEFAULT 1
)
""")

# create the matches table to store the match ids of retrieved matches played by challenger players, the time they were retrieved, and whether or not they have been processed into the champion stats table.
c.execute("""
CREATE TABLE IF NOT EXISTS matches (
    match_id TEXT PRIMARY KEY,
    retrieved_at TIMESTAMP,
    processed BOOLEAN DEFAULT 0
)
""")

# create the champion_matchups table to store the champion ids of each champion and their opponent, the number of wins the champion has against its opponent, and the number of games the champion has played against its opponent.
c.execute("""
CREATE TABLE IF NOT EXISTS champion_matchups (
    champion_id INTEGER,
    opponent_id INTEGER,
    wins INTEGER DEFAULT 0,
    games INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()