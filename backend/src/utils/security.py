import hashlib

from fastapi import Header, HTTPException,  Security
from fastapi.security import APIKeyHeader
from dao.player_dao import PlayerDao
from dao.CompteDAO import CompteDAO
from business_object.compte import Compte


def hash_password(password: str, salt: str = "") -> str:
    """Hashes a password using the SHA-256 algorithm.
    Args:
        password (str): The plain text password to be hashed.
        salt (str, optional): A string added to the password before hashing
            to protect against rainbow table attacks.
    Returns:
        str: The resulting hexadecimal hash string.
    """
    password_bytes = password.encode("utf-8") + salt.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def verify_token(x_auth_token=Header(None)) -> PlayerDao:
    """Verifies the authenticity of a player via the provided auth token.

    This function checks if a token is present in the request headers and
    validates it against the database.
    Args:
        x_auth_token (str, optional): The token extracted from the
            'X-Auth-Token' HTTP header. Defaults to None.
    Returns:
        Player object associated with the valid token.
    Raises:
        HTTPException: 401 error if the token is missing.
        HTTPException: 401 error if the token is not found in the database.
    """
    if not x_auth_token:
        raise HTTPException(status_code=401, detail="Missing token.")

    player = PlayerDao().find_by_token(x_auth_token)
    if not player:
        raise HTTPException(status_code=401, detail="Invalid token.")

    return player

# On définit le schéma de sécurité basé sur l'en-tête "X-Auth-Token"
api_key_header = APIKeyHeader(name="X-Auth-Token", auto_error=True)

def get_current_user(x_auth_token: str = Security(api_key_header)) -> Compte:
    """Vérifie l'authenticité d'un utilisateur via le header X-Auth-Token."""

    compte = CompteDAO().find_by_token(x_auth_token)
    if not compte:
        raise HTTPException(
            status_code=401,
            detail="Token d'authentification invalide, expiré ou manquant."
        )

    return compte
