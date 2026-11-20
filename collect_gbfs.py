"""Lance périodiquement la collecte des données GBFS de Bordeaux."""

import time

from utils.env_variables import load_environment_variables

load_environment_variables()

from external_api.gbfs_factory import create_bordeaux_provider
from dao.StationDAO import StationDao
from dao.StationStatusDAO import StationStatusDao
from service.collection_service import CollectionService
from service.export_database_service import ExportDatabaseService
from utils.log_utils import get_logger

logger = get_logger(__name__)

INTERVAL_SECONDS = 20 * 60


def main():
    """Exécute une collecte toutes les 20 minutes."""

    provider = create_bordeaux_provider()

    collection_service = CollectionService(
        provider=provider,
        station_dao=StationDao(),
        station_status_dao=StationStatusDao(),
    )

    export_service = ExportDatabaseService()

    print("Démarrage de la collecte périodique GBFS.")

    while True:
        debut = time.monotonic()

        try:
            resultat = collection_service.collect()

            print(f"Résultat de la collecte : {resultat}")

            export_service.run()

        except Exception:
            logger.exception(
                "Échec de la collecte ou de l'export GBFS."
            )

        duree = time.monotonic() - debut
        attente = max(0, INTERVAL_SECONDS - duree)

        print(f"Prochaine collecte dans {attente:.1f} secondes.")
        time.sleep(attente)


if __name__ == "__main__":
    main()