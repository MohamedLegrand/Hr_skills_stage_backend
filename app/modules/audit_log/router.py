"""
Chemin : Hr-skills-stage-backend/app/modules/audit_log/router.py
Préfixe : /api/v1/audit
"""
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.modules.audit_log.schemas import (
    SortieJournalAudit,
    ListeJournalAudit,
    FiltresJournalAudit,
)
from app.modules.audit_log.service import ServiceJournalAudit
from app.core.dependencies import SessionDB, exiger_role
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_AUDIT

routeur = APIRouter(
    prefix=PREFIXE_AUDIT,
    tags=["Journal d'audit"],
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)


@routeur.get("/", response_model=ListeJournalAudit, summary="Journal d'audit complet")
async def lister_journal(
    session:           SessionDB,
    page:              int            = Query(1, ge=1),
    taille:            int            = Query(50, ge=1, le=200),
    utilisateur_id:    Optional[str]  = Query(None),
    action:            Optional[str]  = Query(None),
    table_cible:       Optional[str]  = Query(None),
    enregistrement_id: Optional[str]  = Query(None),
    date_debut:        Optional[datetime] = Query(None),
    date_fin:          Optional[datetime] = Query(None),
) -> ListeJournalAudit:
    filtres = FiltresJournalAudit(
        utilisateur_id=utilisateur_id, action=action,
        table_cible=table_cible, enregistrement_id=enregistrement_id,
        date_debut=date_debut, date_fin=date_fin,
    )
    return await ServiceJournalAudit(session).lister(page=page, taille=taille, filtres=filtres)


@routeur.get("/{journal_id}", response_model=SortieJournalAudit, summary="Détail d'une entrée")
async def detail_journal(journal_id: str, session: SessionDB) -> SortieJournalAudit:
    j = await ServiceJournalAudit(session).obtenir_par_id(journal_id)
    return SortieJournalAudit.model_validate(j)


@routeur.get("/utilisateur/{utilisateur_id}", response_model=list[SortieJournalAudit], summary="Historique d'un utilisateur")
async def historique_utilisateur(
    utilisateur_id: str, session: SessionDB,
    limite: int = Query(20, ge=1, le=100),
) -> list[SortieJournalAudit]:
    return await ServiceJournalAudit(session).historique_utilisateur(utilisateur_id, limite)


@routeur.get("/enregistrement/{table_cible}/{enregistrement_id}", response_model=list[SortieJournalAudit], summary="Historique d'un enregistrement")
async def historique_enregistrement(
    table_cible: str, enregistrement_id: str, session: SessionDB,
) -> list[SortieJournalAudit]:
    return await ServiceJournalAudit(session).historique_enregistrement(table_cible, enregistrement_id)


@routeur.get("/stats/actions", summary="Statistiques des actions")
async def statistiques_actions(session: SessionDB) -> list[dict]:
    return await ServiceJournalAudit(session).statistiques_actions()