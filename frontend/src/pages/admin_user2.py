"""
Page Streamlit de gestion des utilisateurs.
Étape 1 : consultation paginée des comptes (10 par 10).
"""

import math
import pandas as pd
import streamlit as st

from utils.api_client import api_client
from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

PAGE_SIZE = 10

st.title("Gestion des utilisateurs")
logger = get_page_logger("admin_user2")

check_authentification()

current_user = st.session_state.get("user") or {}

if not current_user.get("is_admin"):
    st.error("Cette page est réservée aux administrateurs.")
    st.stop()

response = api_client.get("/compte/list_accounts/")

if not response or response.get("status_code") != 200:
    st.error("Erreur lors du chargement des utilisateurs.")
    st.stop()

users = response.get("data") or []
users_by_username = {u["username"]: u for u in users if u.get("username")}

st.subheader("Utilisateurs inscrits")

if not users:
    st.info("Aucun utilisateur trouvé.")
else:
    total_users = len(users)
    total_pages = math.ceil(total_users / PAGE_SIZE)

    # Initialisation et bornage du numéro de page dans session_state
    if "admin_user2_page" not in st.session_state:
        st.session_state.admin_user2_page = 1
    if st.session_state.admin_user2_page > total_pages:
        st.session_state.admin_user2_page = total_pages
    if st.session_state.admin_user2_page < 1:
        st.session_state.admin_user2_page = 1

    current_page = st.session_state.admin_user2_page
    start_idx = (current_page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_users = users[start_idx:end_idx]

    col_prev, col_info, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("⬅️ Précédent", disabled=(current_page <= 1), key="prev_page"):
            st.session_state.admin_user2_page -= 1
            st.rerun()

    with col_info:
        st.markdown(
            f"<div style='text-align: center; padding-top: 6px;'>"
            f"Page <b>{current_page}</b> / <b>{total_pages}</b> "
            f"({start_idx + 1}–{min(end_idx, total_users)} sur {total_users} comptes)"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_next:
        if st.button("Suivant ➡️", disabled=(current_page >= total_pages), key="next_page"):
            st.session_state.admin_user2_page += 1
            st.rerun()

    df_page = pd.DataFrame(page_users).drop(
        columns=["password", "password_hash", "access_token"], errors="ignore"
    )
    st.dataframe(df_page, hide_index=True, use_container_width=True)

# --- Modification d'un compte ---
if users_by_username:
    st.subheader("Modifier un compte")

    target_username = st.selectbox(
        "Compte à modifier",
        options=list(users_by_username.keys()),
        key="update_username_select",
    )
    target_user = users_by_username[target_username]

    new_username_input = st.text_input(
        "Nouveau nom d'utilisateur (laisser vide pour garder l'actuel)",
        value="",
        max_chars=30,
        key=f"update_new_username_{target_username}",
    )
    new_email_input = st.text_input(
        "Nouvel email (laisser vide pour garder l'actuel)",
        value="",
        key=f"update_new_email_{target_username}",
    )
    new_password_input = st.text_input(
        "Nouveau mot de passe (laisser vide pour garder l'actuel)",
        value="",
        type="password",
        key=f"update_new_password_{target_username}",
    )
    new_is_admin = st.checkbox(
        "Administrateur",
        value=bool(target_user.get("is_admin", False)),
        key=f"update_is_admin_{target_username}",
    )

    if st.button("Enregistrer les modifications", type="primary", key="update_account_btn"):
        payload = {
            "username": new_username_input.strip() if new_username_input.strip() else None,
            "email": new_email_input.strip() if new_email_input.strip() else None,
            "password": new_password_input if new_password_input else None,
            "is_admin": new_is_admin,
        }

        logger.info(f"Mise à jour demandée pour le compte : {target_username}")
        res = api_client.put(f"/compte/update_username/{target_username}", json=payload)

        if res and res.get("status_code") == 200:
            updated_name = payload["username"] or target_username
            # Si l'admin modifie son propre compte, on met à jour session_state["user"]
            if target_username == current_user.get("username"):
                st.session_state["user"] = res.get("data", current_user)
            st.toast(f"Compte '{updated_name}' mis à jour ✅")
            st.rerun()
        else:
            detail = res.get("data") if isinstance(res, dict) else "Pas de réponse du serveur"
            st.error(f"Erreur lors de la modification : {detail}")

# --- Suppression d'un compte par nom d'utilisateur ---
deletable_usernames = [
    u["username"]
    for u in users
    if u.get("username") and u.get("username") != current_user.get("username")
]

if deletable_usernames:
    st.subheader("Supprimer un compte")
    selected_username = st.selectbox(
        "Sélectionner le nom d'utilisateur à supprimer",
        options=deletable_usernames,
        key="delete_username_select",
    )
    confirmed = st.checkbox(
        f"Je confirme la suppression du compte '{selected_username}'",
        key="confirm_delete_user",
    )

    if st.button("Supprimer le compte", type="primary", disabled=not confirmed):
        logger.info(f"Suppression demandée pour l'utilisateur : {selected_username}")
        res = api_client.delete(f"/compte/delete_username/{selected_username}")

        if res and res.get("status_code") in (200, 204):
            st.toast(f"Compte '{selected_username}' supprimé ✅")
            st.rerun()
        else:
            detail = res.get("data") if isinstance(res, dict) else "Pas de réponse du serveur"
            st.error(f"Erreur lors de la suppression : {detail}")

if st.button("Retour au menu", type="primary"):
    st.switch_page("pages/main_menu.py")
