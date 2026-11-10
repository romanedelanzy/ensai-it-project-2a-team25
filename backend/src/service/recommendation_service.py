"Classe les stations proches selon leur distance et leur fiabilité"

from math import atan2, cos, exp, radians, sin, sqrt

from dao.StationDAO import StationDao
from dao.StationStatusDAO import StationStatusDao
from service.fiabilite_service import ReliabilityService
from utils.log_utils import log


class RecommandationService:
    """Construit des recommandations à partir de la position de l'utilisateur.

    Les scores de fiabilité proviennent de ``ReliabilityService`` et doivent
    être compris entre 0 et 1."""

    POIDS_DISTANCE = 0.5
    POIDS_FIABILITE = 0.5
    RAYON_TERRESTRE_KM = 6371.0
    SIGMA_DISTANCE_KM = 1.0

    def __init__(
        self,
        station_dao=None,
        station_status_dao=None,
        reliability_service=None,
    ):
        self.station_dao = station_dao if station_dao is not None else StationDao()
        self.station_status_dao = (
            station_status_dao if station_status_dao is not None else StationStatusDao()
        )
        self.reliability_service = (
            reliability_service if reliability_service is not None else ReliabilityService()
        )

    @staticmethod
    def _validate_position(latitude: float, longitude: float) -> None:
        if not isinstance(latitude, (int, float)) or isinstance(latitude, bool):
            raise TypeError("latitude doit être un nombre")
        if not -90 <= latitude <= 90:
            raise ValueError("latitude doit être comprise entre -90 et 90")
        if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
            raise TypeError("longitude doit être un nombre")
        if not -180 <= longitude <= 180:
            raise ValueError("longitude doit être comprise entre -180 et 180")

    @classmethod
    def calculer_distance(
        cls,
        latitude_1: float,
        longitude_1: float,
        latitude_2: float,
        longitude_2: float,
    ) -> float:
        """Renvoie la distance à vol d'oiseau entre deux coordonnées, en km."""
        lat1, lat2 = radians(latitude_1), radians(latitude_2)
        delta_lat = radians(latitude_2 - latitude_1)
        delta_lon = radians(longitude_2 - longitude_1)
        a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        return 2 * cls.RAYON_TERRESTRE_KM * atan2(sqrt(a), sqrt(1 - a))

    def _get_reliability_score(self, station_id: str) -> float:
        """Récupère le score de fiabilité calculé pour une station."""
        result = self.reliability_service.reliability_current_score(station_id)
        score = getattr(result, "score_fiabilite", result)
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise TypeError("Le score de fiabilité doit être numérique")
        if not 0 <= score <= 1:
            raise ValueError("Le score de fiabilité doit être compris entre 0 et 1")
        return float(score)

    @log
    def recommander_stations(
        self,
        latitude: float,
        longitude: float,
        limite: int = 5,
        rayon_km: float | None = None,
    ) -> list[dict]:
        """Retourne les stations utilisables triées du meilleur score au pire.

        Chaque résultat contient ``station``, ``distance_km``,
        ``score_fiabilite`` et ``score_recommandation``. Une station sans statut
        récent, non installée, ne permettant pas l'emprunt ou sans vélo est
        écartée. Le score combine à parts égales proximité (normalisée dans le
        rayon demandé) et fiabilité.
        """
        self._validate_position(latitude, longitude)
        if not isinstance(limite, int) or isinstance(limite, bool) or limite < 1:
            raise ValueError("limite doit être un entier positif")
        if rayon_km is not None and (
            not isinstance(rayon_km, (int, float)) or isinstance(rayon_km, bool) or rayon_km <= 0
        ):
            raise ValueError("rayon_km doit être un nombre positif")

        resultats = []
        for station in self.station_dao.list_all():
            distance = self.calculer_distance(
                latitude, longitude, station.latitude, station.longitude
            )
            if rayon_km is not None and distance > rayon_km:
                continue

            status = self.station_status_dao.find_current_status(station.station_id)
            if not (
                status
                and status.est_installee
                and status.permet_emprunt
                and status.nb_velos_dispos > 0
            ):
                continue

            reliability = self._get_reliability_score(station.station_id)
            # Décroissance gaussienne : à sigma, le score vaut environ 0,607.
            proximity_score = exp(-(distance**2) / (2 * self.SIGMA_DISTANCE_KM**2))
            recommendation_score = (
                self.POIDS_DISTANCE * proximity_score + self.POIDS_FIABILITE * reliability
            )

            resultats.append({
                "station": station,
                "distance_km": round(distance, 3),
                "score_fiabilite": reliability,
                "score_recommandation": round(recommendation_score, 4),
            })

        resultats.sort(
            key=lambda resultat: (
                -resultat["score_recommandation"],
                resultat["distance_km"],
                resultat["station"].name.casefold(),
            )
        )
        return resultats[:limite]
