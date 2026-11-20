# src/controller/compte_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from schema.compte_model import CompteReadModel, CompteCreateModel, ComptePublicModel, CompteUpdateModel
from service.compte_service import CompteService
from utils.log_utils import get_logger
from utils.security import get_current_user, hash_password
from pydantic import EmailStr, TypeAdapter, ValidationError

_email_adapter = TypeAdapter(EmailStr)

router = APIRouter(tags=["Compte"])

logger = get_logger(__name__)

def get_compte_service() -> CompteService:
    """Fournit une instance de CompteService pour l'injection de dépendances."""
    return CompteService()

@router.get("/list_accounts/", response_model=list[ComptePublicModel])
def list_accounts(service: CompteService = Depends(get_compte_service)):
    """Récupère la liste de tous les comptes (sans afficher les mots de passe)."""
    logger.info("Requête GET /compte/ reçue")
    return service.list_account()

@router.post("/create_account/", response_model=CompteReadModel, status_code=status.HTTP_201_CREATED)
def create_account(
    compte_data: CompteCreateModel,
    service: CompteService = Depends(get_compte_service)
    ):
    """Crée un nouveau compte utilisateur."""
    logger.info(f"Requête POST /compte/ pour : {compte_data.username}")

    # Vérifie si le username est déjà pris
    if service.username_already_used(compte_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà utilisé."
        )

    if len(compte_data.username) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nom d'utilisateur trop court"
        )
    if len(compte_data.password) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe trop court"
        )

    # Appel au service de création
    compte = service.create_account(
        username=compte_data.username,
        password=compte_data.password,
        is_admin=False,
        email=compte_data.email
    )

    if not compte:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Échec de la création du compte."
        )

    return compte

@router.get("/id/{user_id}", response_model=ComptePublicModel)
def get_account_by_id(
    user_id: int,
    service: CompteService = Depends(get_compte_service)
    ):
    """Récupère un compte spécifique grâce à son identifiant (user_id)."""
    logger.info(f"Requête GET /compte/{user_id} reçue")

    compte = service.find_by_id(user_id)

    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte non trouvé."
        )

    return compte

@router.get("/username/{username}", response_model=ComptePublicModel)
def get_account_by_username(
    username: str,
    service: CompteService = Depends(get_compte_service)
    ):
    """Récupère un compte spécifique grâce à son nom (username)."""
    logger.info(f"Requête GET /compte/{username} reçue")

    compte = service.find_by_username(username)

    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte non trouvé."
        )

    return compte


@router.put("/update_username/{username}", response_model=CompteReadModel)
def update_account(
    username: str,  # Le nom du compte à modifier passé directement dans l'URL
    compte_data: CompteUpdateModel,  # Utilise ton nouveau schéma optionnel
    service: CompteService = Depends(get_compte_service),
    current_user=Depends(get_current_user)  # Exige un token valide X-Auth-Token
    ):
    """Met à jour un compte existant de manière partielle.
    Si un champ est None, l'ancienne valeur est conservée.
    """
    logger.info(f"Requête PUT /compte/{username} reçue")

    if current_user.username != username and not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action interdite : vous ne pouvez modifier que vos propres informations."
        )

    # 1. Récupérer le compte actuel en base grâce au service
    compte_actuel = service.find_by_username(username)
    if not compte_actuel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compte '{username}' non trouvé."
        )

    # 2. Mettre à jour les champs SEULEMENT s'ils ne sont pas None (on garde l'ancien sinon)
    if compte_data.username is not None:

            if len(compte_data.username) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nouveau nom d'utilisateur trop court"
                )
            compte_actuel.username = compte_data.username

    # on teste la conformité du nouvel email
    if compte_data.email is not None:
        try:
            compte_actuel.email = _email_adapter.validate_python(compte_data.email)
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format d'adresse email invalide."
            )

    if compte_data.password is not None:

        if len(compte_data.password) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nouveau mot de passe trop court"
            )
        compte_actuel.password_hash = hash_password(compte_data.password, compte_actuel.username)

    # Seul un admin peut modifier le statut is_admin (si la valeur est fournie)
    if current_user.is_admin and compte_data.is_admin is not None:
        compte_actuel.is_admin = compte_data.is_admin

    # 3. Sauvegarder via le service
    updated_compte = service.update(compte_actuel)
    if not updated_compte:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du compte."
        )

    return updated_compte

@router.delete("/delete_username/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    username: str,  # Le nom du compte à supprimer passé dans l'URL
    service: CompteService = Depends(get_compte_service),
    current_user=Depends(get_current_user)  # Exige un token valide
    ):
    """Supprime un compte ciblé par son username (propriétaire du compte ou admin uniquement)."""
    logger.info(f"Requête DELETE /compte/{username} reçue par l'utilisateur : {current_user.username}")

    # 1. Vérification des droits d'accès (même règle que pour le PUT)
    if current_user.username != username and not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action interdite : vous ne pouvez supprimer que votre propre compte."
        )

    # 2. Vérifier si le compte à supprimer existe bien en base
    compte = service.find_by_username(username)
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compte '{username}' non trouvé."
        )

    # 3. Supprimer via le service
    success = service.delete(compte.user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression du compte."
        )

    # Status 204 No Content renvoie une réponse vide par convention
    return None
