# ensai-it-project-2a-team25

## Objectifs du groupe

Véloscope est un site permettant de visualiser en temps réel les stations services de vélo de la ville de Bordeaux. L'utilisateur peut créer un compte, gérer ses stations favorites, et naviguer sur le site pour connaître différentes statistiques utiles sur les stations de vélo. Il peut également se faire recommander des stations en indiquant une adresse de Bordeaux. 

### Fonctionnalités 

* F1 gestion des utilisateurs (créer un compte, se connecter, consulter les données & stats, gérer ses stations favorites)

* F2 collecter les données : l'API doit être interrogée toutes les **15 mins** pour récupérer : 
station, date & heure, nb vélos simples dispos, nb vélos électriques dispos, nb places dispos, "état de la station"

* F3 : consulter une station en la cherchant pour afficher état / nb vélos dispos / capacité / taux remplissage / évolution disponibilité (dernières 24h, 7 derniers jours, 30 derniers jours)

* F4 : Afficher le score de fiabilité d'une station
une station est considérée comme :
    vide lorsqu’il n’y a plus de vélo disponible ;
    saturée lorsqu’il ne reste plus de place ;
    fonctionnelle dans les autres cas. À partir de l’historique, l’application calcule notamment :
    pourcentage du temps passé vide ;
    pourcentage du temps passé saturé ;
    durée moyenne des épisodes de saturation ;
    durée moyenne des épisodes de pénurie ;
    évolution du score au cours du temps. Le score global est défini par les étudiants à partir d’une formule documentée.

* F5 : Recommandation d'une station à proximité
 La recommandation doit prendre en compte plusieurs critères, par exemple :
    distance ;
    nombre de vélos actuellement disponibles ;
    fiabilité historique de la station ;
    disponibilité de vélos électriques ;
    tendance récente de la station. Deux stations à distance équivalente ne doivent donc pas nécessairement être classées de la même manière. La formule de classement devra être justifiée et testée.

### Ressources

[Site de la base de données](https://transport.data.gouv.fr/datasets/station-le-velo-en-temps-reel-1)

### Lancement du projet depuis un service Onyxia VsCode

- [ ] Lancer un service **VSCode-python** (qui inclut Visual Studio Code, Python 3.13, Git)
  - Dans les paramètres du service au niveau "Network access", ouvrir les ports 5000 et 8000.
- [ ] Cocher dans les paramètres GIT l'option "Cloner le dépôt" et "Ouvrir un dossier du dépôt"
  - Indiquer l'adresse du dépôt


### Installer les packages requis

Pour installer et gérer les dépendances avec [uv](https://docs.astral.sh/uv/), exécuter dans un terminal les lignes de codes ci-dessous :

```bash
# curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --project backend
uv sync --project frontend
```

### Variables d'environnement

- [ ] Ouvrir dans Onyxia un service PostGreSQL pour la base de données
- [ ] Dans l'onglet "File", créer un nouveau fichier nommé  `.env` à la racine du projet
- [ ] Copier dans ce fichier le texte ci-contre. Remplacer les éléments par ceux du service PostGre, visibles dans la page "Mes services" d'Onyxia en cliquant sur le service Postgre.

```default
POSTGRES_HOST=postgresql-cnpg-<suffixe>
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=user-<username>
POSTGRES_PASSWORD=<password>
POSTGRES_SCHEMA=project

UVICORN_HOST=0.0.0.0
UVICORN_PORT=5000

BACKEND_URL=http://localhost:5000
BACKEND_TIMEOUT=5

ELO_K_FACTOR=32
```

### Lancement de l'application

Ouvrir deux terminaux :

- Un terminal pour le backend FastApi: executer la commande `uv run --project backend python backend/src/main.py`
- Un terminal pour le frontend Streamlit: `cd frontend` puis `uv run --project . streamlit run src/app.py`

Lors du lancement, une demande pour activer la collecte automatique de données sera proposée. Cliquer sur "o" pour lancer la collecte depuis l'API externe et sur "n" pour utiliser l'application sans lancer la collecte. 

Lors du premier lancement, aller dans le port 5000 et naviguer jusqu'à la fin de la page pour lancer la fonction **Reset Database**. Cela permettra de mettre à jour la base de données avec les données contenues dans pop_db.sql. 

:warning: **Ne pas cliquer sur le pop-up pour ouvrir le port. Ouvrir le port directement depuis le service Onyxia**


### Accéder à l'application depuis le web

Comme l'application s'exécute dans un conteneur cloud, les services ne sont pas directement accessibles via *localhost* depuis un navigateur local. Utiliser les URL publiques fournies par Onyxia.

Pour obtenir l'URL publique des services (Frontend ou Backend) :

- Rendez-vous sur la page [Mes services Onyxia](https://datalab.sspcloud.fr/my-services?utm_source=chatgpt.com).
- Cliquer sur le bouton **« Open »** : des liens permettant d'accéder à l'API et/ou à l'interface graphique (GUI) vous seront alors proposés.


### Endpoints de l'API

L'API REST de VeloScope permet d'interagir avec les différentes fonctionnalités de l'application : consultation des stations, gestion des favoris, fiabilité, recommandations et gestion des comptes.

**Documentation interactive**

La documentation complète des endpoints est accessible via les interfaces Swagger (`/docs`) et ReDoc (`/redoc`). Elles permettent de consulter les routes disponibles, leurs paramètres, les données attendues et les réponses possibles. Swagger permet également de tester directement les requêtes.

**Utilisation des endpoints**

Pour effectuer des requêtes depuis un terminal, il faut d'abord définir l'URL du backend dans une variable d'environnement `API_URL`. Celle-ci correspond à l'URL publique fournie par Onyxia lorsque l'application est déployée dans le cloud, ou à l'adresse locale du backend en environnement de développement.

Exemple en local :

```bash
export API_URL=http://localhost:5000
```

**Exemples de requêtes**

Les exemples suivants utilisent `curl` pour interroger l'API. Le résultat est formaté avec `jq` pour faciliter sa lecture.

- **Consulter l'ensemble des stations :**

```bash
curl -L -X GET "$API_URL/station/" | jq .
```

- **Consulter une station à partir de son identifiant :**

```bash
curl -L -X GET "$API_URL/station/IDENTIFIANT_STATION" | jq .
```

- **Consulter le dernier relevé d'une station :**

```bash
curl -L -X GET "$API_URL/station/IDENTIFIANT_STATION/status" | jq .
```

- **Consulter l'évolution de la disponibilité d'une station :**

```bash
curl -L -X GET "$API_URL/station/IDENTIFIANT_STATION/availability-history?period=24h" | jq .
```

- **Consulter les stations favorites de l'utilisateur connecté :**

```bash
curl -L -X GET "$API_URL/favoris/" \
  -H "X-Auth-Token: VOTRE_JETON" | jq .
```

- **Ajouter une station aux favoris :**

```bash
curl -L -X POST "$API_URL/favoris/IDENTIFIANT_STATION" \
  -H "X-Auth-Token: VOTRE_JETON" | jq .
```

- **Retirer une station des favoris :**

```bash
curl -L -X DELETE "$API_URL/favoris/IDENTIFIANT_STATION" \
  -H "X-Auth-Token: VOTRE_JETON" | jq .
```

- **Consulter le score de fiabilité d'une station :**

```bash
curl -L -X GET "$API_URL/reliability/IDENTIFIANT_STATION" | jq .
```

**Authentification**

Certaines routes nécessitent d'être authentifié. Il faut alors transmettre le jeton obtenu lors de la connexion dans l'en-tête HTTP `X-Auth-Token`. En l'absence de jeton valide, l'API renvoie une erreur 401 (Unauthorized).


## :arrow_forward: Structure du projet

### Dossiers

| Item                       | Description                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `data`                     | Scripts SQL pour créer les tables de la base de données et insérer les lignes                     |
| `doc`                      | Diagrammes, rapports...                               |
| `backend`                  | code API code organisé en architecture par couches                     |
| `frontend`                 | code GUI code (interface graphique pour l'utilisateur)                                      |


### Fichiers 

| Élément                    | Description                                                                                                                 |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `README.md`                | Présente l'application et fournit des informations utiles pour son installation et son utilisation.                         |
| `LICENSE`                  | Définit les droits d'utilisation et les conditions de licence du dépôt.                                                     |
| `.github/workflows/ci.yml` | Définit un processus automatisé exécutant des tâches prédéfinies (tests, vérification du code ou déploiement, par exemple). |
| `.vscode/settings.json`    | Contient les paramètres de configuration de VS Code propres à ce projet.                                                    |
| `.gitignore`               | Liste les fichiers et dossiers qui ne doivent pas être suivis par Git.                                                      |

### Erreur lors du reset

Il se peut que le reset de la database ne marche pas à cause d'un problème de tâche en attente. Dans ce cas, suivre la procédure ci-contre :

- Aller dans CloudBeaver
- Lancer la requête SQL suivante :
SELECT pid, state, wait_event_type, wait_event,
       LEFT(query, 100) AS query
FROM pg_stat_activity
WHERE datname = current_database();

- Si une tâche en attente est visible, supprimer-là : Par exemple, s'il s'agit de la tâche n°123975, SELECT pg_terminate_backend(123975);

- Relancer le reset si nécessaire