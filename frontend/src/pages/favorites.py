"""
Page Streamlit des stations favorites (Menu 4).

Regroupe les stations marquées comme favorites par l'utilisateur, avec leur état actuel
affiché directement.

Endpoints utilisés :
    GET /favoris
    GET /stations
    GET /stations/status
"""

import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger
from utils.station_display import load_stations_with_status

st.title("Mes stations favorites")
logger = get_page_logger("favorites")

check_authentification()

response = api_client.get("/favoris/")

if not response or response["status_code"] != 200:
    st.error("Erreur lors du chargement des favoris")
    st.stop()

favorite_ids = [f["station_id"] for f in response["data"]]

if not favorite_ids:
    st.info("Vous n'avez pas encore de station favorite.")
    if st.button("Retour au menu", type="primary"):
        st.switch_page("pages/main_menu.py")
    st.stop()

stations, has_status = load_stations_with_status()

if stations is None:
    st.error("Erreur lors du chargement des stations")
    st.stop()

favorites = stations[stations["station_id"].isin(favorite_ids)]

if has_status:
    colonnes = {
        "name": "Station",
        "etat": "État",
        "nb_velos_dispos": "Vélos disponibles",
        "nb_velos_elec_dispos": "dont électriques",
        "nb_places_dispos": "Places libres",
    }
else:
    st.info("Les disponibilités en temps réel ne sont pas encore disponibles.")
    colonnes = {"name": "Station", "adresse": "Adresse"}

st.dataframe(favorites[list(colonnes)].rename(columns=colonnes), hide_index=True)

noms = dict(zip(favorites["station_id"], favorites["name"]))
station_id = st.selectbox("Choisir une station", list(noms), format_func=lambda sid: noms[sid])

if st.button("Voir le détail"):
    logger.info("Open the detail of a favorite")
    st.session_state["selected_station_id"] = station_id
    st.switch_page("pages/station_detail.py")

if st.button("Retour au menu", type="primary"):
    st.switch_page("pages/main_menu.py")