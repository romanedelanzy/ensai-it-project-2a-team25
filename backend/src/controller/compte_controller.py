# src/controller/compte_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from schema.compte_model import CompteReadModel, CompteCreateModel
from service.compte_service import CompteService
from utils.log_utils import get_logger
from utils.security import get_current_user

# On définit un préfixe "/compte" et un tag pour regrouper joliment sur Swagger
router = APIRouter(tags=["Compte"])

logger = get_logger(__name__)

print("MODELE COMPTE :", CompteCreateModel.__module__)

for name, field in CompteCreateModel.model_fields.items():
    print(name, "required =", field.is_required(), "default =", field.default)

def get_compte_service() -> CompteService:
    """Fournit une instance de CompteService pour l'injection de dépendances."""
    return CompteService()

@router.get("/", response_model=list[CompteReadModel])
def list_accounts(service: CompteService = Depends(get_compte_service)):
    """Récupère la liste de tous les comptes (sans afficher les mots de passe)."""
    logger.info("Requête GET /compte/ reçue")
    return service.list_account()

@router.post("/", response_model=CompteReadModel, status_code=status.HTTP_201_CREATED)
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

@router.get("/{user_id}", response_model=CompteReadModel)
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

@router.put("/{username}", response_model=CompteReadModel)
def update_account(
    username: str,  # Le nom du compte à modifier passé directement dans l'URL
    compte_data: CompteCreateModel,
    service: CompteService = Depends(get_compte_service),
    current_user = Depends(get_current_user)  # Exige un token valide X-Auth-Token
    ):
    """Met à jour un compte existant ciblé par son username."""
    logger.info(f"Requête PUT /compte/{username} reçue")

    # 1. Vérifier si le compte existe grâce à ton service find_by_username
    compte = service.find_by_username(username)
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compte '{username}' non trouvé."
        )

    # 2. Mettre à jour les champs
    compte.username = compte_data.username
    compte.email = compte_data.email
    # Si tu veux aussi mettre à jour le mot de passe en le hachant proprement :
    # compte.password = hash_password(compte_data.password, compte_data.username)

    # 3. Sauvegarder via le service
    updated_compte = service.update(compte)
    if not updated_compte:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du compte."
        )

    return updated_compte
