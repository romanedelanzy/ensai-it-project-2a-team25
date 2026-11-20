"""Fournisseur de donnees metier pour le reseau de Bordeaux."""

from business_object.station import Station
from business_object.stationstatus import StationStatus
from external_api.BordeauxGBFSAdapter import BordeauxGBFSAdapter
from external_api.gbfs_client import GBFSClient
from external_api.gbfs_provider import GBFSProvider


class BordeauxGBFSProvider(GBFSProvider):
    """Relie le client HTTP a l'adaptateur Bordeaux, sans acces a la base."""

    def __init__(self, client: GBFSClient, adapter: BordeauxGBFSAdapter):
        """Recoit le client configure avec les URL et l'adaptateur du reseau."""
        self.client = client
        self.adapter = adapter

    def get_stations(self) -> list[Station]:
        """Recupere les informations JSON et les convertit en objets Station."""
        donnees = self.client.get_station_information()
        return [self.adapter.to_station(data) for data in donnees]

    def get_station_status(self) -> list[StationStatus]:
        """Recupere les disponibilites JSON et les convertit en StationStatus."""
        donnees = self.client.get_station_status()
        return [self.adapter.to_station_status(data) for data in donnees]
