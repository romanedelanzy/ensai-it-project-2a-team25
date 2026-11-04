from fastapi import APIRouter, Depends

from schema.fiabilite_model import ReliabilityReadModel, ScoreEvolutionModel
from service.fiabilite_service import ReliabilityService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_reliability_service():
    """Dependency provider for ReliabilityService."""
    return ReliabilityService()


@router.get(
    "/{station_id}",
    response_model=ReliabilityReadModel,
    tags=["Reliability"]
)
def get_station_reliability(
    station_id: str,
    reliability_service=Depends(get_reliability_service)
):
    """Retrieve reliability indicators for a station."""

    logger.info("Get reliability indicators for station %s", station_id)

    score_evolution = reliability_service.reliability_score_evolution(station_id)

    return ReliabilityReadModel(
        station_id=station_id,
        current_score=reliability_service.reliability_current_score(station_id),
        score_evolution=[
            ScoreEvolutionModel(date=date, score=score)
            for date, score in score_evolution.items()
        ],
        empty_percentage=reliability_service.percent_time_empty_all(station_id),
        saturation_percentage=reliability_service.percent_saturation_all(station_id),
        average_empty_duration=reliability_service.average_empty_duration_all(station_id),
        average_saturated_duration=reliability_service.average_saturated_duration_all(station_id)
    )