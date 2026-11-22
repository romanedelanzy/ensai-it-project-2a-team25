"""Gestion de la collecte GBFS en arrière-plan."""

import asyncio

from utils.env_variables import load_environment_variables

load_environment_variables()

from external_api.gbfs_factory import create_bordeaux_provider
from dao.StationDAO import StationDao
from dao.StationStatusDAO import StationStatusDao
from service.collection_service import CollectionService
from service.export_database_service import ExportDatabaseService
from utils.log_utils import get_logger

logger = get_logger(__name__)

INTERVAL_SECONDS = 60 * 60


def collect_and_export():
    """Effectue une collecte GBFS puis exporte la base."""

    provider = create_bordeaux_provider()

    collection_service = CollectionService(
        provider=provider,
        station_dao=StationDao(),
        station_status_dao=StationStatusDao(),
    )

    resultat = collection_service.collect()

    logger.info("Résultat de la collecte : %s", resultat)

    ExportDatabaseService().run()


async def collection_loop():
    """Réalise une collecte toutes les 1 heures."""

    logger.info("Première collecte GBFS dans 1 heures.")

    while True:

        await asyncio.sleep(INTERVAL_SECONDS)

        try:
            await asyncio.to_thread(collect_and_export)

        except Exception:
            logger.exception("Échec de la collecte ou de l'export GBFS.")

