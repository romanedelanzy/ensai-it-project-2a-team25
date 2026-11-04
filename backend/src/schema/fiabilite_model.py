from datetime import datetime

from pydantic import BaseModel


class ScoreEvolutionModel(BaseModel):
    """Reliability score at a given time."""

    date: datetime
    score: float


class ReliabilityReadModel(BaseModel):
    """Reliability indicators of a station, returned by the API."""

    station_id: str
    current_score: float
    score_evolution: list[ScoreEvolutionModel]
    empty_percentage: float
    saturation_percentage: float
    average_empty_duration: float | None
    average_saturated_duration: float | None