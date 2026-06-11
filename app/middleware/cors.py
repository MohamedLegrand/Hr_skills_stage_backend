"""
Chemin : Hr-skills-stage-backend/app/middleware/cors.py
--------------------------------------------------------
Configuration CORS (Cross-Origin Resource Sharing).
Permet au frontend React de communiquer avec l'API FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import parametres


def configurer_cors(app: FastAPI) -> None:
    """
    Enregistre le middleware CORS sur l'application FastAPI.
    """
    # Récupère la liste des origines depuis la propriété
    origines = parametres.ORIGINES_AUTORISEES
    
    print("=" * 60)
    print("🔍 CONFIGURATION CORS")
    print(f"   Origines autorisées : {origines}")
    print(f"   Type : {type(origines)}")
    print("=" * 60)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origines,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "X-Requested-With",
            "X-Request-ID",
        ],
        expose_headers=[
            "X-Total-Count",
            "X-Request-ID",
        ],
        max_age=600,
    )