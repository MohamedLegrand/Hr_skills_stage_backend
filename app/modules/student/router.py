"""
Chemin : Hr-skills-stage-backend/app/modules/student/router.py
Préfixe : /api/v1/stagiaire
"""
from fastapi import APIRouter, Depends
from app.modules.student.schemas import TableauBordStagiaire
from app.modules.student.service import ServiceStagiaire
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_STAGIAIRE

routeur = APIRouter(
    prefix=PREFIXE_STAGIAIRE, tags=["Espace Stagiaire"],
    dependencies=[Depends(exiger_role(RoleEnum.STAGIAIRE))],
)


@routeur.get("/tableau-bord", response_model=TableauBordStagiaire, summary="Tableau de bord du stagiaire")
async def tableau_bord(session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> TableauBordStagiaire:
    return await ServiceStagiaire(session).tableau_bord(utilisateur.id)