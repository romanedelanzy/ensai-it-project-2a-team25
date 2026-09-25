from datetime import datetime

class ReliabilityStation:
    """
    Modèle représentant une ligne de la table 'ReliabilityStations'.

    Stocke les statistiques et indicateurs de fiabilité d'une station,
    calculés à un instant donné à partir de son historique de relevés.
    """

    def __init__(self, station_id: int, timestamp: datetime, score_fiabilite: float,
                 taux_remplissage_moyen: float, pct_temps_vide: float, pct_temps_sature: float):
        for nom, valeur in [
            ("score_fiabilite", score_fiabilite),
            ("taux_remplissage_moyen", taux_remplissage_moyen),
            ("pct_temps_vide", pct_temps_vide),
            ("pct_temps_sature", pct_temps_sature),
        ]:
            if not (0 <= valeur <= 100):
                raise ValueError(f"{nom} doit être compris entre 0 et 100 (reçu : {valeur})")

        self.station_id = station_id
        self.timestamp = timestamp
        self.score_fiabilite = score_fiabilite
        self.taux_remplissage_moyen = taux_remplissage_moyen
        self.pct_temps_vide = pct_temps_vide
        self.pct_temps_sature = pct_temps_sature
