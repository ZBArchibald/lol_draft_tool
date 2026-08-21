from pydantic import BaseModel, Field

from backend.domain.draft_state import Position


class DraftStateRequest(BaseModel):
    position: Position
    banned: list[int] = Field(default_factory=list)
    allies: list[int] = Field(default_factory=list)
    enemies: list[int] = Field(default_factory=list)


class ChampionInfo(BaseModel):
    name: str
    sprite_url: str


class ChampionRecommendation(BaseModel):
    champion: int
    win_chance: float


class RecommendationResponse(BaseModel):
    recommendations: list[ChampionRecommendation]
