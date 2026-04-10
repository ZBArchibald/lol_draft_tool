### 
# This module holds the functions for retrieving the list of challenger players from the Riot Games API,
#  as well as storing and updating it in the challenger_players table.
###

import sqlite3
import utils
import requests

API_KEY = utils.get_api_key()
REGION = "na1" 
MATCH_REGION = "americas"

# set the headers with the API key for authentication
headers = {"X-Riot-Token": API_KEY}

def get_challenger_puuids():
    # set the API endpoint for retrieving challenger league data
    url = f"https://{REGION}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"

    # make the API request to get the challenger league data and convert the JSON-string response to JSON
    response = requests.get(url, headers=headers)
    challenger_data = response.json()

    # retrieve the list of entries (players and their data).
    entries = challenger_data['entries']

    # retrieve each players puuid and add it to a list of puuids.
    puuids = []
    for entry in entries:
        puuids.append(entry['puuid']) 

    return puuids

def update_challenger_players_table():
    puuids = get_challenger_puuids()
    
    #connect to the database
    conn = sqlite3.connect("riot_data.db")
    c = conn.cursor() 
    ##what is a cursor in this context?

    #mark all players as not currently challenger
    c.execute("UPDATE challenger_players SET is_challenger = 0")

    #for each puuid in the updated list of challenger puuids, add them to the database (if they are not already there), and mark them as currently challenger
    for puuid in puuids:
        c.execute("""
            INSERT INTO challenger_players (puuid, is_challenger)
            VALUES (?, 1)
            ON CONFLICT(puuid) DO UPDATE SET is_challenger = 1
        """, (puuid,))
        ##don't understand this SQL statement.

    #commit changes to the database and close the connection.
    conn.commit()
    conn.close()

