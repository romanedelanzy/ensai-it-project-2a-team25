# src/controller/compte_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from schema.compte_model import CompteReadModel, CompteCreateModel
from service.compte_service import CompteService
from utils.log_utils import get_logger

# On définit un préfixe "/compte" et un tag pour regrouper joliment sur Swagger
router = APIRouter(prefix="/compte", tags=["Compte"])

logger = get_logger(__name__)


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
    logger.info(f"Requête POST /compte/ reçue pour l'utilisateur : {compte_data.username}")

    # 1. On vérifie si le username est déjà pris
    if service.username_already_used(compte_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà utilisé."
        )

    # 2. On appelle le service pour créer le compte
    compte = service.create_account(
        username=compte_data.username,
        password=compte_data.password,
        is_admin=compte_data.is_admin,
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

@router.put("/{user_id}", response_model=CompteReadModel)
def update_account(
    user_id: int,
    compte_data: CompteCreateModel,
    service: CompteService = Depends(get_compte_service)
    ):
    """Met à jour les informations d'un compte existant.
    Args:
        user_id (int): L'identifiant du compte à modifier.
        compte_data (CompteCreateModel): Les nouvelles données du compte.
        service (CompteService): Le service gérant la logique métier.
    Returns:
        CompteReadModel: Le compte mis à jour (sans le mot de passe).
    Raises:
        HTTPException: 404 si le compte n'est pas trouvé.
        HTTPException: 500 si la mise à jour échoue.
    """
    logger.info(f"Requête PUT /compte/{user_id} reçue")

    # 1. Vérifier si le compte existe
    compte = service.find_by_id(user_id)
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Compte (id={user_id}) non trouvé."
        )

    # 2. Mettre à jour les attributs de l'objet Compte
    compte.username = compte_data.username
    compte.email = compte_data.email
    compte.is_admin = compte_data.is_admin
    compte.password_hash = compte_data.password  # Utilisation du setter sécurisé de ton objet

    # 3. Sauvegarder via le service
    updated_compte = service.update(compte)
    if not updated_compte:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Erreur lors de la mise à jour du compte."
        )

    return updated_compte

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    user_id: int,
    service: CompteService = Depends(get_compte_service)
):
    """Supprime un compte par son identifiant."""
    logger.info(f"Requête DELETE /compte/{user_id} reçue")

    compte = service.find_by_id(user_id)
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Compte (id={user_id}) non trouvé."
        )

    # Vérifie si ton service possède une méthode delete (ou supprime selon ta logique DAO)
    success = service.delete(user_id) if hasattr(service, 'delete') else False
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression du compte."
        )
    return None

