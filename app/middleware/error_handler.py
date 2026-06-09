"""
Chemin : Hr-skills-stage-backend/app/middleware/error_handler.py
-----------------------------------------------------------------
Gestion centralisée de toutes les erreurs HTTP.
Garantit que chaque erreur retourne toujours le même
format JSON cohérent au frontend React.

Format de réponse standardisé :
    {
        "succes": false,
        "statut": 404,
        "message": "Utilisateur introuvable",
        "details": null
    }

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.constants import (
    MSG_SERVEUR_ERREUR,
    MSG_VALIDATION_ECHOUEE,
)

logger = logging.getLogger("hr_skills")


# ─────────────────────────────────────────────
# CONSTRUCTEUR DE RÉPONSE D'ERREUR
# ─────────────────────────────────────────────

def construire_reponse_erreur(
    statut: int,
    message: str,
    details=None,
) -> dict:
    """Construit le corps JSON standardisé pour toutes les erreurs."""
    return {
        "succes":  False,
        "statut":  statut,
        "message": message,
        "details": details,
    }


# ─────────────────────────────────────────────
# GESTIONNAIRES D'ERREURS
# ─────────────────────────────────────────────

async def gestionnaire_http(
    requete: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """
    Gère toutes les exceptions HTTP (400, 401, 403, 404, 409...).
    Levées via HTTPException ou nos exceptions personnalisées.
    """
    logger.warning(
        f"HTTP {exc.status_code} | {requete.method} {requete.url.path} "
        f"| {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=construire_reponse_erreur(
            statut=exc.status_code,
            message=exc.detail,
        ),
    )


async def gestionnaire_validation(
    requete: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Gère les erreurs de validation Pydantic (422 Unprocessable Entity).
    Retourne le détail de chaque champ invalide.
    """
    erreurs = []
    for erreur in exc.errors():
        champ = " → ".join(str(l) for l in erreur["loc"] if l != "body")
        erreurs.append({
            "champ":   champ,
            "message": erreur["msg"],
            "valeur":  erreur.get("input"),
        })

    logger.warning(
        f"Validation échouée | {requete.method} {requete.url.path} "
        f"| {len(erreurs)} erreur(s)"
    )

    return JSONResponse(
        status_code=422,
        content=construire_reponse_erreur(
            statut=422,
            message=MSG_VALIDATION_ECHOUEE,
            details=erreurs,
        ),
    )


async def gestionnaire_base_de_donnees(
    requete: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    """
    Gère les erreurs SQLAlchemy inattendues.
    Le message détaillé est loggé mais jamais exposé au client.
    """
    logger.error(
        f"Erreur BDD | {requete.method} {requete.url.path} | {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=construire_reponse_erreur(
            statut=500,
            message="Erreur de base de données — veuillez réessayer",
        ),
    )


async def gestionnaire_generique(
    requete: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Filet de sécurité — capture toute exception non gérée.
    Retourne toujours un 500 sans exposer les détails internes.
    """
    logger.error(
        f"Erreur interne | {requete.method} {requete.url.path} | {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=construire_reponse_erreur(
            statut=500,
            message=MSG_SERVEUR_ERREUR,
        ),
    )


# ─────────────────────────────────────────────
# ENREGISTREMENT DES GESTIONNAIRES
# ─────────────────────────────────────────────

def configurer_gestionnaires_erreurs(app: FastAPI) -> None:
    """
    Enregistre tous les gestionnaires d'erreurs sur l'application.

    Appelé dans main.py :
        from app.middleware.error_handler import configurer_gestionnaires_erreurs
        configurer_gestionnaires_erreurs(app)
    """
    app.add_exception_handler(StarletteHTTPException, gestionnaire_http)
    app.add_exception_handler(RequestValidationError, gestionnaire_validation)
    app.add_exception_handler(SQLAlchemyError, gestionnaire_base_de_donnees)
    app.add_exception_handler(Exception, gestionnaire_generique)