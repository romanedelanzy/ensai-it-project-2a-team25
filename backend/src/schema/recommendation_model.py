from pydantic import BaseModel

from schema.station_model import StationReadModel


class RecommendationReadModel(BaseModel):
    """Station recommandée et scores utilisés pour son classement."""

    station: StationReadModel
    distance_km: float
    score_fiabilite: float
    score_recommandation: float
