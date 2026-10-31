from utils.env_variables import load_environment_variables

load_environment_variables()

from external_api.gbfs_factory import create_bordeaux_provider
from dao.StationDAO import StationDao
from dao.StationStatusDAO import StationStatusDao
from service.collection_service import CollectionService


provider = create_bordeaux_provider()

collection_service = CollectionService(
    provider=provider,
    station_dao=StationDao(),
    station_status_dao=StationStatusDao(),
)

resultat = collection_service.collect()

print("Résultat de la collecte :")
print(resultat)