from business_object.station import Station
from business_object.stationstatus import StationStatus
from dao.StationDAO import StationDao
from dao.StationStatusDAO import StationStatusDao
from utils.log_utils import log
from datetime import datetime


class ReliabilityService:
    """ Service qui calcule la fiabilite d'une station a partir de l'historique."""
    
    def percent_time_empty(self, id_station: str, start: datetime, end: datetime) -> float:
        number_empty = 0
        status_station = StationStatusDao.find_history(id_station, start, end)
        for status in status_station:
            if status.is_empty():
                number_empty += 1
        
        return number_empty / len(status_station)
    
    def percent_time_empty(self, id_station: str, start: datetime, end: datetime) -> float:
        number_empty = 0
        status_station = StationStatusDao.find_history(id_station, end)
        for status in status_station:
            if status.is_empty():
                number_empty += 1
        
        return number_empty / len(status_station)

