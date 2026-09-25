```python
from dao.database_connection import DataBaseConnection
from business_object.favori import Favori


class FavoriDao:
    """
    Permet de gérer les favoris dans la base de données.
    """

    def creer(self, favori):
        """
        Ajoute un favori dans la base de données.
        """
        requete = """
            INSERT INTO favori (station_id, utilisateur_id, cree_a)
            VALUES (%s, %s, %s)
        """

        with DataBaseConnection().connection as connexion:
            with connexion.cursor() as curseur:
                curseur.execute(
                    requete,
                    (
                        favori.station_id,
                        favori.utilisateur_id,
                        favori.cree_a
                    )
                )

    def supprimer(self, station_id, utilisateur_id):
        """
        Supprime un favori.
        """
        requete = """
            DELETE FROM favori
            WHERE station_id = %s
            AND utilisateur_id = %s
        """

        with DataBaseConnection().connection as connexion:
            with connexion.cursor() as curseur:
                curseur.execute(
                    requete,
                    (station_id, utilisateur_id)
                )

    def trouver_par_utilisateur(self, utilisateur_id):
        """
        Récupère tous les favoris d'un utilisateur.
        """
        requete = """
            SELECT station_id, utilisateur_id, cree_a
            FROM favori
            WHERE utilisateur_id = %s
        """

        favoris = []

        with DBConnection().connection as connexion:
            with connexion.cursor() as curseur:
                curseur.execute(requete, (utilisateur_id,))
                resultats = curseur.fetchall()

                for resultat in resultats:
                    favori = Favori(
                        resultat["station_id"],
                        resultat["utilisateur_id"],
                        resultat["cree_a"]
                    )
                    favoris.append(favori)

        return favoris
```
