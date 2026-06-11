"""
Chemin : Hr-skills-stage-backend/app/core/security.py
-------------------------------------------------------
Hachage et vérification des mots de passe avec bcrypt.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import bcrypt as _bcrypt
from app.shared.constants import ROUNDS_BCRYPT


def hacher_mot_de_passe(mot_de_passe_clair: str) -> str:
    sel = _bcrypt.gensalt(rounds=ROUNDS_BCRYPT)
    return _bcrypt.hashpw(mot_de_passe_clair.encode("utf-8"), sel).decode("utf-8")


def verifier_mot_de_passe(mot_de_passe_clair: str, hash_stocke: str) -> bool:
    try:
        return _bcrypt.checkpw(
            mot_de_passe_clair.encode("utf-8"),
            hash_stocke.encode("utf-8"),
        )
    except Exception:
        return False


def mot_de_passe_necessite_rehachage(hash_stocke: str) -> bool:
    try:
        parties = hash_stocke.split("$")
        rounds_stockes = int(parties[2])
        return rounds_stockes < ROUNDS_BCRYPT
    except Exception:
        return False