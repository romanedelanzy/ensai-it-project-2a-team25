"""
Page Streamlit de gestion des utilisateurs (Menu 6, réservé aux administrateurs).

Permet de consulter la liste des utilisateurs inscrits, de créer ou supprimer un compte
et de modifier le rôle d'un utilisateur.

Endpoints utilisés :
    GET /comptes
    POST /comptes
    PUT /comptes/{user_id}
    DELETE /comptes/{user_id}
"""

import pandas as pd
import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

ID_KEY = "user_id"  # nom du champ identifiant dans les comptes renvoyés par l'API

st.title("Gestion des utilisateurs")
logger = get_page_logger("admin_users")

check_authentification()

current_user = st.session_state.get("user")

if not current_user.get("is_admin"):
    st.error("Cette page est réservée aux administrateurs.")
    st.stop()

response = api_client.get("/comptes/")

if not response or response["status_code"] != 200:
    st.error("Erreur lors du chargement des utilisateurs")
    st.stop()

users = response["data"]
users_by_id = {u[ID_KEY]: u for u in users}

# --- Liste ---
st.subheader("Utilisateurs inscrits")
st.dataframe(pd.DataFrame(users).drop(columns=["password"], errors="ignore"), hide_index=True)

# --- Création ---
st.subheader("Créer un compte")
with st.form("create_user"):
    new_username = st.text_input("Nom d'utilisateur", max_chars=30)
    new_email = st.text_input("Email")
    new_password = st.text_input("Mot de passe", type="password")
    new_is_admin = st.checkbox("Administrateur")
    submitted = st.form_submit_button("Créer")

if submitted:
    logger.info("Create a user")
    res = api_client.post(
        "/comptes/",
        json={
            "username": new_username,
            "email": new_email,
            "password": new_password,
            "is_admin": new_is_admin,
        },
    )
    if res and res["status_code"] == 200:
        st.toast(f"Compte {new_username} créé ✅")
        st.rerun()
    else:
        st.error(f"Erreur : {res['data'] if res else 'pas de réponse du serveur'}")

# --- Modification du rôle ---
if users_by_id:
    st.subheader("Modifier le rôle")
    role_user_id = st.selectbox(
        "Utilisateur",
        list(users_by_id),
        format_func=lambda uid: users_by_id[uid]["username"],
        key="role_user",
    )
    make_admin = st.checkbox(
        "Administrateur",
        value=bool(users_by_id[role_user_id].get("is_admin")),
        key=f"role_{role_user_id}",
    )
    if st.button("Enregistrer le rôle"):
        logger.info("Update the role of a user")
        res = api_client.put(f"/comptes/{role_user_id}", json={"is_admin": make_admin})
        if res and res["status_code"] == 200:
            st.toast("Rôle mis à jour ✅")
            st.rerun()
        else:
            st.error(f"Erreur : {res['data'] if res else 'pas de réponse du serveur'}")

# --- Suppression ---
others = [uid for uid in users_by_id if uid != current_user.get(ID_KEY)]
if others:
    st.subheader("Supprimer un compte")
    delete_user_id = st.selectbox(
        "Utilisateur à supprimer",
        others,
        format_func=lambda uid: users_by_id[uid]["username"],
        key="delete_user",
    )
    confirmed = st.checkbox("Je confirme la suppression de ce compte")
    if st.button("Supprimer", type="primary", disabled=not confirmed):
        logger.info("Delete a user")
        res = api_client.delete(f"/comptes/{delete_user_id}")
        if res and res["status_code"] in (200, 204):
            st.toast("Compte supprimé ✅")
            st.rerun()
        else:
            st.error(f"Erreur : {res['data'] if res else 'pas de réponse du serveur'}")

if st.button("Retour au menu", type="primary"):
    st.switch_page("pages/main_menu.py")