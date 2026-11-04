# src/controller/login_compte_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from schema.compte_model import CompteLoginModel, CompteReadModel
from service.compte_service import CompteService
from utils.log_utils import get_logger

# On définit un préfixe "/login" et un tag distinct pour Swagger
router = APIRouter(tags=["Login Compte"])

logger = get_logger(__name__)


def get_compte_service() -> CompteService:
    """Fournit une instance de CompteService pour l'injection de dépendances."""
    return CompteService()


@router.post("/", response_model=CompteReadModel)
def login(
    credentials: CompteLoginModel,
    service: CompteService = Depends(get_compte_service)
    ):
    """Authentifie un utilisateur (compte).
    Args:
        credentials (CompteLoginModel): Contient le username et le password.
        service (CompteService): Le service gérant la logique métier.
    Returns:
        CompteReadModel: Les informations du compte authentifié (incluant is_admin, token, etc.).
    Raises:
        HTTPException: 401 si les identifiants sont invalides ou si l'utilisateur n'existe pas.
    """
    logger.info(f"Tentative de connexion pour l'utilisateur : {credentials.username}")

    # On appelle la méthode de login de ton service
    compte = service.login(credentials.username, credentials.password)

    if compte:
        # On retourne le compte (qui sera filtré par CompteReadModel pour ne jamais renvoyer le mot de passe)
        # Il contient is_admin, ce qui permettra au frontend d'adapter l'interface.
        return compte

    # Si le service renvoie None ou False, les identifiants sont incorrects
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou utilisateur introuvable."
    )