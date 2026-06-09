"""
Chemin : Hr-skills-stage-backend/app/core/security.py
-------------------------------------------------------
Hachage et vérification des mots de passe avec bcrypt.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from passlib.context import CryptContext
from app.shared.constants import ROUNDS_BCRYPT

# Contexte bcrypt — schèmes autorisés
contexte_crypto = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=ROUNDS_BCRYPT,
)


def hacher_mot_de_passe(mot_de_passe_clair: str) -> str:
    """
    Hache un mot de passe en clair avec bcrypt.

    Exemple :
        hash = hacher_mot_de_passe("MonMotDePasse123!")
    """
    return contexte_crypto.hash(mot_de_passe_clair)


def verifier_mot_de_passe(mot_de_passe_clair: str, hash_stocke: str) -> bool:
    """
    Compare un mot de passe en clair avec son hash bcrypt stocké.
    Retourne True si le mot de passe correspond, False sinon.

    Exemple :
        est_valide = verifier_mot_de_passe("MonMotDePasse123!", hash_bdd)
    """
    return contexte_crypto.verify(mot_de_passe_clair, hash_stocke)


def mot_de_passe_necessite_rehachage(hash_stocke: str) -> bool:
    """
    Vérifie si le hash doit être mis à jour
    (par exemple si le nombre de rounds bcrypt a changé).
    """
    return contexte_crypto.needs_update(hash_stocke)