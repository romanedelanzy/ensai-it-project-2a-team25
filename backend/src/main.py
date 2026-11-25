
"""
Main entry point for the FastAPI web service.

Initializes logging, loads environment variables, and sets up API routers.
"""

import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from background_collection import collection_loop

from controller import (
    compte_controller,
    favori_controller,
    fiabilite_controller,
    login_compte_controller,
    recommendation_controller,
    station_controller,
)
from utils.database_utils import synchronize_compte_sequence
from utils.env_variables import display_values, load_environment_variables
from utils.log_utils import LogMiddleware, get_logger, initialize_logs
from utils.reset_database import ResetDatabase

logger = get_logger(__name__)

# Initialization
initialize_logs("Webservice")

load_environment_variables()
display_values()

ENABLE_GBFS_COLLECTION = False


def choose_collection():
    """Demande si la collecte GBFS doit être activée."""

    while True:
        choix = input(
            "Voulez-vous activer la collecte automatique GBFS ? (o/n) : "
        ).strip().lower()

        if choix in ("o", "n"):
            return choix == "o"

        print("Réponse invalide. Veuillez saisir o ou n.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le démarrage et l'arrêt du service."""

    # Synchronisation des identifiants PostgreSQL
    logger.info("Synchronisation de la séquence des comptes.")
    synchronize_compte_sequence()
    logger.info("Séquence des comptes synchronisée.")

    # Démarrage de la collecte GBFS
    if ENABLE_GBFS_COLLECTION:
        logger.info("Démarrage du collecteur GBFS.")
        task = asyncio.create_task(collection_loop())
    else:
        logger.info("Collecte GBFS désactivée au démarrage.")
        task = None

    try:
        yield

    finally:
        if task is not None:
            logger.info("Arrêt du collecteur GBFS.")

            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                logger.info("Collecteur GBFS arrêté.")


app = FastAPI(
    title="My Webservice",
    root_path="/proxy/5000",
    servers=[
        {
            "url": "https://user-elouan-460462-0.user.lab.sspcloud.fr/proxy/5000"
        }
    ],
    lifespan=lifespan,
)

app.add_middleware(LogMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic 422 errors to log them.
    """
    body = await request.body()
    body_str = body.decode() if body else "empty body"

    logger.error(f"Validation Error\nErrors: {exc.errors()}\nBody: {body_str}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body_str},
    )


app.include_router(station_controller.router, prefix="/station", tags=["Stations"])
app.include_router(favori_controller.router, prefix="/favoris", tags=["Favoris"])
app.include_router(fiabilite_controller.router, prefix="/reliability", tags=["Fiabilite"])
app.include_router(recommendation_controller.router, prefix="/recommendation")
app.include_router(compte_controller.router, prefix="/compte", tags=["Compte"])
app.include_router(login_compte_controller.router, prefix="/login-compte", tags=["Login Compte"])


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/hello/{name}", tags=["Misc"])
async def hello_name(name: str):
    """Display Hello."""
    logger.info("Display Hello")
    return {"message": f"Hello {name}"}


@app.get("/reset_database", tags=["Misc"])
async def reset_database():
    """Reset the database."""
    logger.info("Database reset")
    success = ResetDatabase().run()

    return {
        "message": (
            f"Database re-initialization - "
            f"{'SUCCESS' if success else 'FAILURE'}"
        )
    }


# Run the FastAPI application
if __name__ == "__main__":

    ENABLE_GBFS_COLLECTION = choose_collection()

    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "5000")),
    )

    logger.info("Webservice stopped")
