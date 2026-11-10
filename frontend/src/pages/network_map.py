
import streamlit as st
import folium
from streamlit_folium import st_folium

from utils.api_client import api_client


# --------------------------------------------------
# Configuration
# --------------------------------------------------

st.title("Carte des stations")
st.write("Visualisation géographique des stations du réseau Le Vélo de Bordeaux.")


# --------------------------------------------------
# Récupération des données
# --------------------------------------------------

def get_stations():
    """Récupère toutes les stations depuis l'API."""

    response = api_client.get("/station/")

    if response and response.get("status_code") == 200:
        return response.get("data", [])

    return None


# --------------------------------------------------
# Construction de la carte
# --------------------------------------------------

def create_station_map(stations):
    """Construit une carte Folium contenant toutes les stations."""

    carte = folium.Map(
        location=[44.8378, -0.5792],
        zoom_start=13,
        tiles="OpenStreetMap"
    )

    for station in stations:

        latitude = station.get("latitude")
        longitude = station.get("longitude")

        # On ignore les stations sans coordonnées
        if latitude is None or longitude is None:
            continue

        folium.Marker(
            location=[latitude, longitude],
            tooltip=station.get("name", "Station inconnue"),
            popup=folium.Popup(
                f"""
                <b>{station.get('name', 'Station inconnue')}</b><br>
                Adresse : {station.get('adresse', 'Non renseignée')}<br>
                Capacité : {station.get('capacite', 'Inconnue')}
                """,
                max_width=300
            ),
            icon=folium.Icon(
                color="blue",
                icon="bicycle",
                prefix="fa"
            )
        ).add_to(carte)

    return carte


# --------------------------------------------------
# Affichage
# --------------------------------------------------

stations = get_stations()

if stations is None:
    st.error("Impossible de récupérer les stations.")

elif not stations:
    st.warning("Aucune station disponible.")

else:
    st.success(f"{len(stations)} stations récupérées.")

    carte = create_station_map(stations)

    st_folium(
        carte,
        width=None,
        height=650,
        use_container_width=True,
        key="network_map"
    )
