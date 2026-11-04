"""
Page d'accueil Streamlit (Menu 1 : connexion et inscription).

Permet de se connecter avec un compte existant ou d'aller créer un nouveau compte.

Endpoint utilisé :
    POST /login
"""

import streamlit as st
from streamlit import config

from utils.api_client import api_client
from utils.log_init import get_page_logger

if "user" in st.session_state:
    st.switch_page("pages/main_menu.py")

st.set_page_config(page_title="VeloScope", page_icon="🚲", layout="centered")

st.markdown(
    f"""
    <div style="text-align:center">
        <h1 style="color:{config.get_option("theme.primaryColor")}">🚲 VeloScope</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
logger = get_page_logger("home")

username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")

with st.container(horizontal_alignment="center"):
    if st.button("Se connecter"):
        logger.info(f"Attempting login for user: {username}")

        try:
            response = api_client.post("/login-compte/", json={"username": username, "password": password})
            if response:
                status_code = response.get("status_code")
                data = response.get("data")

                if status_code == 200:
                    logger.info(f"User {username} successfully logged in.")
                    user = data
                    st.session_state["user"] = user
                    st.session_state["access_token"] = user["access_token"]
                    st.success(f"Bienvenue {user['username']} ! 🎉")
                    st.switch_page("pages/main_menu.py")
                elif status_code == 401:
                    logger.warning(f"Login failed: 401 Unauthorized for user {username}.")
                    st.error("Identifiants invalides")
                else:
                    logger.error(f"Login failed: Status {status_code}, Data: {data}")
                    st.error("Erreur du serveur, voir les logs.")
            else:
                logger.error("API returned None or empty response")
                st.error("Pas de réponse du serveur.")

        except Exception as e:
            logger.exception(f"Critical error during API call: {str(e)}")
            st.error(f"Erreur de connexion : {str(e)}")

st.space("small")

if st.button("Créer un compte"):
    st.switch_page("pages/create_account.py")