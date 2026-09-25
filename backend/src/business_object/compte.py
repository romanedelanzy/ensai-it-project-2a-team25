class Compte:
    def __init__(
        self,
        user_id: int,
        username: str,
        is_admin: bool,
        password: str,
        email: str
    ):
        self.user_id = user_id
        self.username = username
        self.is_admin = is_admin
        self.__password = password
        self.email = email

    def get_password(self) -> str:
        return self.__password

    def set_password(self, password: str) -> None:
        self.__password = password

    def __str__(self) -> str:
        return (f"Compte(user_id={self.user_id}), "
                f"username={self.username}, "
                f"is_admin={self.is_admin}, "
                f"email={self.email}")
