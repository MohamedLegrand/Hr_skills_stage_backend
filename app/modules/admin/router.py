"""
Chemin : Hr-skills-stage-backend/app/modules/admin/router.py
Préfixe : /api/v1/admin
"""
from fastapi import APIRouter, Depends
from app.modules.admin.schemas import TableauBordAdmin
from app.modules.admin.service import ServiceAdmin
from app.core.dependencies import SessionDB, exiger_role
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_ADMIN

routeur = APIRouter(
    prefix=PREFIXE_ADMIN, tags=["Administration"],
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)


@routeur.get("/tableau-bord", response_model=TableauBordAdmin, summary="Tableau de bord global")
async def tableau_bord(session: SessionDB) -> TableauBordAdmin:
    return await ServiceAdmin(session).tableau_bord()