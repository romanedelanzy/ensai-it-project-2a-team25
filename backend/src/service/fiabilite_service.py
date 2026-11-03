from business_object.station import Station
from business_object.stationstatus import StationStatus
from dao.StationDAO import StationDao
from dao.StationStatusDAO import StationStatusDao
from utils.log_utils import log
from datetime import datetime


class ReliabilityService:
    """ Service qui calcule la fiabilite d'une station a partir de l'historique."""

    def percent_time_empty_until(self, id_station: str, start: datetime, end: datetime) -> float:
        number_empty = 0
        status_station = StationStatusDao.find_history_until(id_station, end)
        for status in status_station:
            if status.is_empty():
                number_empty += 1

        return number_empty / len(status_station)

    def percent_time_empty_all(self, id_station: str) -> float:
        number_empty = 0
        status_station = StationStatusDao.find_all_history(id_station)
        for status in status_station:
            if status.is_empty():
                number_empty += 1

        return number_empty / len(status_station)

    def percent_saturation_until(self, id_station: str, end: datetime) -> float:
        number_satur = 0
        status_station = StationStatusDao.find_history_until(id_station, end)
        for status in status_station:
            if status.is_saturated():
                number_satur += 1

        return number_satur / len(status_station)

    def percent_saturation_all(self, id_station: str) -> float:
        number_satur = 0
        status_station = StationStatusDao.find_all_history(id_station)
        for status in status_station:
            if status.is_saturated():
                number_satur += 1
        return number_satur / len(status_station)
    
    def mean_sat_all(self, id_station: str) -> float:
        status_station = StationStatusDao.find_all_history(id_station)

