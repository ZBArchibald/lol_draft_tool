# game_patch.py
# fetches the latest League of Legends game patch from Data Dragon

import requests
from data.database_utils import update_metadata

URL = "https://ddragon.leagueoflegends.com/api/versions.json"

def get_current_patch():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()

        versions = response.json()

        if not isinstance(versions, list) or len(versions) == 0:
            raise ValueError("Unexpected response format from Data Dragon API")

        return versions[0]

    except requests.RequestException as e:
        raise RuntimeError(f"Network error while fetching patch data: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to parse patch data: {e}")

if __name__ == "__main__":
    current_patch = get_current_patch()
    update_metadata("current_patch", current_patch)