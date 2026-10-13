"""Conversion des donnees GBFS v3 de Bordeaux en objets metier."""

from datetime import datetime
from typing import Any

from business_object.station import Station
from business_object.stationstatus import StationStatus


class BordeauxGBFSAdapter:
    """Adapte une station ou un releve JSON, sans requete HTTP ni acces SQL."""

    def __init__(self, reseau_id: int):
        """Recoit l'identifiant du reseau Bordeaux utilise dans la base."""
        self.reseau_id = reseau_id

    def to_station(self, data: dict[str, Any]) -> Station:
        """Convertit un element du flux station_information en Station."""
        names = data["name"]
        if not names:
            raise ValueError("La station doit avoir au moins un nom.")
        name = names[0]["text"]  # Nom par défaut

        for item in names:
            if item["language"] == "fr":
                name = item["text"]
            break

        return Station(
            station_id=data["station_id"],
            reseau_id=self.reseau_id,
            name=name,
            latitude=data["lat"],
            longitude=data["lon"],
            capacite=data["capacity"],
            adresse=data.get("address"),
        )

    def to_station_status(self, data: dict[str, Any]) -> StationStatus:
        """Convertit un element du flux station_status en StationStatus."""
        nb_velos_elec = sum(
            vehicle_type["count"]
            for vehicle_type in data["vehicle_types_available"]
            if vehicle_type["vehicle_type_id"] == "electric"
        )
        return StationStatus(
            id_station=data["station_id"],
            horodatage=datetime.fromisoformat(data["last_reported"]),
            nb_velos_dispos=data["num_vehicles_available"],
            nb_velos_elec_dispos=nb_velos_elec,
            nb_places_dispos=data["num_docks_available"],
            est_installee=data["is_installed"],
            permet_retour=data["is_returning"],
            permet_emprunt=data["is_renting"],
        )
