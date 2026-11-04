"""
Fonctions utilitaires d'affichage des stations pour les pages Streamlit :
état d'une station, couleurs, taux de remplissage et chargement des stations
avec leur dernier relevé.
"""

import pandas as pd

from utils.api_client import api_client

STATE_EMPTY = "Vide"
STATE_FULL = "Saturée"
STATE_OK = "Fonctionnelle"
STATE_UNKNOWN = "Inconnue"

# Couleurs des points sur la carte (st.map)
STATE_COLORS = {
    STATE_EMPTY: "#e74c3c",
    STATE_FULL: "#e67e22",
    STATE_OK: "#2ecc71",
    STATE_UNKNOWN: "#95a5a6",
}

# Couleurs des badges (st.badge)
STATE_BADGE_COLORS = {
    STATE_EMPTY: "red",
    STATE_FULL: "orange",
    STATE_OK: "green",
    STATE_UNKNOWN: "gray",
}


def station_state(status) -> str:
    """Donne l'état d'une station à partir de son dernier relevé.
    Vide s'il n'y a aucun vélo disponible, saturée s'il n'y a plus de place libre,
    fonctionnelle dans les autres cas.
    Args:
        status: dernier relevé de la station (dict) ou None s'il n'y en a pas.
    Returns:
        str: 'Vide', 'Saturée', 'Fonctionnelle' ou 'Inconnue'.
    """
    if status is None:
        return STATE_UNKNOWN
    if status["nb_velos_dispos"] == 0:
        return STATE_EMPTY
    if status["nb_places_dispos"] == 0:
        return STATE_FULL
    return STATE_OK


def fill_rate(capacite: int, status) -> float | None:
    """Taux de remplissage : vélos disponibles divisé par la capacité (None si inconnu)."""
    if status is None or capacite == 0:
        return None
    return status["nb_velos_dispos"] / capacite


def is_operational(status) -> bool:
    """Une station est opérationnelle si elle est installée, loue et accepte les retours."""
    return (
        status is not None
        and bool(status["est_installee"])
        and bool(status["permet_emprunt"])
        and bool(status["permet_retour"])
    )


def load_stations_with_status() -> tuple[pd.DataFrame | None, bool]:
    """Charge les stations et leur dernier relevé, fusionnés dans un DataFrame.
    Returns:
        tuple: (DataFrame, True si les relevés sont disponibles).
            Le DataFrame vaut None si les stations n'ont pas pu être chargées.
            Il contient une colonne 'etat' (Vide, Saturée, Fonctionnelle ou Inconnue).
    """
    response = api_client.get("/stations/")
    if not response or response["status_code"] != 200:
        return None, False

    stations = pd.DataFrame(response["data"])
    if stations.empty:
        return stations, False

    status_response = api_client.get("/stations/status")
    has_status = bool(
        status_response and status_response["status_code"] == 200 and status_response["data"]
    )

    if has_status:
        statuses = pd.DataFrame(status_response["data"]).rename(
            columns={"id_station": "station_id"}
        )
        stations = stations.merge(statuses, on="station_id", how="left")
        stations["etat"] = stations.apply(
            lambda row: station_state(None if pd.isna(row["nb_velos_dispos"]) else row), axis=1
        )
    else:
        stations["etat"] = STATE_UNKNOWN

    return stations, has_status