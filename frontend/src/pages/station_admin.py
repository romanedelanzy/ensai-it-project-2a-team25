"""
Page Streamlit d'administration des stations (consultation, création et suppression).
"""

import streamlit as st
import pandas as pd

from utils.api_client import api_client


def get_all_stations():
    """Récupère la liste complète des stations depuis l'API."""
    response = api_client.get("/station/list_stations/")

    if not response or response.get("status_code") != 200:
        return None

    return response.get("data") or []


def get_station_detail(station_id):
    """Récupère les détails d'une station via GET /station/{station_id}."""
    response = api_client.get(f"/station/{station_id}")
    if response and response.get("status_code") == 200 and isinstance(response.get("data"), dict):
        return response["data"]
    return None


def create_station(payload: dict):
    """Envoie une requête POST /station/ pour créer une station."""
    return api_client.post("/station/", json=payload)


def delete_station(station_id):
    """Envoie une requête DELETE /station/{station_id} pour supprimer une station."""
    return api_client.delete(f"/station/{station_id}")


def _extract_error_message(response, fallback: str) -> str:
    """Extrait un message d'erreur lisible depuis la réponse de l'API."""
    if not response:
        return fallback
    data = response.get("data")
    if isinstance(data, dict) and data.get("detail"):
        return str(data["detail"])
    status = response.get("status_code")
    return f"{fallback} (code {status})" if status else fallback


def _format_station_option(station: dict) -> str:
    """Formate une station comme dans station_detail : 'Nom (ID)'."""
    name = station.get("name", "Station sans nom")
    station_id = station.get("station_id", "")
    return f"{name} ({station_id})" if station_id != "" else str(name)


def render_stations_list(stations: list[dict]):
    """Affiche toutes les stations disponibles sous forme de tableau."""
    st.subheader("Toutes les stations disponibles")
    if not stations:
        st.info("Aucune station disponible dans la base.")
        return

    st.caption(f"{len(stations)} station(s) disponible(s)")

    df = pd.DataFrame(stations)
    colonnes_souhaitees = [
        "station_id",
        "name",
        "reseau_id",
        "adresse",
        "latitude",
        "longitude",
        "capacite",
    ]
    colonnes_presentes = [c for c in colonnes_souhaitees if c in df.columns]

    st.dataframe(
        df[colonnes_presentes],
        hide_index=True,
        use_container_width=True,
    )


def render_station_by_name(stations: list[dict]):
    """Affiche le détail d'une station sélectionnée dans un menu déroulant."""
    st.subheader("Consulter une station par son nom")

    if not stations:
        st.info("Aucune station disponible à sélectionner.")
        return

    stations_triees = sorted(
        stations,
        key=lambda s: str(s.get("name") or "").lower(),
    )

    selected_station = st.selectbox(
        "Choisir une station",
        options=stations_triees,
        format_func=_format_station_option,
        key="admin_select_station_by_name",
    )

    if not selected_station:
        return

    station_id = selected_station.get("station_id")
    detail = get_station_detail(station_id) if station_id is not None else None
    station = detail or selected_station

    st.markdown(f"### {_format_station_option(station)}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Identifiant (station_id)", station.get("station_id", "—"))
    col2.metric("Réseau (reseau_id)", station.get("reseau_id", "—"))
    col3.metric("Capacité", station.get("capacite", "—"))

    st.write("**Adresse :**", station.get("adresse") or "Non renseignée")
    st.write(
        "**Coordonnées GPS :**",
        f"Latitude {station.get('latitude', '—')} / Longitude {station.get('longitude', '—')}",
    )


def render_create_station():
    """Affiche le formulaire de création d'une station."""
    st.subheader("Créer une station")

    with st.form("create_station_form"):
        station_id = st.text_input("Identifiant de la station", placeholder="ex: 999")
        name = st.text_input("Nom de la station", placeholder="ex: Gare Centrale")
        reseau_id = st.number_input("Identifiant du réseau", min_value=1, step=1, value=1)
        adresse = st.text_input("Adresse", placeholder="ex: 10 Avenue de la Gare")

        col1, col2 = st.columns(2)
        latitude = col1.number_input("Latitude", value=48.117300, format="%.6f")
        longitude = col2.number_input("Longitude", value=-1.677800, format="%.6f")

        capacite = st.number_input("Capacité", min_value=1, step=1, value=20)

        submitted = st.form_submit_button("Créer la station", type="primary")

    if submitted:
        if not station_id.strip() or not name.strip():
            st.error("L'identifiant et le nom de la station sont obligatoires.")
            return

        payload = {
            "station_id": station_id.strip(),
            "reseau_id": int(reseau_id),
            "name": name.strip(),
            "adresse": adresse.strip() or None,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "capacite": int(capacite),
        }

        response = create_station(payload)
        if response and response.get("status_code") in (200, 201):
            st.success(f"Station '{payload['name']}' créée avec succès.")
            st.rerun()
        else:
            st.error(_extract_error_message(response, "Impossible de créer la station."))


def render_delete_station(stations: list[dict]):
    """Affiche l'interface de suppression d'une station avec confirmation."""
    st.subheader("Supprimer une station")

    if not stations:
        st.info("Aucune station disponible à supprimer.")
        return

    stations_triees = sorted(
        stations,
        key=lambda s: str(s.get("name") or "").lower(),
    )

    selected_station = st.selectbox(
        "Choisir une station à supprimer",
        options=stations_triees,
        format_func=_format_station_option,
        key="admin_delete_station_select",
    )

    if not selected_station:
        return

    station_id = selected_station.get("station_id")
    station_label = _format_station_option(selected_station)

    st.warning(
        f"La suppression de **{station_label}** est définitive. "
        "Vérifie qu'aucune donnée liée ne bloque la suppression."
    )
    confirmed = st.checkbox(
        "Je confirme vouloir supprimer cette station",
        key=f"confirm_delete_station_{station_id}",
    )

    if st.button(
        "Supprimer la station",
        type="primary",
        disabled=not confirmed,
        key="btn_delete_station",
    ):
        response = delete_station(station_id)
        if response and response.get("status_code") in (200, 204):
            st.success(f"Station '{station_label}' supprimée avec succès.")
            st.rerun()
        else:
            st.error(_extract_error_message(response, "Impossible de supprimer la station."))


def display_station_admin():
    """Affiche la page d'administration des stations."""
    st.title("Administration des stations")

    if st.button("Actualiser la liste", key="refresh_stations_admin"):
        st.rerun()

    stations = get_all_stations()

    if stations is None:
        st.error("Impossible de récupérer la liste des stations depuis l'API.")
        return

    render_station_by_name(stations)
    st.divider()
    render_create_station()
    st.divider()
    render_delete_station(stations)
    st.divider()
    render_stations_list(stations)


display_station_admin()