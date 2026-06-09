"""
Chemin : Hr-skills-stage-backend/app/modules/auth/schemas.py
------------------------------------------------------------
Schémas Pydantic pour le module authentification.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.modules.user.schemas import SortieUtilisateur


# ─────────────────────────────────────────────
# CONNEXION / INSCRIPTION
# ─────────────────────────────────────────────

class RequeteConnexion(BaseModel):
    courriel:     EmailStr = Field(..., examples=["admin@hr-skills.cm"])
    mot_de_passe: str      = Field(..., min_length=8)


class RequeteInscription(BaseModel):
    nom:              str        = Field(..., min_length=2, max_length=100)
    prenom:           str        = Field(..., min_length=2, max_length=100)
    courriel:         EmailStr
    mot_de_passe:     str        = Field(..., min_length=8)
    confirmation_mdp: str        = Field(..., min_length=8)
    telephone:        str | None = None


class ReponseJeton(BaseModel):
    jeton_acces:            str
    jeton_rafraichissement: str
    type_jeton:             str = "Bearer"
    utilisateur:            SortieUtilisateur


class RequeteRafraichissement(BaseModel):
    jeton_rafraichissement: str


class ReponseSimple(BaseModel):
    succes:  bool
    message: str


# ─────────────────────────────────────────────
# MOT DE PASSE OUBLIÉ
# ─────────────────────────────────────────────

class RequeteMotDePasseOublie(BaseModel):
    """
    Étape 1 : l'utilisateur envoie son adresse email.
    Le système lui envoie un lien de réinitialisation.
    """
    courriel: EmailStr = Field(
        ...,
        examples=["mohamed@hr-skills.cm"],
        description="Adresse email du compte à réinitialiser",
    )


class RequeteReinitialiserMDP(BaseModel):
    """
    Étape 2 : l'utilisateur envoie le token reçu par email
    avec son nouveau mot de passe.
    Le token est valable 30 minutes et à usage unique.
    """
    token:                str = Field(
        ...,
        min_length=10,
        description="Token reçu par email",
    )
    nouveau_mot_de_passe: str = Field(
        ...,
        min_length=8,
        description="Nouveau mot de passe (min 8 caractères, 1 majuscule, 1 chiffre)",
    )
    confirmation_mdp:     str = Field(..., min_length=8)

    @field_validator("confirmation_mdp")
    @classmethod
    def mots_de_passe_identiques(cls, confirmation: str, info) -> str:
        nouveau = info.data.get("nouveau_mot_de_passe")
        if nouveau and confirmation != nouveau:
            raise ValueError("Les mots de passe ne correspondent pas")
        return confirmation

    @field_validator("nouveau_mot_de_passe")
    @classmethod
    def valider_complexite(cls, valeur: str) -> str:
        if not any(c.isupper() for c in valeur):
            raise ValueError(
                "Le mot de passe doit contenir au moins une majuscule"
            )
        if not any(c.isdigit() for c in valeur):
            raise ValueError(
                "Le mot de passe doit contenir au moins un chiffre"
            )
        return valeur