from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

REGION = "na1" 
MATCH_REGION = "americas"
DB_PATH = "data/riot_data.db"