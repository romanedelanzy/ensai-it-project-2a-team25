import time

from business_object.compte import Compte
from dao.CompteDAO import CompteDAO
from utils.env_variables import load_environment_variables

# test des méthodes de CompteDAO
load_environment_variables()


print("--- 1. Test de list_all() initialisation---")

comptes = CompteDAO().list_all()
for c in comptes:
    print(f"ID: {c.user_id} | Username: {c.username} | Admin: {c.is_admin}")
username_find = "username1"

print(f"\n--- 2. Test de trouver_par_username({username_find}) ---")

compte1 = CompteDAO().trouver_par_username(username_find)

if compte1:
    print(f"Trouvé ! Email : {compte1.email}")
else:
    print(f"Compte avec l'username {username_find} non trouvé.")

id_find = 2

print(f"\n--- 3. Test de trouver_par_id({id_find}) ---")


compte2 = CompteDAO().trouver_par_id(id_find)

if compte2:
    print(f"Trouvé ! Email : {compte2.email}")
else:
    print(f"Compte avec l'id {id_find} non trouvé.")


print("\n--- 4. Test de create() ---")

# Génération d'un username unique basé sur le temps actuel pour éviter les erreurs d'unicité du
# paramètre username
unique_username = f"test_creation_{int(time.time())}"

nouveau_compte = Compte(
    username=unique_username,
    is_admin=False,
    password="password_test",
    email=f"{unique_username}@email.fr"
)

id_genere = CompteDAO().creer(nouveau_compte)
print(f"Compte inséré avec succès ! Nouvel ID généré : {id_genere}")

compte_cree = CompteDAO().trouver_par_id(id_genere)
if compte_cree:
    print(f"Vérification réussie : {compte_cree.username} est bien présent en base !")
else:
    print("Erreur : Le compte n'a pas pu être retrouvé après création.")


print("\n--- 5. Test de delete() ---")

id_a_supprimer = 1
succes = CompteDAO().delete(id_a_supprimer)

if succes:
    print(f"Succès : Le compte avec l'ID {id_a_supprimer} a bien été supprimé !")
else:
    print(f"Échec : Aucun compte trouvé avec l'ID {id_a_supprimer}.")

print("\n--- 6. Test de update() ---")

# 1. Récupération d'un compte existant (ex: ID=2)
compte_a_modifier = CompteDAO().trouver_par_id(2)

if compte_a_modifier:
    print(
        f"Avant modification -> Username : {compte_a_modifier.username}"
        f" | Admin : {compte_a_modifier.is_admin} | Email : {compte_a_modifier.email}"
        )

    # 2. Modification des attributs
    compte_a_modifier.username = "username2_modifie"
    compte_a_modifier.is_admin = False
    compte_a_modifier.email = "update.reussi@email.fr"

    # 3. Appel de la méthode update()
    succes_update = CompteDAO().update(compte_a_modifier)

    if succes_update:
        print("Mise à jour envoyée avec succès !")

        # 4. Vérification immédiate en le rechargeant depuis la base
        compte_verif = CompteDAO().trouver_par_id(2)
        print(
            f"Après modification -> Username : {compte_verif.username}"
            f" | Admin : {compte_verif.is_admin} | Email : {compte_verif.email}"
            )
    else:
        print("Échec de la mise à jour.")
else:
    print("Impossible de tester l'update : compte introuvable.")


print("--- . Test de list_all() après les tests ---")

comptes = CompteDAO().list_all()
for c in comptes:
    print(f"ID: {c.user_id} | Username: {c.username} | Admin: {c.is_admin}")
