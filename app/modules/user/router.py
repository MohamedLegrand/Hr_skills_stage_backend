"""
Chemin : Hr-skills-stage-backend/app/modules/user/router.py
------------------------------------------------------------
Endpoints HTTP du module utilisateur.
Préfixe : /api/v1/utilisateurs

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.schemas import (
    CreationUtilisateur,
    MiseAJourUtilisateur,
    ChangementMotDePasse,
    SortieUtilisateur,
    SortieUtilisateurSimple,
    ListeUtilisateurs,
)
from app.modules.user.service import ServiceUtilisateur
from app.modules.user.models import Utilisateur
from app.core.dependencies import (
    obtenir_utilisateur_courant,
    exiger_role,
    SessionDB,
)
from app.shared.enums import RoleEnum
from app.shared.constants import (
    PREFIXE_UTILISATEURS,
    PAGE_PAR_DEFAUT,
    TAILLE_PAGE_DEFAUT,
    TAILLE_PAGE_MAX,
)

routeur = APIRouter(
    prefix=PREFIXE_UTILISATEURS,
    tags=["Utilisateurs"],
)


# ─────────────────────────────────────────────
# MON PROFIL
# ─────────────────────────────────────────────

@routeur.get(
    "/moi",
    response_model=SortieUtilisateur,
    summary="Obtenir mon profil",
    description="Retourne le profil complet de l'utilisateur connecté.",
)
async def obtenir_mon_profil(
    utilisateur_courant: Utilisateur = Depends(obtenir_utilisateur_courant),
) -> SortieUtilisateur:
    sortie = SortieUtilisateur.model_validate(utilisateur_courant)
    sortie.nom_complet = utilisateur_courant.nom_complet
    return sortie


@routeur.put(
    "/moi",
    response_model=SortieUtilisateur,
    summary="Modifier mon profil",
    description="Modifie le nom, prénom, téléphone ou photo de profil.",
)
async def modifier_mon_profil(
    donnees: MiseAJourUtilisateur,
    session: SessionDB,
    utilisateur_courant: Utilisateur = Depends(obtenir_utilisateur_courant),
) -> SortieUtilisateur:
    service = ServiceUtilisateur(session)
    utilisateur = await service.mettre_a_jour_profil(
        utilisateur_id=utilisateur_courant.id,
        donnees=donnees,
        utilisateur_courant=utilisateur_courant,
    )
    return SortieUtilisateur.model_validate(utilisateur)


@routeur.put(
    "/moi/mot-de-passe",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Changer mon mot de passe",
)
async def changer_mon_mot_de_passe(
    donnees: ChangementMotDePasse,
    session: SessionDB,
    utilisateur_courant: Utilisateur = Depends(obtenir_utilisateur_courant),
) -> None:
    service = ServiceUtilisateur(session)
    await service.changer_mot_de_passe(
        utilisateur_id=utilisateur_courant.id,
        donnees=donnees,
        utilisateur_courant=utilisateur_courant,
    )


# ─────────────────────────────────────────────
# GESTION DES UTILISATEURS (ADMIN)
# ─────────────────────────────────────────────

@routeur.get(
    "/",
    response_model=ListeUtilisateurs,
    summary="Lister tous les utilisateurs",
    description="Réservé à l'administrateur. Supporte la pagination et les filtres.",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def lister_utilisateurs(
    session: SessionDB,
    page: int = Query(default=PAGE_PAR_DEFAUT, ge=1),
    taille_page: int = Query(default=TAILLE_PAGE_DEFAUT, ge=1, le=TAILLE_PAGE_MAX),
    role: Optional[RoleEnum] = Query(default=None),
    est_actif: Optional[bool] = Query(default=None),
) -> ListeUtilisateurs:
    service = ServiceUtilisateur(session)
    return await service.lister_utilisateurs(
        page=page,
        taille_page=taille_page,
        role=role,
        est_actif=est_actif,
    )


@routeur.post(
    "/",
    response_model=SortieUtilisateur,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un utilisateur",
    description="Réservé à l'administrateur. Crée un encadreur ou un admin.",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def creer_utilisateur(
    donnees: CreationUtilisateur,
    session: SessionDB,
) -> SortieUtilisateur:
    service = ServiceUtilisateur(session)
    utilisateur = await service.creer_utilisateur(donnees)
    return SortieUtilisateur.model_validate(utilisateur)


@routeur.get(
    "/encadreurs",
    response_model=list[SortieUtilisateurSimple],
    summary="Lister les encadreurs",
    description="Retourne tous les encadreurs actifs. Accessible à l'admin.",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def lister_encadreurs(session: SessionDB) -> list[SortieUtilisateurSimple]:
    service = ServiceUtilisateur(session)
    encadreurs = await service.lister_encadreurs()
    return [SortieUtilisateurSimple.model_validate(e) for e in encadreurs]


@routeur.get(
    "/{utilisateur_id}",
    response_model=SortieUtilisateur,
    summary="Obtenir un utilisateur par ID",
    description="Réservé à l'administrateur.",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def obtenir_utilisateur(
    utilisateur_id: str,
    session: SessionDB,
) -> SortieUtilisateur:
    service = ServiceUtilisateur(session)
    utilisateur = await service.obtenir_par_id(utilisateur_id)
    return SortieUtilisateur.model_validate(utilisateur)


@routeur.put(
    "/{utilisateur_id}",
    response_model=SortieUtilisateur,
    summary="Modifier un utilisateur",
    description="Réservé à l'administrateur.",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def modifier_utilisateur(
    utilisateur_id: str,
    donnees: MiseAJourUtilisateur,
    session: SessionDB,
    utilisateur_courant: Utilisateur = Depends(obtenir_utilisateur_courant),
) -> SortieUtilisateur:
    service = ServiceUtilisateur(session)
    utilisateur = await service.mettre_a_jour_profil(
        utilisateur_id=utilisateur_id,
        donnees=donnees,
        utilisateur_courant=utilisateur_courant,
    )
    return SortieUtilisateur.model_validate(utilisateur)


@routeur.patch(
    "/{utilisateur_id}/desactiver",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Désactiver un compte",
    description="Réservé à l'administrateur. Désactive sans supprimer.",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def desactiver_compte(
    utilisateur_id: str,
    session: SessionDB,
    utilisateur_courant: Utilisateur = Depends(obtenir_utilisateur_courant),
) -> None:
    service = ServiceUtilisateur(session)
    await service.desactiver_compte(utilisateur_id, utilisateur_courant)


@routeur.patch(
    "/{utilisateur_id}/activer",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Réactiver un compte",
    description="Réservé à l'administrateur.",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def activer_compte(
    utilisateur_id: str,
    session: SessionDB,
) -> None:
    service = ServiceUtilisateur(session)
    await service.activer_compte(utilisateur_id)


@routeur.get(
    "/stats/roles",
    summary="Statistiques par rôle",
    description="Réservé à l'administrateur.",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def statistiques_roles(session: SessionDB) -> dict:
    service = ServiceUtilisateur(session)
    return await service.statistiques_par_role()