"""
Chemin : Hr-skills-stage-backend/app/modules/convention/router.py
Préfixe : /api/v1/conventions
"""
from fastapi import APIRouter, Depends, status
from app.modules.convention.schemas import RequeteConvention, SortieConvention
from app.modules.convention.service import ServiceConvention
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_CONVENTIONS

routeur = APIRouter(prefix=PREFIXE_CONVENTIONS, tags=["Conventions"])


@routeur.post("/generer", response_model=SortieConvention, status_code=status.HTTP_201_CREATED,
              summary="Générer une convention PDF", dependencies=[Depends(exiger_role(RoleEnum.ADMIN))])
async def generer(donnees: RequeteConvention, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieConvention:
    c = await ServiceConvention(session).generer(donnees.inscription_id, utilisateur.id)
    return SortieConvention.model_validate(c)


@routeur.get("/{inscription_id}", response_model=SortieConvention, summary="Convention d'une inscription")
async def obtenir(inscription_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieConvention:
    c = await ServiceConvention(session).obtenir_par_inscription(inscription_id)
    return SortieConvention.model_validate(c)