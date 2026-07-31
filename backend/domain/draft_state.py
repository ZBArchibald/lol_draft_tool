from enum import Enum


class Position(Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    BOT = "bot"
    SUPPORT = "support"


class DraftState:
    def __init__(self, position: Position, banned: list[int], allies: list[int], enemies: list[int]) -> None:
        self.position = position
        self.banned = banned
        self.allies = allies
        self.enemies = enemies