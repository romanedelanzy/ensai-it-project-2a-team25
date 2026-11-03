# controller/FavoriController.py

from fastapi import APIRouter, Depends, HTTPException
from psycopg2 import errors

from schema.favori_model import FavoriReadModel
from service.favori_service import FavoriService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_favori_service():
    """Fournisseur d'injection de dépendance pour FavoriService."""
    return FavoriService()


@router.get("/{user_id}", response_model=list[FavoriReadModel], tags=["Favoris"])
def get_user_favorite(user_id: int, favori_service=Depends(get_favori_service)):
    """Liste les stations favorites d'un utilisateur.

    Args:
        user_id (int): Identifiant de l'utilisateur.
        favori_service (FavoriService): Service d'accès aux favoris.

    Returns:
        list[FavoriReadModel]: Les favoris de l'utilisateur (liste vide s'il n'en a pas).
    """
    logger.info("List the favorites of a user")
    favoris = favori_service.recuperer_favoris_par_joueur(user_id)
    return [
        FavoriReadModel(user_id=f.utilisateur_id, station_id=f.station_id, create_at=f.cree_a)
        for f in favoris
    ]


@router.post("/{user_id}/{station_id}", status_code=201, tags=["Favoris"])
def add_favorite(user_id: int, station_id: str, favori_service=Depends(get_favori_service)):
    """Ajoute une station aux favoris d'un utilisateur.

    Args:
        user_id (int): Identifiant de l'utilisateur.
        station_id (str): Identifiant de la station.
        favori_service (FavoriService): Service d'accès aux favoris.

    Returns:
        dict: Un message de confirmation.

    Raises:
        HTTPException: 409 si la station est déjà dans les favoris de l'utilisateur.
        HTTPException: 404 si l'utilisateur ou la station n'existe pas.
        HTTPException: 500 si l'ajout échoue.
    """
    logger.info("Add a favorite")
    try:
        added = favori_service.ajouter_favori(user_id, station_id)
    except errors.UniqueViolation as err:
        raise HTTPException(status_code=409, detail="Station already in favorites.") from err
    except errors.ForeignKeyViolation as err:
        raise HTTPException(status_code=404, detail="User or station not found.") from err

    if not added:
        raise HTTPException(status_code=500, detail="Error while adding favorite.")

    return {"message": f"Station {station_id} added to the favorites of user {user_id}"}


@router.delete("/{user_id}/{station_id}", tags=["Favoris"])
def remove_favorite(user_id: int, station_id: str, favori_service=Depends(get_favori_service)):
    """Retire une station des favoris d'un utilisateur.

    Args:
        user_id (int): Identifiant de l'utilisateur.
        station_id (str): Identifiant de la station.
        favori_service (FavoriService): Service d'accès aux favoris.

    Returns:
        dict: Un message de confirmation.

    Raises:
        HTTPException: 404 si ce favori n'existe pas.
    """
    logger.info("Remove a favorite")
    removed = favori_service.supprimer_favori(user_id, station_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found.")

    return {"message": f"Station {station_id} removed from the favorites of user {user_id}"}