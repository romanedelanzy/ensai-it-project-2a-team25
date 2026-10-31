# Pour lancer le test : PYTHONPATH=backend/src python test_gbfs.py dans le terminal

from external_api.gbfs_factory import create_bordeaux_provider

provider = create_bordeaux_provider()

stations = provider.get_stations()
statuts = provider.get_station_status()

print(f"Nombre de stations récupérées : {len(stations)}")
print(f"Nombre de statuts récupérés : {len(statuts)}")

if stations:
    print("Première station :", stations[0])

if statuts:
    print("Premier statut :", statuts[0])