class Compte:
    """
    Représente un compte utilisateur dans l'application

    Attributs :
        user_id (int) : Identifiant unique du compte.
        username (str) : Nom d'utilisateur unique.
        is_admin (bool) : Indique si le compte possède les privilèges administrateur.
        email (str) : Adresse électronique associée au compte.

    """

    def __init__(
        self,
        username: str,
        is_admin: bool,
        password: str,
        email: str,
        user_id: int | None = None
    ):
        if not isinstance(username, str):
            raise TypeError("L'attribut username doit être de type str.")
        if not isinstance(is_admin, bool):
            raise TypeError("L'attribut is_admin doit être de type bool.")
        if not isinstance(password, str):
            raise TypeError("L'attribut password doit être de type str.")
        if not isinstance(email, str):
            raise TypeError("L'attribut email doit être de type str.")

        self.user_id = user_id
        self.username = username
        self.is_admin = is_admin
        self.__password = password
        self.email = email

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
                f"email={self.email})")
