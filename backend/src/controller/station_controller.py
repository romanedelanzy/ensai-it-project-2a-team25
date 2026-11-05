from typing import Literal

from fastapi import APIRouter, Depends, HTTPException

from schema.station_model import StationReadModel, StationStatusReadModel
from service.station_service import StationService
from utils.log_utils import get_logger
from utils.security import get_current_user
from business_object.station import Station
from datetime import datetime

router = APIRouter()

logger = get_logger(__name__)


def get_station_service():
    """Fournit les injections de dépendances pour StationService."""
    return StationService()


def _verifier_admin(current_user) -> None:
    """Lève une erreur 403 si l'utilisateur connecté n'est pas administrateur."""
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Action réservée aux administrateurs.")


def _construire_station(station_id: str, s: StationReadModel) -> Station:
    """Construit une Station à partir des données reçues.
    Les vérifications de Station (capacité positive, latitude valide, etc.) donnent
    une erreur 422 au lieu d'une erreur serveur si une valeur est invalide.
    """
    try:
        return Station(
            station_id=station_id,
            reseau_id=s.reseau_id,
            name=s.name,
            adresse=s.adresse,
            latitude=s.latitude,
            longitude=s.longitude,
            capacite=s.capacite,
        )
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=list[StationReadModel], tags=["Stations"])
async def find_all_stations(
    name: str | None = None,
    station_service=Depends(get_station_service),
    current_user=Depends(get_current_user),  # Exige un token valide X-Auth-Token
):
    """Liste toutes les stations ou les recherche par leur nom.
    Args:
        name (str, optional): Partie du nom d'une station (au moins 3 caractères).
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
        current_user (Compte): L'utilisateur connecté.
    Returns:
        list[StationReadModel]: Toutes les stations, ou celles correspondant au nom.
    Raises:
        HTTPException: Erreur 401 si l'utilisateur n'est pas authentifié.
    """
    logger.info(f"List all stations (user: {current_user.username})")
    if name:
        return station_service.search_by_name(name)
    return station_service.list_all()


@router.get("/{station_id}", response_model=StationReadModel, tags=["Stations"])
async def station_by_id(
    station_id: str,
    station_service=Depends(get_station_service),
    current_user=Depends(get_current_user),  # Exige un token valide X-Auth-Token
):
    """Trouve une station par son identifiant unique.
    Args:
        station_id (str)
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
        current_user (Compte): L'utilisateur connecté.
    Returns:
        StationReadModel: Les données de la station si elle est trouvée.
    Raises:
        HTTPException: Erreur 401 si l'utilisateur n'est pas authentifié.
        HTTPException: Erreur 404 si la station n'est pas trouvée.
    """
    logger.info(f"Find a station by id (user: {current_user.username})")
    station = station_service.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station (id={station_id}) not found.")
    return station


@router.get("/{station_id}/status", response_model=StationStatusReadModel, tags=["Stations"])
async def station_current_status(
    station_id: str,
    station_service=Depends(get_station_service),
    current_user=Depends(get_current_user),  # Exige un token valide X-Auth-Token
):
    """Récupère le dernier statut d'une station.
    Args:
        station_id (str)
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
        current_user (Compte): L'utilisateur connecté.
    Returns:
        StationStatusReadModel: Le dernier statut de la station.
    Raises:
        HTTPException: Erreur 401 si l'utilisateur n'est pas authentifié.
        HTTPException: Erreur 404 si aucun statut n'existe pour cette station.
    """
    logger.info(f"Get the current status of a station (user: {current_user.username})")
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
    current_user=Depends(get_current_user),  # Exige un token valide X-Auth-Token
):
    """Récupère l'historique d'une station sur les dernières 24h, 7 jours ou 30 jours.
    Args:
        station_id (str)
        period (str): '24h', '7j' ou '30j' (par défaut '24h').
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
        current_user (Compte): L'utilisateur connecté.
    Returns:
        list[StationStatusReadModel]: Les statuts enregistrés sur la période.
    Raises:
        HTTPException: Erreur 401 si l'utilisateur n'est pas authentifié.
        HTTPException: Erreur 404 si la station n'est pas trouvée.
        HTTPException: Erreur 422 si la période n'est pas '24h', '7j' ou '30j'.
    """
    logger.info(f"Get the history of a station (user: {current_user.username})")
    station = station_service.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station (id={station_id}) not found.")
    return station_service.get_history_by_period(station_id, period)

@router.get("/{station_id}/availability-history",response_model=list[tuple[datetime, int]],tags=["Stations"],)
async def station_availability_history(
    station_id: str,
    period: Literal["24h", "7j", "30j"] = "24h",
    station_service=Depends(get_station_service),
    current_user=Depends(get_current_user),
):
    """Récupère l'évolution de la disponibilité d'une station."""

    logger.info(
        f"Get availability history of station {station_id} "
        f"(user: {current_user.username})"
    )

    station = station_service.get_station(station_id)

    if not station:
        raise HTTPException(
            status_code=404,
            detail=f"Station (id={station_id}) not found.",
        )

    return station_service.get_availability_history(station_id, period)

@router.post("/", response_model=StationReadModel, tags=["Stations"])
async def create_station(
    s: StationReadModel,
    station_service=Depends(get_station_service),
    current_user=Depends(get_current_user),  # Exige un token valide X-Auth-Token
):
    """Crée une nouvelle station (administrateur uniquement).
    Args:
        s (StationReadModel): Les données de la station à créer.
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
        current_user (Compte): L'utilisateur connecté.
    Returns:
        StationReadModel: Les données de la station créée.
    Raises:
        HTTPException: Erreur 401 si l'utilisateur n'est pas authentifié.
        HTTPException: Erreur 403 si l'utilisateur n'est pas administrateur.
        HTTPException: Erreur 400 si l'identifiant de la station existe déjà.
        HTTPException: Erreur 422 si une valeur de la station est invalide.
        HTTPException: Erreur 500 si la création échoue.
    """
    logger.info(f"Create a station (user: {current_user.username})")
    _verifier_admin(current_user)

    if station_service.get_station(s.station_id):
        raise HTTPException(status_code=400, detail="Station id already used.")

    new_station = _construire_station(s.station_id, s)

    if not station_service.create(new_station):
        raise HTTPException(status_code=500, detail="Error while creating station.")
    return new_station


@router.put("/{station_id}", response_model=StationReadModel, tags=["Stations"])
async def update_station(
    station_id: str,
    s: StationReadModel,
    station_service=Depends(get_station_service),
    current_user=Depends(get_current_user),  # Exige un token valide X-Auth-Token
):
    """Met à jour une station existante (administrateur uniquement).
    L'identifiant de la station est celui de l'URL.
    Args:
        station_id (str)
        s (StationReadModel): Les nouvelles données de la station.
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
        current_user (Compte): L'utilisateur connecté.
    Returns:
        StationReadModel: Les données de la station mise à jour.
    Raises:
        HTTPException: Erreur 401 si l'utilisateur n'est pas authentifié.
        HTTPException: Erreur 403 si l'utilisateur n'est pas administrateur.
        HTTPException: Erreur 404 si la station n'est pas trouvée.
        HTTPException: Erreur 422 si une valeur de la station est invalide.
        HTTPException: Erreur 500 si la mise à jour échoue.
    """
    logger.info(f"Update station {station_id} (user: {current_user.username})")
    _verifier_admin(current_user)

    if not station_service.get_station(station_id):
        raise HTTPException(status_code=404, detail=f"Station (id={station_id}) not found.")

    updated_station = _construire_station(station_id, s)

    if not station_service.create_or_update(updated_station):
        raise HTTPException(status_code=500, detail="Error while updating station.")
    return updated_station


@router.delete("/{station_id}", tags=["Stations"])
async def delete_station(
    station_id: str,
    station_service=Depends(get_station_service),
    current_user=Depends(get_current_user),  # Exige un token valide X-Auth-Token
):
    """Supprime une station du système (administrateur uniquement).
    Args:
        station_id (str)
        station_service (StationService): Le service utilisé pour interagir avec les données des stations.
        current_user (Compte): L'utilisateur connecté.
    Returns:
        str: Un message de confirmation indiquant que la station a été supprimée.
    Raises:
        HTTPException: Erreur 401 si l'utilisateur n'est pas authentifié.
        HTTPException: Erreur 403 si l'utilisateur n'est pas administrateur.
        HTTPException: Erreur 404 si la station n'est pas trouvée.
        HTTPException: Erreur 500 si la suppression échoue.
    """
    logger.info(f"Delete a station (user: {current_user.username})")
    _verifier_admin(current_user)

    station = station_service.get_station(station_id)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station (id={station_id}) not found.")

    if not station_service.delete(station):
        raise HTTPException(status_code=500, detail="Error while deleting station.")

    return f"Station {station.name} deleted"