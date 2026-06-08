class DraftState:
    def __init__(self, allies: list[str], enemies: list[str], banned: list[str]) -> None:
        self.allies = allies
        self.enemies = enemies
        self.banned = banned
