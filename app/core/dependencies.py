"""
Chemin : Hr-skills-stage-backend/app/core/dependencies.py
----------------------------------------------------------
Injections de dépendances FastAPI.
Utilisées dans les routers via Depends() pour
sécuriser les routes et vérifier les rôles.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import decoder_jeton, obtenir_id_depuis_jeton
from app.core.exceptions import NonAutorise, AccesInterdit, NonTrouve, CompteInactif
from app.database.session import obtenir_session
from app.shared.enums import RoleEnum

# Schème OAuth2 — pointe vers l'endpoint de connexion
schema_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/connexion")


# ─────────────────────────────────────────────
# OBTENIR L'UTILISATEUR COURANT
# ─────────────────────────────────────────────

async def obtenir_utilisateur_courant(
    jeton: Annotated[str, Depends(schema_oauth2)],
    session: Annotated[AsyncSession, Depends(obtenir_session)],
):
    """
    Dépendance principale : décode le JWT et retourne
    l'utilisateur authentifié depuis la base de données.

    Lève NonAutorise si le jeton est invalide.
    Lève NonTrouve si l'utilisateur n'existe plus en BDD.
    Lève CompteInactif si le compte est désactivé.

    Utilisation dans un router :
        @router.get("/moi")
        async def moi(utilisateur = Depends(obtenir_utilisateur_courant)):
            return utilisateur
    """
    # Import ici pour éviter les imports circulaires
    from app.modules.user.crud import CrudUtilisateur

    payload = decoder_jeton(jeton)

    utilisateur_id: str | None = payload.get("sub")
    if not utilisateur_id:
        raise NonAutorise(detail="Jeton invalide : identifiant manquant")

    crud = CrudUtilisateur(session)
    utilisateur = await crud.obtenir_par_id(utilisateur_id)

    if not utilisateur:
        raise NonTrouve("Utilisateur")

    if not utilisateur.est_actif:
        raise CompteInactif()

    return utilisateur


# ─────────────────────────────────────────────
# VÉRIFICATION DES RÔLES
# ─────────────────────────────────────────────

def exiger_role(*roles_autorises: RoleEnum):
    """
    Fabrique de dépendances pour restreindre l'accès par rôle.

    Utilisation :
        @router.get("/admin/stats")
        async def stats(
            utilisateur = Depends(exiger_role(RoleEnum.ADMIN))
        ):
            ...

        # Plusieurs rôles autorisés :
        @router.get("/documents")
        async def documents(
            utilisateur = Depends(exiger_role(RoleEnum.ADMIN, RoleEnum.ENCADREUR))
        ):
            ...
    """
    async def verifier_role(
        utilisateur=Depends(obtenir_utilisateur_courant),
    ):
        if utilisateur.role not in [r.value for r in roles_autorises]:
            raise AccesInterdit(
                detail=f"Accès réservé aux rôles : "
                       f"{', '.join(r.value for r in roles_autorises)}"
            )
        return utilisateur

    return verifier_role


# ─────────────────────────────────────────────
# DÉPENDANCES PRÊTES À L'EMPLOI PAR RÔLE
# ─────────────────────────────────────────────

# Accès réservé à l'administrateur uniquement
UtilisateurAdmin = Depends(exiger_role(RoleEnum.ADMIN))

# Accès réservé à l'encadreur uniquement
UtilisateurEncadreur = Depends(exiger_role(RoleEnum.ENCADREUR))

# Accès réservé au stagiaire uniquement
UtilisateurStagiaire = Depends(exiger_role(RoleEnum.STAGIAIRE))

# Accès admin ou encadreur
UtilisateurAdminOuEncadreur = Depends(
    exiger_role(RoleEnum.ADMIN, RoleEnum.ENCADREUR)
)

# Accès à tout utilisateur authentifié (tous rôles)
UtilisateurAuthentifie = Depends(obtenir_utilisateur_courant)


# ─────────────────────────────────────────────
# DÉPENDANCE : SESSION BASE DE DONNÉES
# ─────────────────────────────────────────────

SessionDB = Annotated[AsyncSession, Depends(obtenir_session)]