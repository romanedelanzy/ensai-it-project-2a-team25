"""Acces HTTP aux flux GBFS, sans logique metier ni acces a la base."""

from typing import Any

import requests


class GBFSError(Exception):
    """Si le flux GBFS est inaccessible ou sa structure est invalide, herite de Exception."""


class GBFSClient:
    """Recupere les flux depuis les URL directes des deux fichiers GBFS station_status et
    station_information.

    Les donnees sont renvoyees telles quelles. Leur conversion en objets
    metier et leur enregistrement appartiennent au service de collecte.
    """

    def __init__(
        self,
        station_information_url: str,
        station_status_url: str,
        timeout: float = 10,
    ):
        if timeout <= 0:
            raise ValueError("Le delai d'attente doit etre strictement positif.")
        self.station_information_url = station_information_url
        self.station_status_url = station_status_url
        self.timeout = timeout

    def _get_data(self, url: str) -> dict[str, Any]:
        """Interroge une URL GBFS et renvoie le contenu de son champ 'data'.

        Effectue une requete HTTP GET avec le delai self.timeout, verifie
        le statut HTTP, puis convertit la reponse JSON en dictionnaire Python.
        Verifie ensuite que la reponse et son champ 'data' sont des dictionnaires.

        Args:
            url: Adresse du flux station_information ou station_status.

        Returns:
            Le dictionnaire contenu dans 'data', sans les metadonnees
            'ttl', 'version' et 'last_updated'. Par exemple, une reponse
            {"ttl": 60, "data": {"stations": []}} donne {"stations": []}.
            Le contenu de 'stations' est verifie par _get_stations.

        Raises:
            GBFSError: Si la requete echoue (reseau, delai depasse ou erreur
                HTTP), si le JSON est invalide, ou si la reponse ou son
                champ 'data' n'est pas un dictionnaire (y compris s'il manque)."""

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise GBFSError("Impossible de recuperer le flux GBFS.") from exc

        try:
            json_data = response.json()
        except ValueError as exc:
            raise GBFSError("Le flux GBFS ne contient pas un JSON valide.") from exc

        if not isinstance(json_data, dict) or not isinstance(json_data.get("data"), dict):
            raise GBFSError("Le flux GBFS doit contenir un objet 'data'.")
        return json_data["data"]

    def _get_stations(self, url: str) -> list[dict[str, Any]]:
        stations = self._get_data(url).get("stations")
        if not isinstance(stations, list) or any(
            not isinstance(station, dict) for station in stations
        ):
            raise GBFSError("Le champ 'stations' doit etre une liste de dict.")
        return stations

    def get_station_information(self) -> list[dict[str, Any]]:
        """Renvoie les informations descriptives des stations."""
        return self._get_stations(self.station_information_url)

    def get_station_status(self) -> list[dict[str, Any]]:
        """Renvoie les disponibilites et les etats actuels des stations."""
        return self._get_stations(self.station_status_url)
