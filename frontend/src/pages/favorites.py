"""
Page Streamlit des stations favorites (Menu 4).

Regroupe les stations marquées comme favorites par l'utilisateur, avec leur état actuel
affiché directement.

Endpoints utilisés :
    GET /favoris
    GET /stations
    GET /stations/status
"""

"""
Page Streamlit des stations favorites de l'utilisateur.
Permet de consulter les stations favorites et de les retirer de la liste.
"""

import streamlit as st

from utils.api_client import api_client
from utils.favoris import get_favorite_station_ids, remove_favorite


def get_station(station_id: str):
    """Récupère les informations d'une station."""

    response = api_client.get(f"/station/{station_id}")

    if response and response["status_code"] == 200:
        return response["data"]

    return None


def get_current_status(station_id: str):
    """Récupère le dernier statut d'une station."""

    response = api_client.get(
        f"/station/{station_id}/status"
    )

    if response and response["status_code"] == 200:
        return response["data"]

    return None


def display_favorites():
    """Affiche les stations favorites de l'utilisateur."""

    st.title("⭐ Mes stations favorites")

    favorite_ids = get_favorite_station_ids()

    if favorite_ids is None:
        st.error("Impossible de récupérer vos favoris.")
        return

    if not favorite_ids:
        st.info(
            "Vous n'avez pas encore de station favorite. "
            "Rendez-vous dans la liste des stations pour en ajouter !"
        )
        return

    st.write(f"Vous avez {len(favorite_ids)} station(s) favorite(s).")

    for station_id in sorted(favorite_ids):

        station = get_station(station_id)

        if station is None:
            st.warning(
                f"Impossible de récupérer la station {station_id}."
            )
            continue

        with st.container(border=True):

            st.subheader(station["name"])

            st.write(f"**Identifiant :** {station['station_id']}")
            st.write(f"**Réseau :** {station['reseau_id']}")
            st.write(
                f"**Adresse :** "
                f"{station['adresse'] or 'Non renseignée'}"
            )
            st.write(f"**Capacité :** {station['capacite']} vélos")

            status = get_current_status(station_id)

            if status is not None:
                st.write(
                    f"**Vélos disponibles :** "
                    f"{status['nb_velos_dispos']}"
                )
                st.write(
                    f"**Places disponibles :** "
                    f"{status['nb_places_dispos']}"
                )
            else:
                st.caption("Aucun relevé disponible.")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "Voir la station",
                    key=f"view_favorite_{station_id}",
                ):
                    st.session_state["selected_station_id"] = station_id
                    st.switch_page("pages/station_status.py")

            with col2:
                if st.button(
                    "Retirer des favoris",
                    key=f"remove_favorite_{station_id}",
                    type="secondary",
                ):
                    if remove_favorite(station_id):
                        st.success("Station retirée de vos favoris.")
                        st.rerun()
                    else:
                        st.error(
                            "Impossible de retirer cette station des favoris."
                        )


display_favorites()