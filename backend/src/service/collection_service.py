"""Service de collecte des donnees GBFS et d'enregistrement en base."""

from external_api.gbfs_provider import GBFSProvider
from dao.StationDAO import StationDao
from dao.StationStatusDAO import StationStatusDao
from utils.log_utils import get_logger, log

logger = get_logger(__name__)


class CollectionService:
    """Orchestre la collecte GBFS et l'enregistrement en base."""

    def __init__(
        self,
        provider: GBFSProvider,
        station_dao: StationDao,
        station_status_dao: StationStatusDao,
    ):
        self.provider = provider
        self.station_dao = station_dao
        self.station_status_dao = station_status_dao

    @log
    def collect(self) -> dict[str, int]:
        """Recupere et enregistre les stations et leurs statuts."""

        stations = self.provider.get_stations()

        for station in stations:
            self.station_dao.create_or_update(station)

        statuts = self.provider.get_station_status()

        nb_statuts_enregistres = 0

        for statut in statuts:
            if self.station_status_dao.create_status(statut):
                nb_statuts_enregistres += 1

        resultat = {
            "nb_stations_traitees": len(stations),
            "nb_statuts_recuperes": len(statuts),
            "nb_statuts_enregistres": nb_statuts_enregistres,
        }

        logger.info("Collecte terminee : %s", resultat)

        return resultat