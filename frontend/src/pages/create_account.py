"""
Page Streamlit de création de compte (Menu 1 : connexion et inscription).

Permet à un nouvel utilisateur de créer son compte (nom d'utilisateur, email, mot de passe).

Endpoint utilisé :
    POST /comptes
"""

import streamlit as st

from utils.api_client import api_client
from utils.log_init import get_page_logger

st.title("Créer un compte")
logger = get_page_logger("create_account")

username = st.text_input("Nom d'utilisateur", max_chars=30)
email = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")
confirmation = st.text_input("Confirmer le mot de passe", type="password")

passwords_match = bool(password) and password == confirmation
st.write("✅" if passwords_match else "❌", "Les deux mots de passe sont identiques")

with st.container(horizontal_alignment="center"):
    if st.button("Créer le compte", width=200, disabled=not username or not passwords_match):
        logger.info("Create an account")
        account = {"username": username, "password": password, "email": email}

        response = api_client.post("/compte/create_account/", json=account)

        if response:
            if response["status_code"] == 201:
                st.success(f"Compte {username} créé avec succès ! 🎉 Vous pouvez vous connecter.")
                logger.info("Account created successfully")
            else:
                st.error(f"Erreur : {response['data']}")
                logger.info("Error while creating account")

if st.button("Retour à l'accueil", type="primary"):
    st.switch_page("pages/home.py")