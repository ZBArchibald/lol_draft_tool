import requests

from backend.core.config import API_KEY, MATCH_REGION, QUEUE_ID, REGION

DATA_DRAGON_VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"


def _riot_headers() -> dict[str, str | None]:
    return {"X-Riot-Token": API_KEY}


def get_current_patch() -> str:
    response = requests.get(DATA_DRAGON_VERSIONS_URL, timeout=10)
    response.raise_for_status()

    versions = response.json()
    if not isinstance(versions, list) or not versions:
        raise ValueError("Unexpected response format from Data Dragon API")

    return versions[0]


def get_challenger_league_puuids() -> list[str]:
    url = (
        f"https://{REGION}.api.riotgames.com/lol/league/v4/"
        "challengerleagues/by-queue/RANKED_SOLO_5x5"
    )
    response = requests.get(url, headers=_riot_headers(), timeout=10)
    response.raise_for_status()

    challenger_data = response.json()
    return [entry["puuid"] for entry in challenger_data["entries"]]


def get_match_ids(puuid: str, start: int, count: int) -> list[str]:
    url = (
        f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/"
        f"by-puuid/{puuid}/ids"
    )
    params = {
        "type": "ranked",
        "queue": QUEUE_ID,
        "start": start,
        "count": count,
    }
    response = requests.get(
        url,
        headers=_riot_headers(),
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return list(response.json())


def get_match_data(match_id: str) -> dict:
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=_riot_headers(), timeout=10)
    response.raise_for_status()
    return response.json()
