
import streamlit as st

from utils.api_client import api_client


def display_station_status():

    st.title("Dernier relevé de la station")

    station_id = st.session_state.get("selected_station_id")

    if not station_id:
        st.warning("Aucune station sélectionnée.")
        return

    response = api_client.get(
        f"/station/{station_id}/status"
    )

    if not response or response["status_code"] != 200:
        st.error("Impossible de récupérer le dernier relevé.")
        return

    status = response["data"]

    st.subheader(f"Station : {station_id}")

    st.write(f"**Date du relevé :** {status['horodatage']}")

    st.write(
        f"**Vélos disponibles :** "
        f"{status['nb_velos_dispos']}"
    )

    st.write(
        f"**Vélos électriques disponibles :** "
        f"{status['nb_velos_elec_dispos']}"
    )

    st.write(
        f"**Places disponibles :** "
        f"{status['nb_places_dispos']}"
    )

    st.write(
        f"**Station installée :** "
        f"{'Oui' if status['est_installee'] else 'Non'}"
    )

    st.write(
        f"**Emprunt autorisé :** "
        f"{'Oui' if status['permet_emprunt'] else 'Non'}"
    )

    st.write(
        f"**Retour autorisé :** "
        f"{'Oui' if status['permet_retour'] else 'Non'}"
    )

    if st.button("Retour aux stations"):
        st.switch_page("pages/station_display.py")


display_station_status()
