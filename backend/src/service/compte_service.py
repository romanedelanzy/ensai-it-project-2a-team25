import secrets

from business_object.compte import Compte
from dao.CompteDAO import CompteDAO
from utils.log_utils import get_logger, log
from utils.security import hash_password
from utils.singleton import Singleton

logger = get_logger(__name__)


class CompteService(metaclass=Singleton):
    """Classe qui gère la logique métier des comptes utilisateurs."""

    @log
    def create_account(self, username: str, password: str, is_admin: bool, email: str) -> Compte | None:
        """Crée un nouveau compte dans le système.
        Args:
            username (str)
            password (str) en clair, qui sera haché avant stockage
            is_admin (bool)
            email (str)
        Returns:
            Compte | None: L'objet Compte créé ou None si la création a échoué.
        """
        # On instancie l'objet Compte en hachant directement le mot de passe
        # On utilise le nom du compte comme sel pour avoir des hash différent même si le mot de passe est identique
        nouveau_compte = Compte(
            username=username,
            password=hash_password(password, username),
            is_admin=is_admin,
            email=email
        )

        # On appelle le DAO pour persister et on retourne l'objet si c'est un succès
        return nouveau_compte if CompteDAO().create(nouveau_compte) else None

    @log
    def list_account(self) -> list[Compte]:
        """Récupère tous les comptes enregistrés dans la base de données.
        Returns:
            list[Compte]: La liste de tous les comptes
        """
        return CompteDAO().list_all()

    @log
    def find_by_id(self, id_compte: int) -> Compte:
        """Recherche un compte via son id
        Args:
            id_compte (int)
        Returns:
            Objet Compte si correspondance avec id_compte et None sinon.
        """
        return CompteDAO().find_by_id(id_compte)

    @log
    def update(self, compte: Compte) -> Compte | None:
        """Met à jour les informations d'un compte existant.
        Args:
            compte (Compte): Objet Compte contenant les informations mises à jour.
        Returns:
            Compte | None: L'objet Compte mis à jour, ou None si la mise à jour a échoué.
        """
        return compte if CompteDAO().update(compte) else None

    @log
    def delete(self, compte: Compte) -> bool:
        """Supprime un compte utilisateur.
        Args:
            compte (Compte): Objet Compte à supprimer de la base de données.
        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        return CompteDAO().delete(compte)

    @log
    def login(self, username: str, password: str) -> Compte | None:
        """Authentifie un utilisateur en utilisant le nom du compte et son mot de passe sans son hash.
        Args:
            username (str)
            password (str)
        Returns:
            Compte object si l'authentification réussit, sinon None.
        """
        # On délègue la vérification au DAO en hachant le mot de passe avec le username comme sel
        compte = CompteDAO().login(username, hash_password(password, username))
        if compte:
            # Génération d'un token d'accès sécurisé et mise à jour du compte
            compte.access_token = secrets.token_urlsafe(32)
            self.update(compte)
            return compte
        return None

    @log
    def username_already_used(self, username: str) -> bool:
        """Vérifie si un nom d'utilisateur est déjà pris.
        Args:
            username (str)
        Returns:
            bool: True si le nom d'utilisateur existe déjà, False sinon.
        """
        comptes = self.list_account()
        return any(compte.username == username for compte in comptes)