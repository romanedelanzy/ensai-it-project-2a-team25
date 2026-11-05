from utils.api_client import api_client


def get_favorite_station_ids() -> set[str] | None:
    """Récupère les identifiants des stations favorites de l'utilisateur."""

    response = api_client.get("/favoris")

    if not response or response["status_code"] != 200:
        return None

    return {
        str(favorite["station_id"])
        for favorite in response["data"]
    }


def add_favorite(station_id: str) -> bool:
    """Ajoute une station aux favoris."""

    response = api_client.post(f"/favoris/{station_id}")

    return bool(response and response["status_code"] == 201)


def remove_favorite(station_id: str) -> bool:
    """Retire une station des favoris."""

    response = api_client.delete(f"/favoris/{station_id}")

    return bool(response and response["status_code"] == 200)