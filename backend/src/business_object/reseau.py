class Reseau:
    def __init__(
        self,
        nom: str,
        ville: str,
        gbfs_url: str,
        reseau_id: int | None = None
    ):
        self.reseau_id = reseau_id
        self.nom = nom
        self.ville = ville
        self.gbfs_url = gbfs_url

    def __repr__(self) -> str:
        return (
            f"Reseau(reseau_id={self.reseau_id}, "
            f"nom='{self.nom}', "
            f"ville='{self.ville}', "
            f"gbfs_url='{self.gbfs_url}')")
