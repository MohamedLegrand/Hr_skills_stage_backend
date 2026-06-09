"""
Chemin : Hr-skills-stage-backend/app/modules/report/router.py
Préfixe : /api/v1/rapports
"""
from fastapi import APIRouter, Depends, status
from app.modules.report.schemas import SortieRapport
from app.modules.report.service import ServiceRapport
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_RAPPORTS

routeur = APIRouter(prefix=PREFIXE_RAPPORTS, tags=["Rapports"])


@routeur.post("/{inscription_id}/attestation", response_model=SortieRapport,
              status_code=status.HTTP_201_CREATED, summary="Générer l'attestation finale",
              dependencies=[Depends(exiger_role(RoleEnum.ADMIN))])
async def generer_attestation(inscription_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieRapport:
    r = await ServiceRapport(session).generer_attestation(inscription_id, utilisateur.id)
    return SortieRapport.model_validate(r)


@routeur.get("/{inscription_id}", response_model=list[SortieRapport], summary="Rapports d'une inscription")
async def lister(inscription_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> list[SortieRapport]:
    return await ServiceRapport(session).lister_par_inscription(inscription_id)