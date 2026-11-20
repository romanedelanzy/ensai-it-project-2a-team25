"""
Page Streamlit du menu principal.

Donne accès aux écrans de l'application : carte du réseau, stations favorites,
recherche d'itinéraire et, pour les administrateurs, gestion des utilisateurs.
"""

import streamlit as st

from utils.auth_guard import check_authentification
from utils.log_init import get_page_logger

st.title("Menu principal")
logger = get_page_logger("main_menu")

check_authentification()

user = st.session_state.get("user")

st.badge(f"Bonjour {user['username']} !", color="green")

st.write("Que souhaitez-vous faire ?")

if st.button("Carte du réseau"):
    st.switch_page("pages/network_map.py")

if st.button("⭐ Mes stations favorites ⭐"):
    st.switch_page("pages/favorites.py")

if st.button("Recherche d'itinéraire"):
    st.switch_page("pages/route_search.py")

if st.button("🚲 Stations recommandées"):
    st.switch_page("pages/recommendation.py")

if user.get("is_admin"):
    if st.button("Gestion des utilisateurs"):
        st.switch_page("pages/admin_users.py")

if st.button(label="Se déconnecter", type="primary"):
    logger.info("Log out")
    del st.session_state["user"]
    st.session_state.pop("access_token", None)
    st.switch_page("pages/home.py")
