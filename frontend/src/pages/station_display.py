"""
Affichage des stations du réseau avec pagination
et accès au dernier relevé de chaque station.
"""

import pandas as pd
import streamlit as st

from utils.api_client import api_client
from utils.favoris import get_favorite_station_ids, add_favorite


STATE_EMPTY = "Vide"
STATE_FULL = "Saturée"
STATE_OK = "Fonctionnelle"
STATE_UNKNOWN = "Inconnue"

STATIONS_PER_PAGE = 10

STATE_BADGE_COLORS = {
    STATE_EMPTY: "red",
    STATE_FULL: "orange",
    STATE_OK: "green",
    STATE_UNKNOWN: "gray",
}


def station_state(status) -> str:
    if status is None:
        return STATE_UNKNOWN

    if status["nb_velos_dispos"] == 0:
        return STATE_EMPTY

    if status["nb_places_dispos"] == 0:
        return STATE_FULL

    return STATE_OK


def fill_rate(capacite: int, status) -> float | None:
    if status is None or capacite == 0:
        return None

    return status["nb_velos_dispos"] / capacite


def is_operational(status) -> bool:
    return (
        status is not None
        and bool(status["est_installee"])
        and bool(status["permet_emprunt"])
        and bool(status["permet_retour"])
    )


def load_stations_with_status() -> tuple[pd.DataFrame | None, bool]:
    """Charge les stations et leur dernier relevé."""

    response = api_client.get("/station/")

    if not response or response["status_code"] != 200:
        return None, False

    stations = pd.DataFrame(response["data"])

    if stations.empty:
        return stations, False

    statuses = []

    for station_id in stations["station_id"]:
        status_response = api_client.get(
            f"/station/{station_id}/status"
        )

        if status_response and status_response["status_code"] == 200:
            statuses.append(status_response["data"])

        elif status_response and status_response["status_code"] == 404:
            continue

        else:
            return stations.assign(etat=STATE_UNKNOWN), False

    if statuses:
        status_df = pd.DataFrame(statuses).rename(
            columns={"id_station": "station_id"}
        )

        stations = stations.merge(
            status_df,
            on="station_id",
            how="left"
        )

        stations["etat"] = stations.apply(
            lambda row: station_state(
                None if pd.isna(row["nb_velos_dispos"]) else row
            ),
            axis=1,
        )

        has_status = True

    else:
        stations["etat"] = STATE_UNKNOWN
        has_status = False

    return stations, has_status


def display_stations():
    """Affiche les stations avec une pagination."""

    st.title("Stations du réseau")

    stations, has_status = load_stations_with_status()

    if stations is None:
        st.error("Impossible de récupérer les stations.")
        return

    if stations.empty:
        st.info("Aucune station disponible.")
        return

    if not has_status:
        st.warning(
            "Les derniers relevés ne sont pas disponibles."
        )

    # Récupération des favoris de l'utilisateur connecté
    favorite_ids = get_favorite_station_ids()

    if favorite_ids is None:
        st.warning(
            "Impossible de récupérer vos favoris. "
            "L'ajout aux favoris est temporairement indisponible."
        )
        favorite_ids = set()

    st.write(f"Nombre total de stations : {len(stations)}")

    # Pagination
    total_pages = (
        len(stations) + STATIONS_PER_PAGE - 1
    ) // STATIONS_PER_PAGE

    page = st.selectbox(
        "Page",
        options=list(range(1, total_pages + 1)),
        key="stations_page",
    )

    start = (page - 1) * STATIONS_PER_PAGE
    end = start + STATIONS_PER_PAGE

    page_stations = stations.iloc[start:end]

    # Affichage des stations
    for _, station in page_stations.iterrows():

        station_id = station["station_id"]

        with st.container(border=True):

            st.subheader(station["name"])

            state = station["etat"]

            st.badge(
                state,
                color=STATE_BADGE_COLORS[state]
            )

            st.write(f"**Identifiant :** {station_id}")
            st.write(f"**Réseau :** {station['reseau_id']}")
            st.write(
                f"**Adresse :** "
                f"{station['adresse'] or 'Non renseignée'}"
            )
            st.write(f"**Capacité :** {station['capacite']} vélos")

            st.write(
                f"**Coordonnées :** "
                f"{station['latitude']}, {station['longitude']}"
            )

            if "nb_velos_dispos" in station.index and pd.notna(
                station.get("nb_velos_dispos")
            ):
                st.write(
                    f"**Vélos disponibles :** "
                    f"{int(station['nb_velos_dispos'])}"
                )

                st.write(
                    f"**Places disponibles :** "
                    f"{int(station['nb_places_dispos'])}"
                )

            # Bouton d'ajout aux favoris
            if station_id in favorite_ids:
                st.caption("⭐ Déjà dans vos favoris")

            elif st.button(
                "☆ Ajouter aux favoris",
                key=f"add_favorite_{station_id}",
            ):
                if add_favorite(station_id):
                    st.success("Station ajoutée à vos favoris !")
                    st.rerun()
                else:
                    st.error("Impossible d'ajouter cette station aux favoris.")

            # Accès au dernier relevé
            if st.button(
                "Voir le dernier relevé",
                key=f"status_{station_id}",
                disabled=(
                    "nb_velos_dispos" not in station.index
                    or pd.isna(station.get("nb_velos_dispos"))
                ),
            ):
                st.session_state["selected_station_id"] = station_id
                st.switch_page("pages/station_status.py")


display_stations()