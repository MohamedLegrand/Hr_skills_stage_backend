"""
Chemin : Hr-skills-stage-backend/app/modules/payment/router.py
Préfixe : /api/v1/paiements
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.modules.payment.schemas import InitiationPaiement, ChargeWebhook, SortiePaiement, ListePaiements
from app.modules.payment.service import ServicePaiement
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum, StatutPaiement
from app.shared.constants import PREFIXE_PAIEMENTS

routeur = APIRouter(prefix=PREFIXE_PAIEMENTS, tags=["Paiements"])


@routeur.post("/initier", response_model=SortiePaiement, status_code=status.HTTP_201_CREATED, summary="Initier un paiement")
async def initier(donnees: InitiationPaiement, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortiePaiement:
    p = await ServicePaiement(session).initier(donnees)
    return SortiePaiement.model_validate(p)


@routeur.post("/webhook", response_model=SortiePaiement, summary="Webhook passerelle paiement")
async def webhook(donnees: ChargeWebhook, session: SessionDB) -> SortiePaiement:
    p = await ServicePaiement(session).confirmer_webhook(donnees)
    return SortiePaiement.model_validate(p)


@routeur.get("/{paiement_id}", response_model=SortiePaiement, summary="Détail d'un paiement")
async def detail(paiement_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortiePaiement:
    p = await ServicePaiement(session).obtenir_par_id(paiement_id)
    return SortiePaiement.model_validate(p)


@routeur.get("/inscription/{inscription_id}", response_model=ListePaiements, summary="Historique paiements")
async def historique(inscription_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> ListePaiements:
    return await ServicePaiement(session).historique_inscription(inscription_id)


@routeur.get("/", response_model=ListePaiements, summary="Tous les paiements", dependencies=[Depends(exiger_role(RoleEnum.ADMIN))])
async def lister_tous(session: SessionDB, page: int = Query(1, ge=1), taille: int = Query(20, ge=1, le=100), statut: Optional[StatutPaiement] = None) -> ListePaiements:
    return await ServicePaiement(session).lister_tous(page, taille, statut)