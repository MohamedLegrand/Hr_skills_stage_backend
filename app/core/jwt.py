"""
Chemin : Hr-skills-stage-backend/app/core/jwt.py
-------------------------------------------------
Création et décodage des jetons JWT (access token + refresh token).

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt
from jwt.exceptions import PyJWTError

from app.core.config import obtenir_parametres
from app.core.exceptions import NonAutorise
from app.shared.constants import (
    ALGORITHME_JWT,
    DUREE_JETON_ACCES_MINUTES,
    DUREE_JETON_RAFRAICH_JOURS,
    MSG_NON_AUTORISE,
)

parametres = obtenir_parametres()


# ─────────────────────────────────────────────
# CRÉATION DES JETONS
# ─────────────────────────────────────────────

def creer_jeton_acces(
    utilisateur_id: str | UUID,
    role: str,
    courriel: str,
    duree_minutes: Optional[int] = None,
) -> str:
    """
    Crée un jeton d'accès JWT (access token).
    Durée par défaut : 24 heures.

    Payload inclus :
        - sub  : identifiant de l'utilisateur
        - role : rôle de l'utilisateur
        - email: adresse email
        - type : "access"
        - exp  : date d'expiration
    """
    duree = duree_minutes or DUREE_JETON_ACCES_MINUTES
    expiration = datetime.now(timezone.utc) + timedelta(minutes=duree)

    payload = {
        "sub":   str(utilisateur_id),
        "role":  role,
        "email": courriel,
        "type":  "access",
        "exp":   expiration,
        "iat":   datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        parametres.SECRET_KEY,
        algorithm=ALGORITHME_JWT,
    )


def creer_jeton_rafraichissement(
    utilisateur_id: str | UUID,
    duree_jours: Optional[int] = None,
) -> str:
    """
    Crée un jeton de rafraîchissement JWT (refresh token).
    Durée par défaut : 7 jours.

    Payload inclus :
        - sub  : identifiant de l'utilisateur
        - type : "refresh"
        - exp  : date d'expiration
    """
    duree = duree_jours or DUREE_JETON_RAFRAICH_JOURS
    expiration = datetime.now(timezone.utc) + timedelta(days=duree)

    payload = {
        "sub":  str(utilisateur_id),
        "type": "refresh",
        "exp":  expiration,
        "iat":  datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        parametres.SECRET_KEY,
        algorithm=ALGORITHME_JWT,
    )


# ─────────────────────────────────────────────
# DÉCODAGE ET VALIDATION DES JETONS
# ─────────────────────────────────────────────

def decoder_jeton(jeton: str) -> dict:
    """
    Décode et valide un jeton JWT.
    Lève NonAutorise si le jeton est invalide ou expiré.
    """
    try:
        payload = jwt.decode(
            jeton,
            parametres.SECRET_KEY,
            algorithms=[ALGORITHME_JWT],
        )
        return payload
    except PyJWTError:
        raise NonAutorise(detail="Jeton invalide ou expiré")


def obtenir_id_depuis_jeton(jeton: str) -> str:
    """
    Extrait l'identifiant utilisateur (sub) d'un jeton JWT.
    Lève NonAutorise si le jeton est invalide.
    """
    payload = decoder_jeton(jeton)
    utilisateur_id: Optional[str] = payload.get("sub")

    if not utilisateur_id:
        raise NonAutorise(detail="Jeton invalide : identifiant manquant")

    return utilisateur_id


def obtenir_role_depuis_jeton(jeton: str) -> str:
    """
    Extrait le rôle de l'utilisateur depuis un jeton JWT.
    """
    payload = decoder_jeton(jeton)
    role: Optional[str] = payload.get("role")

    if not role:
        raise NonAutorise(detail="Jeton invalide : rôle manquant")

    return role


def valider_jeton_rafraichissement(jeton: str) -> str:
    """
    Valide un refresh token et retourne l'identifiant utilisateur.
    Lève NonAutorise si le type n'est pas 'refresh'.
    """
    payload = decoder_jeton(jeton)

    if payload.get("type") != "refresh":
        raise NonAutorise(detail="Ce jeton n'est pas un jeton de rafraîchissement")

    utilisateur_id: Optional[str] = payload.get("sub")
    if not utilisateur_id:
        raise NonAutorise(detail="Jeton de rafraîchissement invalide")

    return utilisateur_id