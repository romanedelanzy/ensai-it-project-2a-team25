
from business_object.favoris import Favori
from dao.FavoriDAO import FavoriDao
from utils.log_utils import log


class FavoriService:
    """Service qui gère les stations favorites des utilisateurs."""

    def __init__(self, favori_dao=None):
        """Initialise le service avec un DAO."""
        self.favori_dao = (
            favori_dao if favori_dao is not None else FavoriDao()
        )

    @log
    def ajouter_favori(self, user_id: int, station_id: str) -> bool:
        """Ajoute une station aux favoris d'un utilisateur."""
        return self.favori_dao.add_favorite(user_id, station_id)

    @log
    def supprimer_favori(self, user_id: int, station_id: str) -> bool:
        """Supprime une station des favoris d'un utilisateur."""
        return self.favori_dao.remove_favorite(user_id, station_id)

    @log
    def recuperer_favoris_par_joueur(
        self, user_id: int
    ) -> list[Favori]:
        """Récupère les stations favorites d'un utilisateur."""
        return self.favori_dao.user_favorite(user_id)
