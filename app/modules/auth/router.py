"""
Chemin : Hr-skills-stage-backend/app/modules/auth/router.py
------------------------------------------------------------
Endpoints HTTP pour l'authentification.
Préfixe : /api/v1/auth

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from fastapi import APIRouter, Depends, status

from app.modules.auth.schemas import (
    RequeteConnexion,
    RequeteInscription,
    RequeteRafraichissement,
    RequeteMotDePasseOublie,
    RequeteReinitialiserMDP,
    ReponseJeton,
    ReponseSimple,
)
from app.modules.auth.service import ServiceAuth
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant
from app.shared.constants import PREFIXE_AUTH

routeur = APIRouter(prefix=PREFIXE_AUTH, tags=["Authentification"])


@routeur.post(
    "/connexion",
    response_model=ReponseJeton,
    summary="Connexion",
    description="Connecte un utilisateur et retourne les jetons JWT.",
)
async def connexion(
    donnees: RequeteConnexion,
    session: SessionDB,
) -> ReponseJeton:
    return await ServiceAuth(session).connecter(donnees)


@routeur.post(
    "/inscription",
    response_model=ReponseJeton,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription stagiaire",
    description="Crée un compte stagiaire et retourne les jetons JWT.",
)
async def inscription(
    donnees: RequeteInscription,
    session: SessionDB,
) -> ReponseJeton:
    return await ServiceAuth(session).inscrire_stagiaire(donnees)


@routeur.post(
    "/rafraichissement",
    response_model=ReponseJeton,
    summary="Rafraîchir le jeton",
    description="Génère un nouveau jeton d'accès depuis le refresh token.",
)
async def rafraichir(
    donnees: RequeteRafraichissement,
    session: SessionDB,
) -> ReponseJeton:
    return await ServiceAuth(session).rafraichir_jeton(
        donnees.jeton_rafraichissement
    )


@routeur.post(
    "/deconnexion",
    response_model=ReponseSimple,
    summary="Déconnexion",
    description="Déconnecte l'utilisateur. Côté client, supprimer les jetons.",
)
async def deconnexion(
    utilisateur_courant=Depends(obtenir_utilisateur_courant),
) -> ReponseSimple:
    return ReponseSimple(succes=True, message="Déconnexion réussie")


# ─────────────────────────────────────────────
# MOT DE PASSE OUBLIÉ
# ─────────────────────────────────────────────

@routeur.post(
    "/mot-de-passe-oublie",
    response_model=ReponseSimple,
    summary="Mot de passe oublié",
    description="""
    **Étape 1** — L'utilisateur envoie son adresse email.

    Le système génère un token sécurisé valable **30 minutes**
    et envoie un email avec un lien de réinitialisation.

    Pour des raisons de sécurité, la réponse est identique
    que l'email existe ou non dans la base.
    """,
)
async def mot_de_passe_oublie(
    donnees: RequeteMotDePasseOublie,
    session: SessionDB,
) -> ReponseSimple:
    return await ServiceAuth(session).mot_de_passe_oublie(donnees)


@routeur.post(
    "/reinitialiser-mdp",
    response_model=ReponseSimple,
    summary="Réinitialiser le mot de passe",
    description="""
    **Étape 2** — L'utilisateur envoie le token reçu par email
    avec son nouveau mot de passe.

    Règles du nouveau mot de passe :
    - Minimum 8 caractères
    - Au moins 1 majuscule
    - Au moins 1 chiffre

    Le token est à **usage unique** et expire après **30 minutes**.
    """,
)
async def reinitialiser_mot_de_passe(
    donnees: RequeteReinitialiserMDP,
    session: SessionDB,
) -> ReponseSimple:
    return await ServiceAuth(session).reinitialiser_mot_de_passe(donnees)


@routeur.get(
    "/verifier-token/{token}",
    response_model=ReponseSimple,
    summary="Vérifier la validité d'un token",
    description="""
    Vérifie si un token de réinitialisation est encore valide
    avant que l'utilisateur remplisse le formulaire.
    Utile pour afficher un message d'erreur côté frontend
    avant même que l'utilisateur soumette le formulaire.
    """,
)
async def verifier_token(
    token: str,
    session: SessionDB,
) -> ReponseSimple:
    from app.modules.auth.crud import CrudTokenReinitialisation
    crud = CrudTokenReinitialisation(session)
    token_obj = await crud.obtenir_par_token(token)

    if not token_obj or not token_obj.est_valide:
        return ReponseSimple(
            succes=False,
            message="Ce lien est invalide ou a expiré.",
        )

    return ReponseSimple(
        succes=True,
        message="Lien valide. Vous pouvez définir un nouveau mot de passe.",
    )