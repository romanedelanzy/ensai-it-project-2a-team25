from dataclasses import dataclass
from datetime import datetime


@dataclass
class StationStatus:
    """Représente l'état ponctuel d'une station"""

    id_station: int
    horodatage: datetime
    nb_velos_dispos: int
    nb_velos_elec_dispos: int
    nb_places_dispos: int
    est_installee: bool
    permet_retour: bool
    permet_emprunt: bool

    def __post_init__(self):
        if self.nb_velos_dispos < 0 or self.nb_places_dispos < 0:
            raise ValueError("le nombre de vélos ou de places disponibles ne peut être négatif")
        if self.nb_velos_elec_dispos > self.nb_velos_dispos:
            raise ValueError("il ne peut y avoir plus de vélos électriques que de vélos au total")
