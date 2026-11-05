from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import errors

from business_object.compte import Compte
from schema.favori_model import FavoriReadModel
from service.favori_service import FavoriService
from utils.log_utils import get_logger
from utils.security import get_current_user

router = APIRouter()

logger = get_logger(__name__)


def get_favori_service():
    """Fournisseur d'injection de dépendance pour FavoriService."""
    return FavoriService()


@router.get("/", response_model=list[FavoriReadModel], tags=["Favoris"])
def get_user_favorite(
    favori_service=Depends(get_favori_service),
    current_user: Compte = Depends(get_current_user),
):
    """Liste les stations favorites de l'utilisateur connecté.

    Args:
        favori_service (FavoriService): Service d'accès aux favoris.
        current_user (Compte): Utilisateur identifié par le header X-Auth-Token.

    Returns:
        list[FavoriReadModel]: Les favoris de l'utilisateur (liste vide s'il n'en a pas).
    """
    logger.info("List the favorites of the current user")
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
    """Ajoute une station aux favoris de l'utilisateur connecté.

    Args:
        station_id (str): Identifiant de la station.
        favori_service (FavoriService): Service d'accès aux favoris.
        current_user (Compte): Utilisateur identifié par le header X-Auth-Token.

    Returns:
        dict: Un message de confirmation.

    Raises:
        HTTPException: 401 si le token est absent ou invalide.
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


@router.delete("/{station_id}", tags=["Favoris"])
def remove_favorite(
    station_id: str,
    favori_service=Depends(get_favori_service),
    current_user: Compte = Depends(get_current_user),
):
    """Retire une station des favoris de l'utilisateur connecté.

    Args:
        station_id (str): Identifiant de la station.
        favori_service (FavoriService): Service d'accès aux favoris.
        current_user (Compte): Utilisateur identifié par le header X-Auth-Token.

    Returns:
        dict: Un message de confirmation.

    Raises:
        HTTPException: 401 si le token est absent ou invalide.
        HTTPException: 404 si ce favori n'existe pas.
    """
    logger.info("Remove a favorite")
    removed = favori_service.supprimer_favori(current_user.user_id, station_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found.")

    return {"message": f"Station {station_id} removed from the favorites of user {current_user.user_id}"}