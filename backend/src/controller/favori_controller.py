# controller/FavoriController.py

from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import errors

from business_object.compte import Compte
from schema.favori_model import FavoriReadModel
from service.favori_service import FavoriService
from service.station_service import StationService
from utils.log_utils import get_logger
from utils.security import get_current_user

router = APIRouter()

logger = get_logger(__name__)


def get_favori_service():
    """Fournisseur d'injection de dépendance pour FavoriService."""
    return FavoriService()


def get_station_service():
    """Fournisseur d'injection de dépendance pour StationService."""
    return StationService()


@router.get("/", response_model=list[FavoriReadModel], tags=["Favoris"])
def get_user_favorite(
    favori_service=Depends(get_favori_service),
    current_user: Compte = Depends(get_current_user),
):
    """Liste les stations favorites d'un utilisateur.

    Args:
        favori_service (FavoriService): Service d'accès aux favoris.
        current_user (Compte): Utilisateur identifié par le header X-Auth-Token.

    Returns:
        list[FavoriReadModel]: Les favoris de l'utilisateur (liste vide s'il n'en a pas).
    """
    logger.info("List the favorites of a user")
    favoris = favori_service.recuperer_favoris_par_joueur(current_user.user_id)
    return [
        FavoriReadModel(user_id=f.utilisateur_id, station_id=f.station_id, create_at=f.cree_a)
        for f in favoris
    ]


@router.post("/{station_id}", status_code=201, tags=["Favoris"])
def add_favorite(
    station_id: str,
    favori_service=Depends(get_favori_service),
    current_user: Compte = Depends(get_current_user),
):
    """Ajoute une station aux favoris d'un utilisateur.

    Args:
        station_id (str): Identifiant de la station.
        favori_service (FavoriService): Service d'accès aux favoris.
        current_user (Compte): Utilisateur identifié par le header X-Auth-Token.

    Returns:
        dict: Un message de confirmation.

    Raises:
        HTTPException: 409 si la station est déjà dans les favoris de l'utilisateur.
        HTTPException: 404 si l'utilisateur ou la station n'existe pas.
        HTTPException: 500 si l'ajout échoue.
    """
    logger.info("Add a favorite")
    try:
        added = favori_service.ajouter_favori(current_user.user_id, station_id)
    except errors.UniqueViolation as err:
        raise HTTPException(status_code=409, detail="Station already in favorites.") from err
    except errors.ForeignKeyViolation as err:
        raise HTTPException(status_code=404, detail="User or station not found.") from err

    if not added:
        raise HTTPException(status_code=500, detail="Error while adding favorite.")

    return {"message": f"Station {station_id} added to the favorites of user {current_user.user_id}"}


@router.post("/nom/{station_name}", status_code=201, tags=["Favoris"])
def add_favorite_by_name(
    station_name: str,
    favori_service=Depends(get_favori_service),
    station_service=Depends(get_station_service),
    current_user: Compte = Depends(get_current_user),
):
    """Ajoute une station aux favoris de l'utilisateur connecté, à partir de son nom.

    Le nom est d'abord comparé exactement (sans tenir compte de la casse ni des espaces
    autour). À défaut, la recherche se fait sur une partie du nom (au moins 3 caractères) et
    doit identifier une seule station.

    Args:
        station_name (str): Nom (ou partie du nom) de la station.
        favori_service (FavoriService): Service d'accès aux favoris.
        station_service (StationService): Service d'accès aux stations.
        current_user (Compte): Utilisateur identifié par le header X-Auth-Token.

    Returns:
        dict: Un message de confirmation.

    Raises:
        HTTPException: 401 si le token est absent ou invalide.
        HTTPException: 404 si aucune station ne correspond à ce nom.
        HTTPException: 400 si plusieurs stations correspondent (nom trop imprécis).
        HTTPException: 409 si la station est déjà dans les favoris de l'utilisateur.
        HTTPException: 500 si l'ajout échoue.
    """
    logger.info("Add a favorite by station name")
    matches = station_service.search_by_name(station_name.strip())

    exact = [s for s in matches if s.name.strip().lower() == station_name.strip().lower()]
    if exact:
        matches = exact

    if not matches:
        raise HTTPException(status_code=404, detail="No station found with this name.")
    if len(matches) > 1:
        noms = ", ".join(sorted(s.name.strip() for s in matches))
        raise HTTPException(
            status_code=400,
            detail=f"Several stations match this name, please be more precise: {noms}",
        )

    return add_favorite(
        matches[0].station_id, favori_service=favori_service, current_user=current_user
    )


@router.delete("/{station_id}", tags=["Favoris"])
def remove_favorite(
    station_id: str,
    favori_service=Depends(get_favori_service),
    current_user: Compte = Depends(get_current_user),
):
    """Retire une station des favoris d'un utilisateur.

    Args:
        station_id (str): Identifiant de la station.
        favori_service (FavoriService): Service d'accès aux favoris.
        current_user (Compte): Utilisateur identifié par le header X-Auth-Token.

    Returns:
        dict: Un message de confirmation.

    Raises:
        HTTPException: 404 si ce favori n'existe pas.
    """
    logger.info("Remove a favorite")
    removed = favori_service.supprimer_favori(current_user.user_id, station_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found.")

    return {"message": f"Station {station_id} removed from the favorites of user {current_user.user_id}"}