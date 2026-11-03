from typing import Literal
 
from fastapi import APIRouter, Depends, HTTPException
 
from schema.station_model import StationReadModel, StationStatusReadModel
from service.station_service import StationService
from utils.log_utils import get_logger
from utils.security import verify_token
 
router = APIRouter()
 
logger = get_logger(__name__)
 
 
def get_station_service():
    """Fournit les injections de dépendances pour StationService."""
    return StationService()
 
 
@router.get("/", response_model=list[StationReadModel], tags=["Stations"])
async def find_all_stations(name: str | None = None, station_service=Depends(get_station_service)):
    """Liste toutes les stations ou les recherche par leur nom.
    Args:
        name (str, optional): Partie du nom d'une station (au moins 3 caractères).
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
    Returns:
        list[StationReadModel]: Toutes les stations, ou celles correspondant au nom.
    """
    logger.info("List all stations")
    if name:
        return station_service.search_by_name(name)
    return station_service.list_all()
 
 
@router.get("/{station_id}", response_model=StationReadModel, tags=["Stations"])
async def station_by_id(station_id: str, station_service=Depends(get_station_service)):
    """Trouve une station par son identifiant unique.
    Args:
        station_id (str)
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
    Returns:
        StationReadModel: Les données de la station si elle est trouvée.
    Raises:
        HTTPXException: Erreur 404 si la station n'est pas trouvée.
    """
    logger.info("Find a station by id")
    station = station_service.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station (id={station_id}) not found.")
    return station
 
 
@router.get("/{station_id}/status", response_model=StationStatusReadModel, tags=["Stations"])
async def station_current_status(station_id: str, station_service=Depends(get_station_service)):
    """Récupère le dernier statut d'une station.
    Args:
        station_id (str)
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
    Returns:
        StationStatusReadModel: Le dernier statut de la station.
    Raises:
        HTTPException: Erreur 404 si aucun statut n'existe pour cette station.
    """
    logger.info("Get the current status of a station")
    status = station_service.get_current_status(station_id)
    if not status:
        raise HTTPException(
            status_code=404, detail=f"No status found for station (id={station_id})."
        )
    return status
 
 
@router.get(
    "/{station_id}/history", response_model=list[StationStatusReadModel], tags=["Stations"]
)
async def station_history(
    station_id: str,
    period: Literal["24h", "7j", "30j"] = "24h",
    station_service=Depends(get_station_service),
):
    """Récupère l'historique d'une station sur les dernières 24h, 7 jours ou 30 jours.
    Args:
        station_id (str)
        period (str): '24h', '7j' ou '30j' (par défaut '24h').
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
    Returns:
        list[StationStatusReadModel]: Les statuts enregistrés sur la période.
    Raises:
        HTTPException: Erreur 404 si la station n'est pas trouvée.
        HTTPException: Erreur 422 si la période n'est pas '24h', '7j' ou '30j'.
    """
    logger.info("Get the history of a station")
    station = station_service.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station (id={station_id}) not found.")
    return station_service.get_history_by_period(station_id, period)
 
 
@router.delete("/{station_id}", tags=["Stations"], dependencies=[Depends(verify_token)])
async def delete_station(station_id: str, station_service=Depends(get_station_service)):
    """Supprime une station du système (authentification requise).
    Args:
        station_id (str)
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
    Returns:
        str: Un message de confirmation indiquant que la station a été supprimée.
    Raises:
        HTTPException: Erreur 401 si l'utilisateur n'est pas authentifié.
        HTTPException: Erreur 404 si la station n'est pas trouvée.
        HTTPException: Erreur 500 si la suppression échoue.
    """
    logger.info("Delete a station")
    station = station_service.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station (id={station_id}) not found.")
 
    if not station_service.delete(station):
        raise HTTPException(status_code=500, detail="Error while deleting station.")
 
    return f"Station {station.name} deleted"
