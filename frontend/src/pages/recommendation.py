"""Page de recommandation de stations à proximité."""

import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

logger = get_page_logger("recommendation")
check_authentification()

st.title("Stations recommandées")

st.write(
    "Entrez une adresse à Bordeaux pour obtenir les stations les plus adaptées "
    "à proximité. Le backend convertit l’adresse en coordonnées puis calcule "
    "les meilleures stations."
)

address = st.text_input(
    "Adresse à Bordeaux",
    value="",
    placeholder="Ex. : 36 Rue Villedieu, Bordeaux",
)

col1, col2 = st.columns(2)
with col1:
    limite = st.number_input(
        "Nombre de stations",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )
with col2:
    rayon_km = st.number_input(
        "Rayon de recherche (km)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
    )

if st.button("Rechercher des stations"):
    if not address.strip():
        st.warning("Veuillez saisir une adresse à Bordeaux.")
        st.stop()

    params = {
        "address": address,
        "limite": int(limite),
        "rayon_km": float(rayon_km),
    }

    with st.spinner("Recherche des meilleures stations..."):
        response = api_client.get("/recommendation/", params=params, timeout=20)

    if not response or response["status_code"] != 200:
        logger.error("Recommendation request failed: %s", response)
        st.error(f"Erreur API : {response.get('data') if response else 'Aucune réponse'}")
        st.stop()

    stations = response["data"]

    if not stations:
        st.warning("Aucune station trouvée dans ce rayon pour cette adresse.")
        st.stop()

    st.success(f"{len(stations)} station(s) trouvée(s)")

    for item in stations:
        station = item["station"]

        with st.container(border=True):
            st.subheader(station["name"])
            st.write(f"**Adresse :** {station['adresse']}")
            st.write(f"**Distance :** {item['distance_km']} km")
            st.write(f"**Fiabilité :** {item['score_fiabilite']:.4f}")
            st.write(f"**Score de recommandation :** {item['score_recommandation']:.4f}")
            st.write(f"**Capacité :** {station['capacite']} vélos")
            st.write(f"**Coordonnées :** {station['latitude']}, {station['longitude']}")
