from datetime import datetime


class Favori:  # ruff: ignore[class-as-data-structure]
    """
    Représente un favori associé à une station et à un utilisateur.
    """
    def __init__(self, station_id: str, utilisateur_id: int, cree_a: datetime):
        self.station_id = station_id
        self.utilisateur_id = utilisateur_id
        self.cree_a = cree_a
