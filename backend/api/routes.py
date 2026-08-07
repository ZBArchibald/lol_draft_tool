import logging

from fastapi import APIRouter, HTTPException

from backend.api.schemas import ChampionRecommendation, DraftStateRequest, RecommendationResponse
from backend.db.queries import get_all_champions
from backend.domain.draft_state import DraftState
from backend.services.draft_service import recommend_champions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/draft", tags=["draft"])


@router.get("/champions")
async def list_champions() -> dict[int, str]:
    return get_all_champions()


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend(draft_state_request: DraftStateRequest) -> RecommendationResponse:
    draft_state = DraftState(
        position=draft_state_request.position,
        banned=draft_state_request.banned,
        allies=draft_state_request.allies,
        enemies=draft_state_request.enemies,
    )

    try:
        recommendation_hierarchy = recommend_champions(draft_state)
    except Exception:
        logger.exception("Failed to compute champion recommendations for %s", draft_state_request)
        raise HTTPException(status_code=500, detail="Failed to compute recommendations")

    return RecommendationResponse(
        recommendations=[
            ChampionRecommendation(champion=champion, win_chance=win_chance)
            for champion, win_chance in recommendation_hierarchy.items()
        ]
    )
