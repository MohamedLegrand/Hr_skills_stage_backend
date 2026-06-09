"""
Chemin : Hr-skills-stage-backend/app/modules/user/schemas.py
-------------------------------------------------------------
Schémas Pydantic pour le module utilisateur.
Valident les données entrantes et formatent les réponses sortantes.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.shared.enums import RoleEnum


# ─────────────────────────────────────────────
# SCHÉMAS DE BASE
# ─────────────────────────────────────────────

class UtilisateurBase(BaseModel):
    """Champs communs à la création et la mise à jour."""
    nom:       str = Field(..., min_length=2, max_length=100, examples=["TAKADJIO"])
    prenom:    str = Field(..., min_length=2, max_length=100, examples=["Mohamed"])
    courriel:  EmailStr = Field(..., examples=["mohamed@hr-skills.cm"])
    telephone: Optional[str] = Field(None, max_length=25, examples=["+237 6XX XXX XXX"])


# ─────────────────────────────────────────────
# CRÉATION D'UN UTILISATEUR
# ─────────────────────────────────────────────

class CreationUtilisateur(UtilisateurBase):
    """
    Schéma utilisé pour créer un nouvel utilisateur.
    Le mot de passe est hashé dans le service avant insertion.
    """
    mot_de_passe:         str      = Field(..., min_length=8, examples=["MotDePasse123!"])
    confirmation_mdp:     str      = Field(..., min_length=8, examples=["MotDePasse123!"])
    role:                 RoleEnum = Field(default=RoleEnum.STAGIAIRE)

    @field_validator("nom", "prenom")
    @classmethod
    def mettre_en_majuscule(cls, valeur: str) -> str:
        return valeur.strip().title()

    @field_validator("confirmation_mdp")
    @classmethod
    def mots_de_passe_identiques(cls, confirmation: str, info) -> str:
        mot_de_passe = info.data.get("mot_de_passe")
        if mot_de_passe and confirmation != mot_de_passe:
            raise ValueError("Les mots de passe ne correspondent pas")
        return confirmation

    @field_validator("mot_de_passe")
    @classmethod
    def valider_complexite(cls, valeur: str) -> str:
        if not any(c.isupper() for c in valeur):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.isdigit() for c in valeur):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return valeur


# ─────────────────────────────────────────────
# MISE À JOUR DU PROFIL
# ─────────────────────────────────────────────

class MiseAJourUtilisateur(BaseModel):
    """
    Schéma pour modifier le profil.
    Tous les champs sont optionnels — on met à jour seulement ce qui est fourni.
    """
    nom:       Optional[str] = Field(None, min_length=2, max_length=100)
    prenom:    Optional[str] = Field(None, min_length=2, max_length=100)
    telephone: Optional[str] = Field(None, max_length=25)
    url_photo: Optional[str] = Field(None, max_length=500)

    @field_validator("nom", "prenom")
    @classmethod
    def mettre_en_majuscule(cls, valeur: Optional[str]) -> Optional[str]:
        if valeur:
            return valeur.strip().title()
        return valeur


class ChangementMotDePasse(BaseModel):
    """Schéma pour changer le mot de passe."""
    ancien_mot_de_passe:  str = Field(..., min_length=8)
    nouveau_mot_de_passe: str = Field(..., min_length=8)
    confirmation_mdp:     str = Field(..., min_length=8)

    @field_validator("confirmation_mdp")
    @classmethod
    def mots_de_passe_identiques(cls, confirmation: str, info) -> str:
        nouveau = info.data.get("nouveau_mot_de_passe")
        if nouveau and confirmation != nouveau:
            raise ValueError("Les mots de passe ne correspondent pas")
        return confirmation


# ─────────────────────────────────────────────
# RÉPONSES (SORTIES)
# ─────────────────────────────────────────────

class SortieUtilisateur(BaseModel):
    """
    Schéma de réponse — ne retourne jamais le mot de passe.
    Utilisé dans toutes les réponses API impliquant un utilisateur.
    """
    id:                 str
    nom:                str
    prenom:             str
    courriel:           str
    role:               RoleEnum
    telephone:          Optional[str]
    url_photo:          Optional[str]
    est_actif:          bool
    derniere_connexion: Optional[datetime]
    cree_le:            datetime
    mis_a_jour_le:      datetime
    nom_complet:        Optional[str] = None

    model_config = {"from_attributes": True}


class SortieUtilisateurSimple(BaseModel):
    """
    Version allégée — utilisée dans les listes et les relations.
    """
    id:        str
    nom:       str
    prenom:    str
    courriel:  str
    role:      RoleEnum
    est_actif: bool
    url_photo: Optional[str]

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# PAGINATION
# ─────────────────────────────────────────────

class ListeUtilisateurs(BaseModel):
    """Réponse paginée pour la liste des utilisateurs."""
    total:        int
    page:         int
    taille_page:  int
    utilisateurs: list[SortieUtilisateurSimple]