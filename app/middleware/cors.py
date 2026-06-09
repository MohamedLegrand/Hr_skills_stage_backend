"""
Chemin : Hr-skills-stage-backend/app/middleware/cors.py
--------------------------------------------------------
Configuration CORS (Cross-Origin Resource Sharing).
Permet au frontend React de communiquer avec l'API FastAPI.

Auteur : TAKADJIO Mohamed — Developpeur Full Stack
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import obtenir_parametres

parametres = obtenir_parametres()


def configurer_cors(app: FastAPI) -> None:
    """
    Enregistre le middleware CORS sur l'application FastAPI.

    Appelé une seule fois dans main.py :
        from app.middleware.cors import configurer_cors
        configurer_cors(app)
    """
    app.add_middleware(
        CORSMiddleware,
        # Origines autorisées (définies dans .env)
        allow_origins=parametres.ORIGINES_AUTORISEES,
        # Autoriser les cookies et headers d'authentification
        allow_credentials=True,
        # Méthodes HTTP autorisées
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        # Headers autorisés dans les requêtes
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
            "X-Request-ID",
        ],
        # Headers exposés dans les réponses
        expose_headers=[
            "X-Total-Count",     # Pagination — nombre total d'éléments
            "X-Request-ID",      # Identifiant de la requête pour le débogage
        ],
        # Durée de cache du preflight OPTIONS (en secondes)
        max_age=600,
    )