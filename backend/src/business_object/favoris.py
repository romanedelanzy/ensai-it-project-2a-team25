from datetime import datetime
class Favori:
    """
    Représente un favori associé à une station et à un utilisateur.
    """
    def __init__(self, station_id: int, utilisateur_id:int, cree_a: datetime):
        self.station_id = station_id
        self.utilisateur_id = utilisateur_id
        self.cree_a = cree_a
