from business_object.station import Station
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class StationDao(metaclass=Singleton):
    """Classe qui stocke et actualise les informations des stations."""

    @log
    def create(self, station) -> bool:
        """Crée une station dans la base de données.
        Parameters:
            Station à créer
        Returns:
            True si la station a été crée, False sinon
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO station(station_id, reseau_id, name, adresse, latitude, longitude, capacite) VALUES "
                        "(%(station_id)s, %(reseau_id)s, %(name)s, %(adresse)s, %(latitude)s, %(longitude)s, %(capacite)s) "
                        "RETURNING station_id;",
                        {
                            "station_id": station.station_id,
                            "reseau_id": station.reseau_id,
                            "name": station.name,
                            "adresse": station.adresse,
                            "latitude": station.latitude,
                            "longitude": station.longitude,
                            "capacite": station.capacite,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return res is not None

    @log
    def create_or_update(self, station) -> bool:
        """Crée une station ou la met à jour si station_id existe déjà.
        Parameters:
            Station à créer / mettre à jour
        Returns:
            True si la manipulation fonctionne, False sinon
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO station(station_id, reseau_id, name, adresse, latitude, longitude, capacite) VALUES "
                        "(%(station_id)s, %(reseau_id)s, %(name)s, %(adresse)s, %(latitude)s, %(longitude)s, %(capacite)s) "
                        "ON CONFLICT (station_id) DO UPDATE                                                              "
                        "   SET reseau_id = %(reseau_id)s,                                                              "
                        "       name = %(name)s,                                                                        "
                        "       adresse = %(adresse)s,                                                                  "
                        "       latitude = %(latitude)s,                                                                "
                        "       longitude = %(longitude)s,                                                              "
                        "       capacite = %(capacite)s                                                                 "
                        "RETURNING station_id;",
                        {
                            "station_id": station.station_id,
                            "reseau_id": station.reseau_id,
                            "name": station.name,
                            "adresse": station.adresse,
                            "latitude": station.latitude,
                            "longitude": station.longitude,
                            "capacite": station.capacite,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        return res is not None

    @log
    def find_by_id(self, station_id: str) -> Station:
        """Trouve une station par son id.
        Parameters:
            station_id (str): l'identifiant de la station à trouver.
        Returns:
            La station correspondant à l'identifiant
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                             "
                        "  FROM station                       "
                        " WHERE station_id = %(station_id)s;  ",
                        {"station_id": station_id},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        station = None
        if res:
            station = Station(
                station_id=res["station_id"],
                reseau_id=res["reseau_id"],
                name=res["name"],
                adresse=res["adresse"],
                latitude=float(res["latitude"]),
                longitude=float(res["longitude"]),
                capacite=res["capacite"],
            )

        return station

    @log
    def list_all(self) -> list[Station]:
        """Donne la liste des stations de la base de données.
        Returns:
            list[Station] ordonnée par nom de station
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                                "
                        "  FROM station                          "
                        " ORDER BY name;                         "
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        stations_list = []

        if res:
            for row in res:
                station = Station(
                    station_id=row["station_id"],
                    reseau_id=row["reseau_id"],
                    name=row["name"],
                    adresse=row["adresse"],
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    capacite=row["capacite"],
                )
                stations_list.append(station)

        return stations_list