from fastapi import APIRouter, Depends, HTTPException, Query
from utils.geocoding import geocode_bordeaux_address

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
    latitude: float | None = Query(None, ge=-90, le=90),
    longitude: float | None = Query(None, ge=-180, le=180),
    address: str | None = Query(None, min_length=2),
    limite: int = Query(5, ge=1),
    rayon_km: float | None = Query(None, gt=0),
    recommendation_service=Depends(get_recommendation_service),
):
    """Renvoie les meilleures stations disponibles à proximité
    de la position ou de l'adresse indiquée."""
    logger.info("Get station recommendations")

    if address is not None:
        try:
            latitude, longitude = geocode_bordeaux_address(address)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    if latitude is None or longitude is None:
        raise HTTPException(
            status_code=422,
            detail="Either latitude/longitude or address must be provided.",
        )

    return recommendation_service.recommander_stations(
        latitude=latitude,
        longitude=longitude,
        limite=limite,
        rayon_km=rayon_km,
    )
