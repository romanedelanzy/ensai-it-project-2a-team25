import hashlib

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from business_object.compte import Compte
from dao.CompteDAO import CompteDAO


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
