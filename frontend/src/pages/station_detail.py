"""
Page Streamlit du détail d'une station (Menu 3).

Affiche l'état actuel d'une station, sa capacité, son taux de remplissage, l'évolution
de sa disponibilité sur 24h, 7 jours ou 30 jours, son score de fiabilité, et permet
de l'ajouter ou de la retirer des favoris.

Endpoints utilisés :
    GET /stations
    GET /stations/{station_id}/status
    GET /stations/{station_id}/history?period=
    GET /reliability/{station_id}
    GET /favoris
    POST /favoris/{station_id}
    DELETE /favoris/{station_id}
"""

import pandas as pd
import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger
from utils.station_display import STATE_BADGE_COLORS, fill_rate, is_operational, station_state

st.title("Détail d'une station")
logger = get_page_logger("station_detail")

check_authentification()

response = api_client.get("/stations/")

if not response or response["status_code"] != 200:
    st.error("Erreur lors du chargement des stations")
    st.stop()

stations = {s["station_id"]: s for s in response["data"]}

if not stations:
    st.warning("Aucune station disponible")
    st.stop()

ids = list(stations)
selected = st.session_state.get("selected_station_id")
station_id = st.selectbox(
    "Station",
    ids,
    index=ids.index(selected) if selected in ids else 0,
    format_func=lambda sid: stations[sid]["name"],
)
st.session_state["selected_station_id"] = station_id
station = stations[station_id]

st.subheader(station["name"])
if station.get("adresse"):
    st.caption(station["adresse"])

# --- État actuel ---
status_response = api_client.get(f"/stations/{station_id}/status")
status = (
    status_response["data"]
    if status_response and status_response["status_code"] == 200
    else None
)

etat = station_state(status)
st.badge(etat, color=STATE_BADGE_COLORS[etat])

if status:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Vélos disponibles", status["nb_velos_dispos"])
    col2.metric("dont électriques", status["nb_velos_elec_dispos"])
    col3.metric("Places libres", status["nb_places_dispos"])
    col4.metric("Capacité", station["capacite"])

    taux = fill_rate(station["capacite"], status)
    if taux is not None:
        st.progress(min(taux, 1.0), text=f"Taux de remplissage : {taux:.0%}")

    st.write("✅ Station opérationnelle" if is_operational(status) else "⚠️ Station non opérationnelle")
else:
    st.warning("Aucun relevé disponible pour cette station")

# --- Historique ---
st.subheader("Évolution de la disponibilité")
period = st.radio("Période", ["24h", "7j", "30j"], horizontal=True)

history_response = api_client.get(f"/stations/{station_id}/history?period={period}")

if history_response and history_response["status_code"] == 200 and history_response["data"]:
    history = pd.DataFrame(history_response["data"])
    history["horodatage"] = pd.to_datetime(history["horodatage"])
    st.line_chart(history, x="horodatage", y=["nb_velos_dispos", "nb_places_dispos"])
else:
    st.info("Pas d'historique disponible sur cette période")

# --- Fiabilité ---
st.subheader("Fiabilité")
reliability_response = api_client.get(f"/reliability/{station_id}")

if reliability_response and reliability_response["status_code"] == 200:
    reliability = reliability_response["data"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Score de fiabilité", f"{reliability['score_fiabilite']:.1f}")
    col2.metric("Temps passé vide", f"{reliability['pct_temps_vide']:.0f} %")
    col3.metric("Temps passé saturée", f"{reliability['pct_temps_sature']:.0f} %")
else:
    st.info("Le score de fiabilité n'est pas encore disponible.")

# --- Favoris ---
st.subheader("Favoris")
favorites_response = api_client.get("/favoris/")

if favorites_response and favorites_response["status_code"] == 200:
    is_favorite = any(f["station_id"] == station_id for f in favorites_response["data"])

    if is_favorite:
        if st.button("Retirer des favoris"):
            logger.info("Remove a favorite")
            res = api_client.delete(f"/favoris/{station_id}")
            if res and res["status_code"] in (200, 204):
                st.rerun()
            else:
                st.error("Erreur lors du retrait des favoris")
    else:
        if st.button("Ajouter aux favoris"):
            logger.info("Add a favorite")
            res = api_client.post(f"/favoris/{station_id}", json={})
            if res and res["status_code"] in (200, 201):
                st.rerun()
            else:
                st.error("Erreur lors de l'ajout aux favoris")
else:
    st.info("Les favoris ne sont pas encore disponibles.")

if st.button("Retour à la carte", type="primary"):
    st.switch_page("pages/network_map.py")