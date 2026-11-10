from fastapi import APIRouter, Depends, Query
from schema.recommendation_model import RecommendationReadModel

from service.recommandation_service import RecommandationService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_recommendation_service():
    """Fournit une instance de RecommandationService."""
    return RecommandationService()


@router.get("/", response_model=list[RecommendationReadModel], tags=["Recommandations"])
def get_recommendations(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    limite: int = Query(5, ge=1),
    rayon_km: float | None = Query(None, gt=0),
    recommendation_service=Depends(get_recommendation_service),
):
    """Renvoie les meilleures stations disponibles à proximité de la position indiquée."""
    logger.info("Get station recommendations")
    return recommendation_service.recommander_stations(
        latitude=latitude,
        longitude=longitude,
        limite=limite,
        rayon_km=rayon_km,
    )
