from datetime import datetime

from pydantic import BaseModel


class StationReadModel(BaseModel):
    """Station data returned by the API."""

    station_id: str
    reseau_id: int
    name: str
    adresse: str | None = None
    latitude: float
    longitude: float
    capacite: int


class StationStatusReadModel(BaseModel):
    """Status of a station at a given time, returned by the API."""

    id_station: str
    horodatage: datetime
    nb_velos_dispos: int
    nb_velos_elec_dispos: int
    nb_places_dispos: int
    est_installee: bool
    permet_retour: bool
    permet_emprunt: bool