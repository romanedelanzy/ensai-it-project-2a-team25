from datetime import datetime

from business_object.stationstatus import StationStatus
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log

logger = get_logger(__name__)


class StationStatusDao:
    """Class containing methods to access the status of a station in the database."""

    @log
    def create_status(self, status: StationStatus) -> bool:
        """Create a stationstatus in the database.
        Args:
            StationStatus to create
        Returns:
            True if creation is successful, False otherwise
        """
        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO station_status("
                        "station_id, last_reported, num_bike_available, "
                        "num_bike_elec_available, num_docks_available, "
                        "is_installed, is_renting, is_returning) VALUES "
                        "(%(station_id)s, %(last_reported)s, "
                        "%(num_bike_available)s, "
                        "%(num_bike_elec_available)s, "
                        "%(num_docks_available)s, %(is_installed)s, "
                        "%(is_renting)s, %(is_returning)s) "
                        "RETURNING station_id;",
                        {
                            "station_id": status.id_station,
                            "last_reported": status.horodatage,
                            "num_bike_available": status.nb_velos_dispos,
                            "num_bike_elec_available": (
                                status.nb_velos_elec_dispos
                            ),
                            "num_docks_available": status.nb_places_dispos,
                            "is_installed": status.est_installee,
                            "is_renting": status.permet_emprunt,
                            "is_returning": status.permet_retour,

                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            created = True

        return created


@log
def find_current_status(
    self, id_station: str
) -> StationStatus | None:
    """Find the last updated status of a station by its id."""

    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * "
                    "FROM station_status "
                    "WHERE station_id = %(id_station)s "
                    "ORDER BY last_reported DESC "
                    "LIMIT 1;",
                    {"id_station": id_station},
                )
                res = cursor.fetchone()
    except Exception as e:
        logger.error(e)
        raise

    if res is None:
        return None

    return StationStatus(
        id_station=id_station,
        horodatage=res["last_reported"],
        nb_velos_dispos=res["num_bike_available"],
        nb_velos_elec_dispos=res["num_bike_elec_available"],
        nb_places_dispos=res["num_docks_available"],
        est_installee=res["is_installed"],
        permet_emprunt=res["is_renting"],
        permet_retour=res["is_returning"],
    )


@log
def find_history(
    self, station_id: str, start_date: datetime, end_date: datetime
) -> list[StationStatus]:
    """List all station statuses for a station between two dates."""

    try:
        with DBConnection().connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * "
                    "FROM station_status "
                    "WHERE station_id = %(station_id)s "
                    "AND last_reported BETWEEN %(start_date)s "
                    "AND %(end_date)s "
                    "ORDER BY last_reported ASC;",
                    {
                        "station_id": station_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                res = cursor.fetchall()
    except Exception as e:
        logger.error(e)
        raise

    station_status_list = []

    for row in res:
        station_status = StationStatus(
            id_station=station_id,
            horodatage=row["last_reported"],
            nb_velos_dispos=row["num_bike_available"],
            nb_velos_elec_dispos=row["num_bike_elec_available"],
            nb_places_dispos=row["num_docks_available"],
            est_installee=row["is_installed"],
            permet_emprunt=row["is_renting"],
            permet_retour=row["is_returning"],
        )
        station_status_list.append(station_status)

    return station_status_list
