
from pydantic import BaseModel, EmailStr


class CompteCreateModel(BaseModel):
    """Contrat de données pour la création d'un compte utilisateur.
    """

    user_id: int | None = None
    username: str
    password: str
    email: EmailStr
    is_admin: bool = False


class CompteReadModel(BaseModel):
    """Contrat de données pour la lecture d'un compte avec le token pour la connexion.
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


class CompteUpdateModel(BaseModel):
    """Contrat de données pour la saisie d'informations modifiées du compte"""
    username: str | None | None = None
    password: str | None| None  = None
    email: str | None| None  = None
    is_admin: bool | None| None  = None
