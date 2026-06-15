class DraftState:
    def __init__(self, position: str, banned: list[str], allies: list[str], enemies: list[str]) -> None:
        self.position = position #should be one of: top, jungle, mid, adc, support
        self.banned = banned
        self.allies = allies
        self.enemies = enemies
        
