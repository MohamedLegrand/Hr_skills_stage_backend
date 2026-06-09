"""
Chemin : Hr-skills-stage-backend/app/modules/attendance/router.py
Préfixe : /api/v1/presences
"""
from fastapi import APIRouter, Depends, status
from app.modules.attendance.schemas import MarquagePresence, SortiePresence, ResumePresences
from app.modules.attendance.service import ServicePresence
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_PRESENCES

routeur = APIRouter(prefix=PREFIXE_PRESENCES, tags=["Présences"])


@routeur.post("/", response_model=SortiePresence, status_code=status.HTTP_201_CREATED, summary="Marquer une présence",
              dependencies=[Depends(exiger_role(RoleEnum.ENCADREUR, RoleEnum.ADMIN))])
async def marquer(donnees: MarquagePresence, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortiePresence:
    p = await ServicePresence(session).marquer(donnees, utilisateur.id)
    return SortiePresence.model_validate(p)


@routeur.get("/{inscription_id}", response_model=list[SortiePresence], summary="Historique des présences")
async def historique(inscription_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> list[SortiePresence]:
    return await ServicePresence(session).lister_par_inscription(inscription_id)


@routeur.get("/{inscription_id}/resume", response_model=ResumePresences, summary="Résumé des présences")
async def resume(inscription_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> ResumePresences:
    return await ServicePresence(session).resume(inscription_id)