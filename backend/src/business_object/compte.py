
class Compte:
    """
    Représente un compte utilisateur dans l'application

    Attributs :
        user_id (int) : Identifiant unique du compte.
        username (str) : Nom d'utilisateur unique.
        is_admin (bool) : Indique si le compte possède les privilèges administrateur.
        email (str) : Adresse électronique associée au compte.
        access_token (str, optional) : Jeton d'accès pour l'authentification.
    """

    def __init__(
        self,
        username: str,
        is_admin: bool,
        password: str,
        email: str,
        user_id: int | None = None,
        access_token: str | None = None,
    ):
        if not isinstance(username, str):
            raise TypeError("L'attribut username doit être de type str.")
        if not isinstance(is_admin, bool):
            raise TypeError("L'attribut is_admin doit être de type bool.")
        if not isinstance(password, str):
            raise TypeError("L'attribut password doit être de type str.")
        if not isinstance(email, str):
            raise TypeError("L'attribut email doit être de type str.")
        if access_token is not None and not isinstance(access_token, str):
            raise TypeError("L'attribut access_token doit être de type str.")

        self.user_id = user_id
        self.username = username
        self.is_admin = is_admin
        self.__password = password
        self.email = email
        self.access_token = access_token

    @property
    def password_hash(self) -> str:
        """Retourne le mot de passe hashé de l'utilisateur."""
        return self.__password

    @password_hash.setter
    def password_hash(self, password: str) -> None:
        """Met à jour le mot de passe hashé de l'utilisateur."""
        self.__password = password

    def __str__(self) -> str:
        return (f"Compte(user_id={self.user_id}, "
                f"username={self.username}, "
                f"is_admin={self.is_admin}, "
                f"email={self.email}, "
                f"access_token={self.access_token})")