"""
Chemin : Hr-skills-stage-backend/app/middleware/rate_limiter.py
"""
import time
import logging
from collections import defaultdict, deque
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import obtenir_parametres
from app.shared.constants import (
    LIMITE_REQUETES_MINUTE,
    LIMITE_CONNEXIONS_MINUTE,
    LIMITE_UPLOAD_MINUTE,
    PREFIXE_AUTH,
    PREFIXE_DOCUMENTS,
)

parametres = obtenir_parametres()
logger     = logging.getLogger("hr_skills")

historique_requetes:   dict[str, deque] = defaultdict(deque)
historique_connexions: dict[str, deque] = defaultdict(deque)
historique_uploads:    dict[str, deque] = defaultdict(deque)

FENETRE_SECONDES = 60

# Utilise les constantes au lieu de strings codés en dur
ROUTES_CONNEXION = {
    f"{PREFIXE_AUTH}/connexion",
    f"{PREFIXE_AUTH}/inscription",
}
ROUTES_UPLOAD  = {f"{PREFIXE_DOCUMENTS}/"}
ROUTES_EXCLUES = {"/health", "/docs", "/redoc", "/openapi.json", "/"}


def compter_requetes_recentes(historique: dict[str, deque], cle: str) -> int:
    maintenant = time.time()
    file = historique[cle]
    while file and file[0] < maintenant - FENETRE_SECONDES:
        file.popleft()
    file.append(maintenant)
    return len(file)


class MiddlewareLimiteDebit(BaseHTTPMiddleware):
    async def dispatch(self, requete: Request, suivant: Callable) -> Response:
        chemin = requete.url.path

        if chemin in ROUTES_EXCLUES:
            return await suivant(requete)

        ip = requete.headers.get("X-Forwarded-For", requete.client.host if requete.client else "unknown")

        if chemin in ROUTES_CONNEXION:
            nb = compter_requetes_recentes(historique_connexions, ip)
            if nb > LIMITE_CONNEXIONS_MINUTE:
                logger.warning(f"Rate limit connexion | IP: {ip} | {nb}/min")
                return JSONResponse(status_code=429, content={
                    "succes": False, "statut": 429,
                    "message": f"Trop de tentatives. Réessayez dans {FENETRE_SECONDES} secondes.",
                })

        elif any(chemin.startswith(r) for r in ROUTES_UPLOAD):
            nb = compter_requetes_recentes(historique_uploads, ip)
            if nb > LIMITE_UPLOAD_MINUTE:
                logger.warning(f"Rate limit upload | IP: {ip} | {nb}/min")
                return JSONResponse(status_code=429, content={
                    "succes": False, "statut": 429,
                    "message": f"Trop de fichiers déposés. Réessayez dans {FENETRE_SECONDES} secondes.",
                })

        else:
            nb = compter_requetes_recentes(historique_requetes, ip)
            if nb > LIMITE_REQUETES_MINUTE:
                logger.warning(f"Rate limit global | IP: {ip} | {nb}/min")
                return JSONResponse(status_code=429, content={
                    "succes": False, "statut": 429,
                    "message": f"Trop de requêtes. Réessayez dans {FENETRE_SECONDES} secondes.",
                })

        return await suivant(requete)


def configurer_limite_debit(app: FastAPI) -> None:
    app.add_middleware(MiddlewareLimiteDebit)