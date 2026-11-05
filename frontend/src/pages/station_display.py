
"""
Affichage des stations du réseau avec pagination,
accès au dernier relevé, favoris et fiabilité.
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


def get_reliability(station_id: str):
    """Récupère les indicateurs de fiabilité d'une station."""

    response = api_client.get(f"/reliability/{station_id}")

    if response and response["status_code"] == 200:
        return response["data"]

    return None


def display_reliability(station_id: str):
    """Affiche le score et l'historique de fiabilité."""

    reliability = get_reliability(station_id)

    if reliability is None:
        st.error("Impossible de récupérer les indicateurs de fiabilité.")
        return

    score = reliability["current_score"]

    st.subheader("Score de fiabilité")

    st.metric(
        "Fiabilité actuelle",
        f"{score:.1%}",
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Temps passé vide",
        f"{reliability['empty_percentage']:.1%}",
    )

    col2.metric(
        "Temps passé saturé",
        f"{reliability['saturation_percentage']:.1%}",
    )

    col3, col4 = st.columns(2)

    empty_duration = reliability["average_empty_duration"]
    saturated_duration = reliability["average_saturated_duration"]

    col3.metric(
        "Durée moyenne des épisodes vides",
        f"{empty_duration:.2f} h"
        if empty_duration is not None else "Non disponible",
    )

    col4.metric(
        "Durée moyenne des épisodes saturés",
        f"{saturated_duration:.2f} h"
        if saturated_duration is not None else "Non disponible",
    )

    st.subheader("Historique du score")

    evolution = reliability["score_evolution"]

    if not evolution:
        st.info("Aucun historique de fiabilité disponible.")
        return

    df = pd.DataFrame(evolution)

    df["date"] = pd.to_datetime(df["date"])
    df["score"] = df["score"] * 100

    df = df.rename(
        columns={
            "date": "Date",
            "score": "Score de fiabilité (%)",
        }
    )

    df = df.set_index("Date")

    st.line_chart(
        df,
        y="Score de fiabilité (%)",
        use_container_width=True,
        height=250,
    )


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
        st.warning("Les derniers relevés ne sont pas disponibles.")

    favorite_ids = get_favorite_station_ids()

    if favorite_ids is None:
        st.warning("Impossible de récupérer vos favoris.")
        favorite_ids = set()

    st.write(f"Nombre total de stations : {len(stations)}")

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

            # Favoris
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

            # Dernier relevé
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

            # Fiabilité
            reliability_key = f"reliability_{station_id}"

            if st.button(
                "Masquer la fiabilité"
                if st.session_state.get("reliability_station_id") == station_id
                else "Afficher la fiabilité",
                key=f"show_reliability_{station_id}",
            ):
                if st.session_state.get("reliability_station_id") == station_id:
                    st.session_state["reliability_station_id"] = None
                else:
                    st.session_state["reliability_station_id"] = station_id

            if st.session_state.get("reliability_station_id") == station_id:
                display_reliability(station_id)


display_stations()
