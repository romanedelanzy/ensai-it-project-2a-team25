class Station:
    """
    Représente une station de vélos en libre-service.
    """

    def __init__(self, station_id: str, reseau_id: int, name: str,
                 latitude: float, longitude: float, capacite: int,
                 adresse: str = None):
        # conditions station_id
        if not isinstance(station_id, str):
            raise TypeError(
                f"station_id doit être une chaîne de caractères, "
                f"reçu {type(station_id).__name__}"
            )
        if len(station_id) == 0:
            raise ValueError("station_id ne peut pas être vide")
        if len(station_id) > 50:
            raise ValueError(
                f"station_id ne doit pas dépasser 50 caractères "
                f"(reçu {len(station_id)})"
            )
        # conditions reseau_id
        if not isinstance(reseau_id, int) or isinstance(reseau_id, bool):
            raise TypeError(
                f"reseau_id doit être un entier, "
                f"reçu {type(reseau_id).__name__}"
            )
        # conditions name
        if not isinstance(name, str):
            raise TypeError(
                f"name doit être une chaîne de caractères, "
                f"reçu {type(name).__name__}"
            )
        if len(name) == 0:
            raise ValueError("name ne peut pas être vide")
        if len(name) > 150:
            raise ValueError(
                f"name ne doit pas dépasser 150 caractères "
                f"(reçu {len(name)})"
            )
        # conditions latitude
        if not isinstance(latitude, (int, float)) or isinstance(latitude, bool):
            raise TypeError(
                f"latitude doit être un nombre, "
                f"reçu {type(latitude).__name__}"
            )
        if not -90 <= latitude <= 90:
            raise ValueError(
                f"latitude doit être comprise entre -90 et 90 "
                f"(reçu {latitude})"
            )
        # conditions longitude
        if not isinstance(longitude, (int, float)) or isinstance(longitude, bool):
            raise TypeError(
                f"longitude doit être un nombre, "
                f"reçu {type(longitude).__name__}"
            )
        if not -180 <= longitude <= 180:
            raise ValueError(
                f"longitude doit être comprise entre -180 et 180 "
                f"(reçu {longitude})"
            )
        # conditions capacite
        if not isinstance(capacite, int) or isinstance(capacite, bool):
            raise TypeError(
                f"capacite doit être un entier, "
                f"reçu {type(capacite).__name__}"
            )
        if capacite < 0:
            raise ValueError(
                f"capacite ne peut pas être négative (reçu {capacite})"
            )

        self.station_id = station_id
        self.reseau_id = reseau_id
        self.name = name
        self.adresse = adresse
        self.latitude = latitude
        self.longitude = longitude
        self.capacite = capacite

    def __repr__(self):
        return (f"Station(id={self.station_id}, name='{self.name}', "
                f"capacite={self.capacite})")

#à voir si les prochaines méthodes sont utiles
    def to_dict(self) -> dict:
        """Convertit l'objet Station en dictionnaire (utile pour le DAO/API)."""
        return {
            "station_id": self.station_id,
            "reseau_id": self.reseau_id,
            "name": self.name,
            "adresse": self.adresse,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "capacite": self.capacite,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Station":
        """Construit une Station à partir d'un dictionnaire (ex: résultat SQL ou JSON API)."""
        return cls(
            station_id=data["station_id"],
            reseau_id=data["reseau_id"],
            name=data["name"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            capacite=data["capacite"],
            adresse=data.get("adresse"),
        )