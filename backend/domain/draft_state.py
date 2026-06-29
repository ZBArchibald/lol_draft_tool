from enum import Enum


class Position(Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    BOT = "bot"
    SUPPORT = "support"


class DraftState:
    def __init__(self, position: Position, banned: list[str], allies: list[str], enemies: list[str]) -> None:
        self.position = position
        self.banned = banned
        self.allies = allies
        self.enemies = enemies