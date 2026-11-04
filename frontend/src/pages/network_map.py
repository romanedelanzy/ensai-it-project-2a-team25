"""
Page Streamlit de la carte du réseau (Menu 2).

Affiche toutes les stations sur une carte, avec le nombre de vélos disponibles et
de places libres, et permet de sélectionner une station pour en voir le détail.

Endpoints utilisés :
    GET /stations
    GET /stations/status
"""

import streamlit as st

from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger
from utils.station_display import STATE_COLORS, load_stations_with_status

st.title("Carte du réseau")
logger = get_page_logger("network_map")

check_authentification()

stations, has_status = load_stations_with_status()

if stations is None:
    st.error("Erreur lors du chargement des stations")
    st.stop()

if stations.empty:
    st.warning("Aucune station disponible")
    st.stop()

stations["color"] = stations["etat"].map(STATE_COLORS)
st.map(stations, latitude="latitude", longitude="longitude", color="color", size=30)

if has_status:
    st.caption("🟢 Fonctionnelle · 🔴 Vide · 🟠 Saturée")
    colonnes = {
        "name": "Station",
        "etat": "État",
        "nb_velos_dispos": "Vélos disponibles",
        "nb_places_dispos": "Places libres",
    }
else:
    st.info("Les disponibilités en temps réel ne sont pas encore disponibles.")
    colonnes = {"name": "Station", "adresse": "Adresse"}

st.dataframe(stations[list(colonnes)].rename(columns=colonnes), hide_index=True)

noms = dict(zip(stations["station_id"], stations["name"]))
station_id = st.selectbox("Choisir une station", list(noms), format_func=lambda sid: noms[sid])

if st.button("Voir le détail"):
    logger.info("Open the detail of a station")
    st.session_state["selected_station_id"] = station_id
    st.switch_page("pages/station_detail.py")

if st.button("Retour au menu", type="primary"):
    st.switch_page("pages/main_menu.py")