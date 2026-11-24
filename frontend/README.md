#  Frontend – VeloScope

Le frontend constitue l’interface graphique de l’application VeloScope. Il s’agit d’un tableau de bord web interactif développé avec **Streamlit**, qui permet aux utilisateurs de consulter les stations de vélos en libre-service, de suivre leur disponibilité et d’accéder aux différentes fonctionnalités de l’application.

Il communique avec le backend via son API REST développée avec **FastAPI**.

## Lancer l’application

- [ ] Installer les dépendances :

  ```bash
  uv sync --project frontend --all-extras
  ```

- [ ] Se placer dans le dossier `frontend` :

  ```bash
  cd frontend
  ```

- [ ] Lancer l’application Streamlit :

  ```bash
  uv run --project . streamlit run src/app.py
  ```

L’interface est alors accessible depuis l’adresse indiquée dans le terminal.

## Architecture

Le frontend adopte une organisation modulaire afin de séparer les différentes interfaces utilisateur de la logique de communication avec le backend.

- **Pages** (`pages/`) : regroupent les différentes vues de l’application, notamment la consultation des stations, les favoris et les fonctionnalités de recommandation.
- **Client API** (`utils/`) : centralise les appels HTTP vers le backend FastAPI, afin de récupérer les données et d'effectuer les opérations demandées par l'utilisateur.
- **Gestion de l'authentification** : assure la gestion de la session utilisateur et du jeton d'authentification nécessaire à l'accès aux fonctionnalités protégées.
- **Utilitaires** (`utils/`) : regroupent les fonctions communes utilisées par les différentes pages, notamment pour l'initialisation de l'application, la journalisation et la gestion de l'interface.

## ⚒️ Débogage et qualité du code

### Logs

Le frontend dispose d'un système de journalisation permettant de suivre son fonctionnement et de faciliter l'identification des erreurs.

Les logs permettent notamment de repérer les problèmes rencontrés lors des interactions avec l'API backend.

### Qualité du code

Le projet utilise **Ruff** pour le formatage et la vérification du code Python.

Le formatage automatique à l'enregistrement (*format on save*) peut être configuré dans les paramètres de l'espace de travail (`.vscode/settings.json`).