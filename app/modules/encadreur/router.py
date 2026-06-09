"""
Chemin : Hr-skills-stage-backend/app/modules/encadreur/router.py
Préfixe : /api/v1/encadreur
"""
from fastapi import APIRouter, Depends
from app.modules.encadreur.schemas import TableauBordEncadreur
from app.modules.encadreur.service import ServiceEncadreur
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_ENCADREUR

routeur = APIRouter(
    prefix=PREFIXE_ENCADREUR, tags=["Espace Encadreur"],
    dependencies=[Depends(exiger_role(RoleEnum.ENCADREUR))],
)


@routeur.get("/tableau-bord", response_model=TableauBordEncadreur, summary="Tableau de bord encadreur")
async def tableau_bord(session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> TableauBordEncadreur:
    return await ServiceEncadreur(session).tableau_bord(utilisateur.id)