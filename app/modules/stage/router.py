"""
Chemin : Hr-skills-stage-backend/app/modules/stage/router.py
Préfixe : /api/v1/offres-stage
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.modules.stage.schemas import CreationOffre, MiseAJourOffre, SortieOffre, ListeOffres
from app.modules.stage.service import ServiceOffre
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum, StatutOffre
from app.shared.constants import PREFIXE_OFFRES

routeur = APIRouter(prefix=PREFIXE_OFFRES, tags=["Offres de stage"])


@routeur.get("/", response_model=ListeOffres, summary="Lister les offres")
async def lister(
    session: SessionDB,
    page: int = Query(1, ge=1),
    taille: int = Query(20, ge=1, le=100),
    statut: Optional[StatutOffre] = None,
    domaine: Optional[str] = None,
) -> ListeOffres:
    return await ServiceOffre(session).lister(page, taille, statut, domaine)


@routeur.get("/{offre_id}", response_model=SortieOffre, summary="Détail d'une offre")
async def detail(offre_id: str, session: SessionDB) -> SortieOffre:
    offre = await ServiceOffre(session).obtenir_par_id(offre_id)
    return SortieOffre.model_validate(offre)


@routeur.post(
    "/", response_model=SortieOffre,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une offre",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def creer(
    donnees: CreationOffre, session: SessionDB,
    utilisateur=Depends(obtenir_utilisateur_courant),
) -> SortieOffre:
    offre = await ServiceOffre(session).creer(donnees, utilisateur.id)
    return SortieOffre.model_validate(offre)


@routeur.put(
    "/{offre_id}", response_model=SortieOffre,
    summary="Modifier une offre",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def modifier(offre_id: str, donnees: MiseAJourOffre, session: SessionDB) -> SortieOffre:
    offre = await ServiceOffre(session).mettre_a_jour(offre_id, donnees)
    return SortieOffre.model_validate(offre)


@routeur.patch(
    "/{offre_id}/archiver",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archiver une offre",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def archiver(offre_id: str, session: SessionDB) -> None:
    await ServiceOffre(session).archiver(offre_id)