class Favori:
    """
    Représente un favori associé à une station et à un utilisateur.

    Attributs
    ---------
    station_id : int
        Identifiant de la station ajoutée aux favoris.
    utilisateur_id : int
        Identifiant de l'utilisateur ayant ajouté la station aux favoris.
    cree_a : datetime
        Date et heure de création du favori.
    """
    def __init__(self, station_id, utilisateur_id, cree_a):
        self.station_id = station_id
        self.utilisateur_id = utilisateur_id
        self.cree_a = cree_a
