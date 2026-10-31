
from abc import ABC, abstractmethod

from business_object.station import Station
from business_object.stationstatus import StationStatus


class GBFSProvider(ABC):
    """Definit les methodes que chaque provider de reseau doit implementer.

    Les providers renvoient des objets metier, et non les dictionnaires
    JSON bruts recuperes par le client HTTP.
    """

    @abstractmethod
    def get_stations(self) -> list[Station]:
        """Renvoie les informations descriptives des stations du reseau."""
        pass

    @abstractmethod
    def get_station_status(self) -> list[StationStatus]:
        """Renvoie les releves de disponibilite et d'etat des stations."""
        pass
