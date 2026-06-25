import logging
import requests
import threading
import time
from collections import deque

from backend.core.config import API_KEY, MATCH_REGION, QUEUE_ID, REGION

LOG = logging.getLogger(__name__)
DATA_DRAGON_VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"

_REQUEST_RATE_LIMIT_1S = 20
_REQUEST_RATE_LIMIT_120S = 100
_REQUEST_WINDOW_1S = 1.0
_REQUEST_WINDOW_120S = 120.0
_REQUEST_MAX_RETRIES = 3
_REQUEST_BACKOFF_BASE = 1.0
_REQUEST_BACKOFF_MAX = 60.0

_request_lock = threading.Lock()
_request_timestamps: deque[float] = deque()


def _riot_headers() -> dict[str, str | None]:
    return {"X-Riot-Token": API_KEY}


def _wait_for_rate_limit() -> None:
    while True:
        now = time.monotonic()
        with _request_lock:
            while _request_timestamps and _request_timestamps[0] <= now - _REQUEST_WINDOW_120S:
                _request_timestamps.popleft()

            last_1s_count = sum(
                1 for timestamp in _request_timestamps
                if timestamp > now - _REQUEST_WINDOW_1S
            )
            last_120s_count = len(_request_timestamps)

            if last_1s_count < _REQUEST_RATE_LIMIT_1S and last_120s_count < _REQUEST_RATE_LIMIT_120S:
                _request_timestamps.append(now)
                return

            wait_1s = 0.0
            wait_120s = 0.0

            if last_1s_count >= _REQUEST_RATE_LIMIT_1S:
                earliest_1s_timestamp = min(
                    timestamp for timestamp in _request_timestamps
                    if timestamp > now - _REQUEST_WINDOW_1S
                )
                wait_1s = earliest_1s_timestamp + _REQUEST_WINDOW_1S - now

            if last_120s_count >= _REQUEST_RATE_LIMIT_120S:
                wait_120s = _request_timestamps[0] + _REQUEST_WINDOW_120S - now

        wait_time = max(wait_1s, wait_120s, 0.01)
        LOG.debug(
            "Rate limiter waiting %.3fs (1s=%s/20, 120s=%s/100)",
            wait_time,
            last_1s_count,
            last_120s_count,
        )
        time.sleep(wait_time)


def _make_riot_request(
    url: str,
    params: dict[str, str | int] | None = None,
    timeout: int = 10,
) -> requests.Response:
    attempt = 0

    while True:
        attempt += 1
        _wait_for_rate_limit()

        response = requests.get(url, headers=_riot_headers(), params=params, timeout=timeout)
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            try:
                delay = float(retry_after) if retry_after is not None else 0.0
            except ValueError:
                delay = 0.0

            if delay <= 0:
                delay = min(_REQUEST_BACKOFF_BASE * 2 ** (attempt - 1), _REQUEST_BACKOFF_MAX)

            LOG.warning(
                "Riot API rate limit hit: 429 on %s (attempt %s), retry-after=%s, sleeping %.1fs",
                url,
                attempt,
                retry_after,
                delay,
            )

            if attempt < _REQUEST_MAX_RETRIES:
                time.sleep(delay)
                continue

            LOG.error(
                "Riot API request failed after %s retries: %s",
                _REQUEST_MAX_RETRIES,
                url,
            )

        response.raise_for_status()
        return response


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
    response = _make_riot_request(url, timeout=10)

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
    response = _make_riot_request(url, params=params, timeout=10)
    return list(response.json())


def get_match_data(match_id: str) -> dict:
    url = f"https://{MATCH_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = _make_riot_request(url, timeout=10)
    return response.json()
