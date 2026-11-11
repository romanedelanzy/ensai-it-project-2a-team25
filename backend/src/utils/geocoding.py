import requests


def geocode_bordeaux_address(address: str) -> tuple[float, float]:
    """Convertit une adresse Bordeaux en coordonnées GPS."""
    cleaned = (address or "").strip()
    if not cleaned:
        raise ValueError("L'adresse ne peut pas être vide.")

    query = f"{cleaned}, Bordeaux, France"
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": query,
            "format": "jsonv2",
            "limit": 1,
            "addressdetails": 1,
        },
        headers={"User-Agent": "ensai-it-project-2a-team25"},
        timeout=10,
    )
    response.raise_for_status()

    result = response.json()
    if not result:
        raise ValueError("Aucune adresse Bordeaux n'a été trouvée.")

    first = result[0]
    latitude = float(first["lat"])
    longitude = float(first["lon"])

    if not 44.7 <= latitude <= 45.0 or not -0.7 <= longitude <= -0.4:
        raise ValueError("L'adresse doit se trouver dans l'agglomération de Bordeaux.")

    return latitude, longitude
