
from pydantic import BaseModel, EmailStr, field_validator


class CompteCreateModel(BaseModel):
    """Contrat de données pour la création d'un compte utilisateur.
    Définit la structure JSON et assure la validation des données entrantes.
    """

    user_id: int | None = None
    username: str
    password: str
    email: EmailStr
    is_admin: bool = False

    @field_validator("password")
    @classmethod
    def check_password_length(cls, v: str) -> str:
        # On fixe une longueur minimale raisonnable (ex: 4 caractères pour correspondre à tes tests, 
        # contrairement au prof qui mettait 35 pour un hachage spécifique)
        min_len = 4
        if len(v) < min_len:
            raise ValueError(f"Le mot de passe doit contenir au moins {min_len} caractères")
        return v

class CompteReadModel(BaseModel):
    """Contrat de données pour la lecture / affichage d'un compte avec le token pour la connexion.
    Sécurité : NE CONTIENT PAS LE MOT DE PASSE.
    """

    user_id: int
    username: str
    email: EmailStr
    is_admin: bool
    access_token: str | None = None


class CompteLoginModel(BaseModel):
    """Contrat de données strict pour l'authentification (login)."""

    username: str
    password: str


class ComptePublicModel(BaseModel):
    """Contrat de données pour la lecture et l'affichage d'un compte,
    ce modèle ne contient pas d'information sensible comme le token ou le mot de passe"""
    user_id: int
    username: str
    email: str
    is_admin: bool = False
