from datetime import datetime, timedelta, timezone
 
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

    def __init__(self, station_dao=None, station_status_dao=None):
        self.station_dao = station_dao if station_dao is not None else StationDao()
        self.station_status_dao = (
            station_status_dao if station_status_dao is not None else StationStatusDao()
        )

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
            Objet StationStatus si trouvé, sinon None.
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
    
    @log
    def search_by_name(self, name: str) -> list[Station]:
        """Cherche les stations dont le nom contient le string donné.
        Au moins 3 caractères sont requis pour lancer la recherche.
        Args:
            name (str)
        Returns:
            list[Station], vide s'il y a moins de 3 caractères.
        """
        if len(name) < 3:
            return []
        return [s for s in StationDao().list_all() if name.lower() in s.name.lower()]

    @log
    def is_operational(self, station_id: str) -> bool:
        """Vérifie si une station est opérationnelle.
        (installée, loue et accepte les retours de vélos).
        Args:
            station_id (str)
        Returns:
            True si la station est opérationnelle, False sinon.
        """
        status = StationStatusDao().find_current_status(station_id)
        return bool(
            status and status.est_installee and status.permet_emprunt and status.permet_retour
        )

    @log
    def get_fill_rate(self, station_id: str) -> float:
        """Calcule le taux de remplissage d'une station
        nombre de vélos disponibles divisé par la capacité de la station).
        Args:
            station_id (str)
        Returns:
            float entre 0 et 1, ou None si la station ou son status est inconnu,
            ou si la capacité est 0.
        """
        station = StationDao().find_by_id(station_id)
        status = StationStatusDao().find_current_status(station_id)
        if not station or not status or station.capacite == 0:
            return None
        return status.nb_velos_dispos / station.capacite

    @log
    def get_history_by_period(self, station_id: str, period: str = "24h") -> list:
        """Récupère tous les status enregistrés sur une station ces dernières 24h, 7jours ou 30jours.
        Args:
            station_id (str)
            period (str): '24h', '7j' ou '30j'
        Returns:
            list[StationStatus]
        Raises:
            ValueError: la période n'est pas de '24h', '7j', ou '30j'.
        """
        if period not in PERIODS:
            raise ValueError(f"period doit valoir {list(PERIODS)} (reçu {period!r})")
        end_date = datetime.now(timezone.utc)
        return self.get_history(station_id, end_date - PERIODS[period], end_date)
