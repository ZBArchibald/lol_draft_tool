### 
# This module holds the functions for retrieving match data from the Riot Games API,
#  as well as storing and updating it in the matches table.
###

import sqlite3
import utils
import requests

API_KEY = utils.get_api_key()
REGION = "na1" 
MATCH_REGION = "americas"

# set the headers with the API key for authentication
headers = {"X-Riot-Token": API_KEY}

