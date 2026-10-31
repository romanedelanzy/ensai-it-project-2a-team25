"""Creation du fournisseur GBFS pour le reseau de Bordeaux. 
   Fournit les url de l'API de Bordeaux et créer le client, provider et adapter correspondants.
"""

import os

from external_api.gbfs_client import GBFSClient
from external_api.BordeauxGBFSAdapter import BordeauxGBFSAdapter
from external_api.BordeauxGBFSProvider import BordeauxGBFSProvider


API_KEY = os.getenv(
    "BORDEAUX_GBFS_API_KEY",
    "opendata-bordeaux-metropole-flux-gtfs-rt",
)

BASE_URL = "https://bdx.mecatran.com/utw/ws/gbfs/bordeaux/v3"

URL_STATION_INFORMATION = (
    f"{BASE_URL}/station_information.json?apiKey={API_KEY}"
)
URL_STATION_STATUS = (
    f"{BASE_URL}/station_status.json?apiKey={API_KEY}"
)


def create_bordeaux_provider() -> BordeauxGBFSProvider:
    """Construit un fournisseur GBFS configure pour Bordeaux."""
    client = GBFSClient(
        station_information_url=URL_STATION_INFORMATION,
        station_status_url=URL_STATION_STATUS,
    )
    # Note : par defaut j'ai mis Bordeaux en id 1 sur le reseau
    adapter = BordeauxGBFSAdapter(reseau_id=1)

    return BordeauxGBFSProvider(
        client=client,
        adapter=adapter,
    )