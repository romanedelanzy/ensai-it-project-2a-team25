"""
Page Streamlit de consultation et modification des informations personnelles.
Permet à l'utilisateur connecté de consulter son compte et de modifier
son nom d'utilisateur, son email ou son mot de passe.
"""

import pandas as pd
import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.title("Mes informations personnelles")
logger = get_page_logger("personal_information")

check_authentification()

current_user = st.session_state.get("user") or {}
current_username = current_user.get("username")

if not current_username:
    st.error("Impossible d'identifier l'utilisateur connecté.")
    st.stop()

# Récupération des informations à jour du compte connecté
response = api_client.get(f"/compte/username/{current_username}")

if response and response.get("status_code") == 200 and isinstance(response.get("data"), dict):
    account_data = response["data"]
else:
    account_data = current_user

# --- Consultation du compte ---
st.subheader("Informations de mon compte")

safe_account = {
    k: v
    for k, v in account_data.items()
    if k not in ("password", "password_hash", "access_token")
}
st.dataframe(pd.DataFrame([safe_account]), hide_index=True, use_container_width=True)

# --- Modification des informations personnelles ---
st.subheader("Modifier mes informations")

new_username_input = st.text_input(
    "Nouveau nom d'utilisateur (laisser vide pour garder l'actuel)",
    value="",
    max_chars=30,
    key="personal_new_username",
)
new_email_input = st.text_input(
    "Nouvel email (laisser vide pour garder l'actuel)",
    value="",
    key="personal_new_email",
)
new_password_input = st.text_input(
    "Nouveau mot de passe (laisser vide pour garder l'actuel)",
    value="",
    type="password",
    key="personal_new_password",
)

if st.button("Enregistrer mes modifications", type="primary", key="personal_update_btn"):
    payload = {
        "username": new_username_input.strip() if new_username_input.strip() else None,
        "email": new_email_input.strip() if new_email_input.strip() else None,
        "password": new_password_input if new_password_input else None,
        "is_admin": None,
    }

    if all(v is None for v in payload.values()):
        st.info("Aucune modification saisie.")
    else:
        logger.info(f"Mise à jour personnelle demandée par : {current_username}")
        res = api_client.put(f"/compte/update_username/{current_username}", json=payload)

        if res and res.get("status_code") == 200:
            updated_data = res.get("data") if isinstance(res.get("data"), dict) else {}
            merged_user = {**current_user, **updated_data}
            if payload["username"]:
                merged_user["username"] = payload["username"]
            if payload["email"]:
                merged_user["email"] = payload["email"]
            st.session_state["user"] = merged_user

            st.toast("Vos informations ont été mises à jour")
            st.rerun()
        else:
            status_code = res.get("status_code") if isinstance(res, dict) else None
            detail = res.get("data") if isinstance(res, dict) else "Pas de réponse du serveur"
            if status_code == 400 or (isinstance(detail, str) and "déjà" in detail.lower()):
                st.error(f"Impossible de mettre à jour le compte : {detail}")
            else:
                st.error(f"Erreur lors de la mise à jour : {detail}")

if st.button("Retour au menu", type="primary", key="personal_retour_menu_btn"):
    st.switch_page("pages/main_menu.py")