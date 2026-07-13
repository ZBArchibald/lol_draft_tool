from pydantic import BaseModel, Field

from backend.domain.draft_state import Position


class DraftStateRequest(BaseModel):
    position: Position
    banned: list[str] = Field(default_factory=list)
    allies: list[str] = Field(default_factory=list)
    enemies: list[str] = Field(default_factory=list)


class ChampionRecommendation(BaseModel):
    champion: str
    win_chance: float


class RecommendationResponse(BaseModel):
    recommendations: list[ChampionRecommendation]
