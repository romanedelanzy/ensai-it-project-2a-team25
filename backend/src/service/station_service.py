from datetime import datetime, timedelta
 
from business_object.station import Station
from dao.StationDAO import StationDao
from dao.StationStatusDAO import StationStatusDao
from utils.log_utils import log

PERIODS = {
    "24h": timedelta(hours=24),
    "7j": timedelta(days=7),
    "30j": timedelta(days=30),
}

class StationService:
    """Service qui gère la logique métier liée aux stations (recherche, status, historique, etc.)."""

    @log
    def get_station(self, station_id: str) -> Station:
        """Trouve une station spécifique par son identifiant unique.
        Args:
            station_id (str)
        Returns:
            Objet station s'il est trouvé, sinon None.
        """
        return StationDao().find_by_id(station_id)

    @log
    def list_all(self) -> list[Station]:
        """Récupère toutes les stations de la base de données.
        Returns:
            list[Station]
        """
        return StationDao().list_all()

    @log
    def get_current_status(self, station_id: str):
        """Récupère le dernier status enregistré d'une station.
        Args:
            station_id (str)
        Returns:
            Objet StationStatu si trouvé, sinon None.
        """
        return StationStatusDao().find_current_status(station_id)

    @log
    def get_history(self, station_id: str, start_date: datetime, end_date: datetime) -> list:
        """Récupère tous les status enregistrés sur une station entre deux dates.
        Args:
            station_id (str)
            start_date (datetime)
            end_date (datetime)
        Returns:
            list[StationStatus]
        """
        return StationStatusDao().find_history(station_id, start_date, end_date)