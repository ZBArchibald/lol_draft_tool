### 
# This module holds the functions for retrieving the list of challenger players from the Riot Games API,
#  as well as storing and updating it in the challenger_players table.
###

import sqlite3
from urllib import response
import requests
from config import API_KEY, REGION, DB_PATH ####this is probably not the right way to do this

def get_challenger_puuids():
    # set the API endpoint for retrieving challenger league data
    url = f"https://{REGION}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"

    # set the headers with the API key for authentication
    headers = {"X-Riot-Token": API_KEY}

    # make the API request to get the challenger league data and convert the JSON-string response to JSON
    response = requests.get(url, headers=headers)
    print(response.status_code)
    print(response.text)
    
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor() 
    ##what is a cursor in this context?

    #mark all players as not currently challenger
    c.execute("UPDATE challenger_players SET currently_challenger = 0")

    #for each puuid in the updated list of challenger puuids, add them to the database (if they are not already there), and mark them as currently challenger
    for puuid in puuids:
        c.execute("""
            INSERT INTO challenger_players (puuid, currently_challenger)
            VALUES (?, 1)
            ON CONFLICT(puuid) DO UPDATE SET currently_challenger = 1
        """, (puuid,))
        ##don't understand this SQL statement.

    #commit changes to the database and close the connection.
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_challenger_players_table()
    print("update complete")