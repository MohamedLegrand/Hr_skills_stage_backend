"""
Chemin : Hr-skills-stage-backend/app/middleware/logging.py
-----------------------------------------------------------
Middleware de journalisation des requêtes et réponses HTTP.
Enregistre : méthode, route, code de réponse, durée, IP client.

Auteur : TAKADJIO Mohamed — Developpeur Full Stack
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.shared.constants import FORMAT_LOG, FICHIER_LOG, FICHIER_LOG_ERREURS

# ─────────────────────────────────────────────
# CONFIGURATION DU LOGGER
# ─────────────────────────────────────────────

def configurer_logger() -> logging.Logger:
    """Configure et retourne le logger principal du projet."""
    logger = logging.getLogger("hr_skills")
    logger.setLevel(logging.DEBUG)

    formateur = logging.Formatter(FORMAT_LOG)

    # Handler console
    handler_console = logging.StreamHandler()
    handler_console.setLevel(logging.INFO)
    handler_console.setFormatter(formateur)

    # Handler fichier — toutes les requêtes
    handler_fichier = logging.FileHandler(FICHIER_LOG, encoding="utf-8")
    handler_fichier.setLevel(logging.INFO)
    handler_fichier.setFormatter(formateur)

    # Handler fichier — erreurs uniquement
    handler_erreurs = logging.FileHandler(FICHIER_LOG_ERREURS, encoding="utf-8")
    handler_erreurs.setLevel(logging.ERROR)
    handler_erreurs.setFormatter(formateur)

    if not logger.handlers:
        logger.addHandler(handler_console)
        logger.addHandler(handler_fichier)
        logger.addHandler(handler_erreurs)

    return logger


logger = configurer_logger()


# ─────────────────────────────────────────────
# MIDDLEWARE DE JOURNALISATION
# ─────────────────────────────────────────────

class MiddlewareJournalisation(BaseHTTPMiddleware):
    """
    Intercepte chaque requête HTTP pour :
        - Générer un identifiant unique de requête (X-Request-ID)
        - Mesurer le temps de traitement
        - Journaliser : méthode, route, IP, statut, durée
        - Logger les erreurs 4xx et 5xx séparément
    """

    async def dispatch(self, requete: Request, suivant: Callable) -> Response:
        # Identifiant unique pour tracer la requête dans les logs
        id_requete = str(uuid.uuid4())[:8]

        # Heure de début
        debut = time.perf_counter()

        # Adresse IP du client (prend en compte les proxies)
        ip_client = requete.headers.get("X-Forwarded-For", requete.client.host)

        # Log de la requête entrante
        logger.info(
            f"→ [{id_requete}] {requete.method} {requete.url.path} "
            f"| IP: {ip_client}"
        )

        # Traitement de la requête
        reponse: Response = await suivant(requete)

        # Durée de traitement
        duree_ms = round((time.perf_counter() - debut) * 1000, 2)

        # Ajout de l'identifiant de requête dans les headers de réponse
        reponse.headers["X-Request-ID"] = id_requete

        # Log de la réponse
        niveau = (
            logging.ERROR   if reponse.status_code >= 500
            else logging.WARNING if reponse.status_code >= 400
            else logging.INFO
        )

        logger.log(
            niveau,
            f"← [{id_requete}] {requete.method} {requete.url.path} "
            f"| {reponse.status_code} | {duree_ms}ms"
        )

        return reponse


def configurer_journalisation(app: FastAPI) -> None:
    """
    Enregistre le middleware de journalisation sur l'application.

    Appelé dans main.py :
        from app.middleware.logging import configurer_journalisation
        configurer_journalisation(app)
    """
    app.add_middleware(MiddlewareJournalisation)