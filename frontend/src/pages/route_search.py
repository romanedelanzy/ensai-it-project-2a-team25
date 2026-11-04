"""
Page Streamlit de recherche d'itinéraire (Menu 5).

L'utilisateur saisit une adresse de départ et une adresse d'arrivée. L'application
propose une station de départ et une station d'arrivée adaptées (distance, vélos
disponibles, fiabilité, vélos électriques), le temps de trajet et la distance estimés,
et trace l'itinéraire sur la carte.

Endpoint utilisé :
    POST /routes
        corps : {"start_address": str, "end_address": str}
        réponse : {
            "start_station": {"name", "latitude", "longitude", "nb_velos_dispos"},
            "end_station": {"name", "latitude", "longitude", "nb_places_dispos"},
            "duration_min": float,
            "distance_m": float,
            "path": [{"latitude": float, "longitude": float}, ...],
        }
"""

import pandas as pd
import pydeck as pdk
import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.title("Recherche d'itinéraire")
logger = get_page_logger("route_search")

check_authentification()

start_address = st.text_input("Adresse de départ")
end_address = st.text_input("Adresse d'arrivée")

if st.button("Rechercher", disabled=not start_address or not end_address):
    logger.info("Search a route")
    with st.spinner("Recherche en cours..."):
        response = api_client.post(
            "/routes/", json={"start_address": start_address, "end_address": end_address}
        )

    if not response or response["status_code"] != 200:
        st.error(f"Erreur : {response['data'] if response else 'pas de réponse du serveur'}")
        st.stop()

    route = response["data"]
    start = route["start_station"]
    end = route["end_station"]

    col1, col2 = st.columns(2)
    col1.metric("Temps de trajet estimé", f"{route['duration_min']:.0f} min")
    col2.metric("Distance estimée", f"{route['distance_m'] / 1000:.1f} km")

    st.write(f"🚲 **Station de départ :** {start['name']} ({start['nb_velos_dispos']} vélos)")
    st.write(f"🅿️ **Station d'arrivée :** {end['name']} ({end['nb_places_dispos']} places libres)")

    path = [[p["longitude"], p["latitude"]] for p in route["path"]]
    stations = pd.DataFrame([start, end])

    layers = [
        pdk.Layer(
            "PathLayer",
            data=[{"path": path}],
            get_path="path",
            get_color=[0, 120, 255],
            width_min_pixels=4,
        ),
        pdk.Layer(
            "ScatterplotLayer",
            data=stations,
            get_position="[longitude, latitude]",
            get_fill_color=[231, 76, 60],
            get_radius=40,
        ),
    ]
    view = pdk.ViewState(
        latitude=stations["latitude"].mean(), longitude=stations["longitude"].mean(), zoom=13
    )
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view))

if st.button("Retour au menu", type="primary"):
    st.switch_page("pages/main_menu.py")