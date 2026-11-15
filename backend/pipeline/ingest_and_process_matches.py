import logging

from backend.core.config import PATCHES_RETAINED
from backend.db.connection import db_connection
from backend.db.queries import (
    get_ladder_puuids,
    get_last_synced_match_id,
    get_processed_match_ids,
    insert_matches,
    update_last_synced_match_id,
    upsert_champion_relationships,
    upsert_champion_stats,
)
from backend.external.riot_api import get_match_data, get_match_ids, get_recent_patches

LOG = logging.getLogger(__name__)

# raw Riot teamPosition tokens we aggregate stats for; stored as-is in champion_role_stats.role
_VALID_ROLES = {"TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"}

# teamPosition -> the matches column suffix for that role
_TEAM_POSITION_SUFFIX = {
    "TOP": "top",
    "JUNGLE": "jungle",
    "MIDDLE": "middle",
    "BOTTOM": "bottom",
    "UTILITY": "support",
}

_BLUE_TEAM_ID = 100

_EMPTY_MATCH_ROW = {
    "blueside_win": None,
    "blueside_top_champ_id": None,
    "blueside_jungle_champ_id": None,
    "blueside_middle_champ_id": None,
    "blueside_bottom_champ_id": None,
    "blueside_support_champ_id": None,
    "redside_top_champ_id": None,
    "redside_jungle_champ_id": None,
    "redside_middle_champ_id": None,
    "redside_bottom_champ_id": None,
    "redside_support_champ_id": None,
}

_EMPTY_RELATIONSHIP_ROW = {
    "wins_as_ally": 0,
    "games_as_ally": 0,
    "wins_as_opponent": 0,
    "games_as_opponent": 0,
}


def sync_all_ladder_matches(batch_size: int = 20) -> None:
    puuids = get_ladder_puuids()
    patches = get_recent_patches(PATCHES_RETAINED)
    LOG.info(
        "Starting match sync for %d ladder players (patches: %s)",
        len(puuids), ", ".join(patches),
    )

    for count, puuid in enumerate(puuids, start=1):
        sync_player_matches(puuid, patches, batch_size)
        LOG.info("Player %d/%d synced", count, len(puuids))
    LOG.info("Match sync complete")


def sync_player_matches(puuid: str, patches: list[str], batch_size: int = 20) -> None:
    last_synced_match_id = get_last_synced_match_id(puuid)
    LOG.info("Syncing player %s", puuid)
    start_index = 0
    stop_sync = False

    newest_match_id: str | None = None
    match_ids: list[str] = []
    match_rows: list[dict] = []
    stats: dict[tuple[int, str, str], dict[str, int]] = {}
    relationships: dict[tuple[int, int, str], dict[str, int]] = {}

    while not stop_sync:
        match_ids_batch = get_match_ids(puuid, start_index, batch_size)

        if not match_ids_batch:
            break

        if newest_match_id is None:
            newest_match_id = match_ids_batch[0]

        already_processed = get_processed_match_ids(match_ids_batch)

        for match_id in match_ids_batch:
            if match_id == last_synced_match_id:
                LOG.debug("Stopping sync for %s: reached prior sync point %s", puuid, match_id)
                stop_sync = True
                break

            if match_id in already_processed:
                # recorded via another ladder player's sync (shared match) - already
                # captured, but doesn't tell us anything about this player's own history
                LOG.debug("Skipping %s for %s: already processed via another player", match_id, puuid)
                continue

            match_data = get_match_data(match_id)
            patch = get_match_patch(match_data)

            if patch not in patches:
                LOG.debug("Stopping sync for %s: match %s is from patch %s, outside the retained patches", puuid, match_id, patch)
                stop_sync = True
                break

            LOG.debug("Aggregating match %s", match_id)
            match_ids.append(match_id)
            match_rows.append(build_match_row(match_id, patch, match_data))
            aggregate_match(match_data, patch, stats, relationships)
            if len(match_ids) % 10 == 0:
                LOG.info("Fetched %d matches for %s", len(match_ids), puuid)

        start_index += batch_size

    flush_player_data(puuid, newest_match_id, match_ids, match_rows, stats, relationships)
    LOG.info("Finished player %s: %d new matches processed", puuid, len(match_ids))


def get_match_patch(match_data: dict) -> str:
    #retrive and build truncated patch from match_data
    major, minor, *_ = match_data["info"]["gameVersion"].split(".")
    return f"{major}.{minor}"


def aggregate_match(
    match_data: dict,
    patch: str,
    stats: dict[tuple[int, str, str], dict[str, int]],
    relationships: dict[tuple[int, int, str], dict[str, int]],
) -> None:
    # excludes remakes and other games where teamPosition wasn't assigned, so
    # they're skipped consistently by both champion_stats and champion_relationships
    participants = [
        p for p in match_data["info"]["participants"]
        if p["teamPosition"] in _VALID_ROLES
    ]

    for participant in participants:
        key = (participant["championId"], participant["teamPosition"], patch)
        if key not in stats:
            stats[key] = {"wins": 0, "games": 0}
        stats[key]["wins"] += int(participant["win"])
        stats[key]["games"] += 1

    for participant_a in participants:
        for participant_b in participants:
            if participant_a is participant_b:
                continue
            key = (participant_a["championId"], participant_b["championId"], patch)
            row = relationships.setdefault(key, dict(_EMPTY_RELATIONSHIP_ROW))
            if participant_a["teamId"] == participant_b["teamId"]:
                row["wins_as_ally"] += int(participant_a["win"])
                row["games_as_ally"] += 1
            else:
                row["wins_as_opponent"] += int(participant_a["win"])
                row["games_as_opponent"] += 1


def build_match_row(match_id: str, patch: str, match_data: dict) -> dict:
    row = dict(_EMPTY_MATCH_ROW, match_id=match_id, patch=patch)

    for participant in match_data["info"]["participants"]:
        suffix = _TEAM_POSITION_SUFFIX.get(participant["teamPosition"])
        if suffix is None:
            continue
        side = "blueside" if participant["teamId"] == _BLUE_TEAM_ID else "redside"
        row[f"{side}_{suffix}_champ_id"] = participant["championId"]
        if side == "blueside":
            row["blueside_win"] = participant["win"]

    return row


def flush_player_data(
    puuid: str,
    newest_match_id: str | None,
    match_ids: list[str],
    match_rows: list[dict],
    stats: dict[tuple[int, str, str], dict[str, int]],
    relationships: dict[tuple[int, int, str], dict[str, int]],
) -> None:
    if newest_match_id is None:
        return
    with db_connection() as conn, conn.pipeline():
        if match_ids:
            insert_matches(conn, match_rows)
            upsert_champion_stats(
                conn,
                [
                    (champ_id, role, patch, row["wins"], row["games"])
                    for (champ_id, role, patch), row in stats.items()
                ],
            )
            upsert_champion_relationships(
                conn,
                [
                    (
                        champ_id,
                        other_champ_id,
                        patch,
                        row["wins_as_ally"],
                        row["games_as_ally"],
                        row["wins_as_opponent"],
                        row["games_as_opponent"],
                    )
                    for (champ_id, other_champ_id, patch), row in relationships.items()
                ],
            )
        update_last_synced_match_id(conn, puuid, newest_match_id)
