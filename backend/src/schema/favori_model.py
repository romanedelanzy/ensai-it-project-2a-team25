from datetime import datetime

from pydantic import BaseModel


class FavoriReadModel(BaseModel):
    """Représentation JSON d'un favori renvoyée par l'API."""

    user_id: int
    station_id: str
    create_at: datetime