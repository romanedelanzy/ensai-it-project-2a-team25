
"""
Page Streamlit de consultation détaillée d'une station.

Affiche les informations générales, le dernier statut,
l'évolution de la disponibilité, les favoris et la fiabilité.
"""

import streamlit as st
import pandas as pd
from urllib.parse import quote

from utils.api_client import api_client
from utils.favoris import get_favorite_station_ids, add_favorite


STATE_UNKNOWN = "Inconnue"
STATE_EMPTY = "Vide"
STATE_FULL = "Saturée"
STATE_UNAVAILABLE = "Non opérationnelle"
STATE_OK = "Disponible"

STATE_BADGE_COLORS = {
    STATE_UNKNOWN: "gray",
    STATE_EMPTY: "red",
    STATE_FULL: "orange",
    STATE_UNAVAILABLE: "orange",
    STATE_OK: "green",
}


def get_station_state(status) -> str:
    """Détermine l'état actuel d'une station."""

    if status is None:
        return STATE_UNKNOWN

    if not status["est_installee"]:
        return STATE_UNAVAILABLE

    if not status["permet_emprunt"] or not status["permet_retour"]:
        return STATE_UNAVAILABLE

    if status["nb_velos_dispos"] == 0:
        return STATE_EMPTY

    if status["nb_places_dispos"] == 0:
        return STATE_FULL

    return STATE_OK


def get_fill_rate(capacite: int, status) -> float | None:
    """Calcule le taux de remplissage d'une station."""

    if status is None or capacite <= 0:
        return None

    return (capacite - status["nb_places_dispos"]) / capacite


def search_stations(name: str):
    """Recherche les stations par leur nom."""

    if len(name.strip()) < 3:
        return []

    response = api_client.get(
        f"/station/?name={quote(name.strip())}"
    )

    if not response or response["status_code"] != 200:
        return None

    return response["data"]


def get_current_status(station_id: str):
    """Récupère le dernier statut d'une station."""

    response = api_client.get(
        f"/station/{station_id}/status"
    )

    if response and response["status_code"] == 200:
        return response["data"]

    return None


def get_availability_history(station_id: str, period: str):
    """Récupère l'évolution de la disponibilité d'une station."""

    response = api_client.get(
        f"/station/{station_id}/availability-history?period={period}"
    )

    if response and response["status_code"] == 200:
        return response["data"]

    return None


def display_favorite_button(station_id: str):
    """Affiche le bouton d'ajout aux favoris."""

    favorite_ids = get_favorite_station_ids()

    if favorite_ids is None:
        st.warning("Impossible de récupérer vos favoris.")
        return

    if station_id in favorite_ids:
        st.caption("⭐ Cette station est déjà dans vos favoris.")
        return

    if st.button(
        "☆ Ajouter aux favoris",
        key=f"detail_add_favorite_{station_id}",
    ):
        if add_favorite(station_id):
            st.success("Station ajoutée à vos favoris !")
            st.rerun()
        else:
            st.error("Impossible d'ajouter cette station aux favoris.")


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

    st.subheader("Score de fiabilité")

    st.metric(
        "Fiabilité actuelle",
        f"{reliability['current_score']:.1%}",
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


def display_station_information(station: dict):
    """Affiche les informations générales de la station."""

    st.subheader(station["name"])

    st.write(f"**Identifiant :** {station['station_id']}")
    st.write(f"**Réseau :** {station['reseau_id']}")
    st.write(f"**Adresse :** {station['adresse'] or 'Non renseignée'}")
    st.write(
        f"**Coordonnées :** "
        f"{station['latitude']}, {station['longitude']}"
    )

    display_favorite_button(station["station_id"])

    # Affichage de la fiabilité à la demande
    reliability_key = f"detail_reliability_{station['station_id']}"

    if st.button(
        "Masquer la fiabilité"
        if st.session_state.get(reliability_key, False)
        else "Afficher la fiabilité",
        key=f"toggle_{reliability_key}",
    ):
        st.session_state[reliability_key] = not st.session_state.get(
            reliability_key, False
        )

    if st.session_state.get(reliability_key, False):
        display_reliability(station["station_id"])


def display_current_status(station: dict, status: dict | None):
    """Affiche les indicateurs du dernier statut."""

    st.subheader("État actuel")

    if status is None:
        st.warning("Aucun relevé disponible pour cette station.")
        return

    state = get_station_state(status)

    st.badge(
        state,
        color=STATE_BADGE_COLORS[state]
    )

    capacite = station["capacite"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Vélos disponibles", status["nb_velos_dispos"])
    col2.metric("Vélos électriques", status["nb_velos_elec_dispos"])
    col3.metric("Places disponibles", status["nb_places_dispos"])
    col4.metric("Capacité", capacite)

    fill = get_fill_rate(capacite, status)

    if fill is not None:
        st.write("**Taux de remplissage**")
        st.progress(fill)
        st.write(f"{fill:.1%}")

    st.caption(f"Dernier relevé : {status['horodatage']}")

    with st.expander("Détails du statut"):
        st.write(
            f"**Station installée :** "
            f"{'Oui' if status['est_installee'] else 'Non'}"
        )
        st.write(
            f"**Emprunts autorisés :** "
            f"{'Oui' if status['permet_emprunt'] else 'Non'}"
        )
        st.write(
            f"**Retours autorisés :** "
            f"{'Oui' if status['permet_retour'] else 'Non'}"
        )


def display_availability_history(station_id: str):
    """Affiche l'évolution de la disponibilité sur une période."""

    st.subheader("Évolution de la disponibilité")

    period = st.selectbox(
        "Période étudiée",
        options=["24h", "7j", "30j"],
        format_func=lambda p: {
            "24h": "Dernières 24 heures",
            "7j": "7 derniers jours",
            "30j": "30 derniers jours",
        }[p],
        key="availability_period",
    )

    history = get_availability_history(station_id, period)

    if history is None:
        st.error("Impossible de récupérer l'historique de disponibilité.")
        return

    if not history:
        st.info("Aucun relevé disponible sur cette période.")
        return

    df = pd.DataFrame(
        history,
        columns=["Date", "Disponibilité"]
    )

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")

    st.line_chart(
        df,
        y="Disponibilité",
        use_container_width=True,
        height=300,
    )

    st.caption("1 = station disponible | 0 = station indisponible")


def display_station_consultation():
    """Page de consultation détaillée d'une station."""

    st.title("Consultation d'une station")

    st.write(
        "Recherchez une station par son nom "
        "pour consulter ses informations."
    )

    search = st.text_input(
        "Nom de la station",
        placeholder="Saisissez au moins 3 caractères...",
        key="station_search"
    )

    if len(search.strip()) < 3:
        st.info("Saisissez au moins 3 caractères pour rechercher.")
        return

    stations = search_stations(search)

    if stations is None:
        st.error("Impossible de récupérer les stations.")
        return

    if not stations:
        st.warning("Aucune station trouvée.")
        return

    selected_station = st.selectbox(
        "Stations trouvées",
        options=stations,
        format_func=lambda s: f"{s['name']} ({s['station_id']})",
        key="consulted_station",
    )

    if selected_station is None:
        return

    st.divider()

    display_station_information(selected_station)

    st.divider()

    status = get_current_status(selected_station["station_id"])
    display_current_status(selected_station, status)

    st.divider()

    display_availability_history(selected_station["station_id"])


display_station_consultation()
