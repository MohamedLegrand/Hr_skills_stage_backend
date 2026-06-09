"""
Chemin : Hr-skills-stage-backend/app/core/exceptions.py
---------------------------------------------------------
Exceptions HTTP personnalisées du projet HR-Skills Stage.
Utilisées dans les services et les routes pour retourner
des réponses d'erreur cohérentes.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from fastapi import HTTPException, status
from app.shared.constants import (
    MSG_NON_AUTORISE,
    MSG_ACCES_INTERDIT,
    MSG_NON_TROUVE,
    MSG_VALIDATION_ECHOUEE,
    MSG_SERVEUR_ERREUR,
    MSG_EMAIL_DEJA_UTILISE,
    MSG_IDENTIFIANTS_INVALIDES,
    MSG_COMPTE_INACTIF,
    MSG_FICHIER_TROP_GRAND,
    MSG_TYPE_FICHIER_INVALIDE,
    MSG_DOCUMENT_DEJA_SOUMIS,
    MSG_PAIEMENT_DEJA_CONFIRME,
    MSG_STAGE_COMPLET,
    MSG_DEJA_INSCRIT,
)


# ─────────────────────────────────────────────
# 401 — NON AUTHENTIFIÉ
# ─────────────────────────────────────────────
class NonAutorise(HTTPException):
    """
    Levée quand l'utilisateur n'est pas authentifié
    ou que le jeton JWT est invalide / expiré.
    """
    def __init__(self, detail: str = MSG_NON_AUTORISE):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─────────────────────────────────────────────
# 403 — ACCÈS INTERDIT
# ─────────────────────────────────────────────
class AccesInterdit(HTTPException):
    """
    Levée quand l'utilisateur est authentifié mais
    ne dispose pas des droits nécessaires (mauvais rôle).
    """
    def __init__(self, detail: str = MSG_ACCES_INTERDIT):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


# ─────────────────────────────────────────────
# 404 — RESSOURCE INTROUVABLE
# ─────────────────────────────────────────────
class NonTrouve(HTTPException):
    """
    Levée quand une ressource demandée n'existe pas en base.
    """
    def __init__(self, ressource: str = "Ressource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{ressource} introuvable",
        )


# ─────────────────────────────────────────────
# 409 — CONFLIT
# ─────────────────────────────────────────────
class Conflit(HTTPException):
    """
    Levée quand une ressource existe déjà (doublon).
    Ex : email déjà utilisé, déjà inscrit au stage.
    """
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


# ─────────────────────────────────────────────
# 400 — REQUÊTE INVALIDE
# ─────────────────────────────────────────────
class RequeteInvalide(HTTPException):
    """
    Levée quand les données soumises sont incorrectes
    ou ne respectent pas les règles métier.
    """
    def __init__(self, detail: str = MSG_VALIDATION_ECHOUEE):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


# ─────────────────────────────────────────────
# 500 — ERREUR INTERNE SERVEUR
# ─────────────────────────────────────────────
class ErreurServeur(HTTPException):
    """
    Levée pour les erreurs internes inattendues.
    """
    def __init__(self, detail: str = MSG_SERVEUR_ERREUR):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


# ─────────────────────────────────────────────
# EXCEPTIONS MÉTIER SPÉCIALISÉES
# ─────────────────────────────────────────────

class IdentifiantsInvalides(NonAutorise):
    """Email ou mot de passe incorrect lors de la connexion."""
    def __init__(self):
        super().__init__(detail=MSG_IDENTIFIANTS_INVALIDES)


class CompteInactif(AccesInterdit):
    """Le compte utilisateur a été désactivé."""
    def __init__(self):
        super().__init__(detail=MSG_COMPTE_INACTIF)


class EmailDejaUtilise(Conflit):
    """L'adresse email est déjà associée à un compte."""
    def __init__(self):
        super().__init__(detail=MSG_EMAIL_DEJA_UTILISE)


class FichierTropGrand(RequeteInvalide):
    """Le fichier déposé dépasse la taille maximale autorisée."""
    def __init__(self):
        super().__init__(detail=MSG_FICHIER_TROP_GRAND)


class TypeFichierInvalide(RequeteInvalide):
    """Le type MIME du fichier n'est pas autorisé (PDF uniquement)."""
    def __init__(self):
        super().__init__(detail=MSG_TYPE_FICHIER_INVALIDE)


class DocumentDejaExistant(Conflit):
    """Un document de ce type a déjà été soumis pour cette inscription."""
    def __init__(self):
        super().__init__(detail=MSG_DOCUMENT_DEJA_SOUMIS)


class PaiementDejaConfirme(Conflit):
    """Ce paiement a déjà été confirmé — doublon webhook."""
    def __init__(self):
        super().__init__(detail=MSG_PAIEMENT_DEJA_CONFIRME)


class StageComplet(RequeteInvalide):
    """L'offre de stage n'a plus de places disponibles."""
    def __init__(self):
        super().__init__(detail=MSG_STAGE_COMPLET)


class DejaInscrit(Conflit):
    """Le stagiaire est déjà inscrit à cette offre de stage."""
    def __init__(self):
        super().__init__(detail=MSG_DEJA_INSCRIT)