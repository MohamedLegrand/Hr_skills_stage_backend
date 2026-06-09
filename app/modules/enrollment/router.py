"""
Chemin : Hr-skills-stage-backend/app/modules/enrollment/router.py
Préfixe : /api/v1/inscriptions
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.modules.enrollment.schemas import CreationInscription, RequeteValidation, RequeteRefus, SortieInscription, ListeInscriptions
from app.modules.enrollment.service import ServiceInscription
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum, StatutInscription
from app.shared.constants import PREFIXE_INSCRIPTIONS

routeur = APIRouter(prefix=PREFIXE_INSCRIPTIONS, tags=["Inscriptions"])


@routeur.post("/", response_model=SortieInscription, status_code=status.HTTP_201_CREATED, summary="S'inscrire à un stage")
async def inscrire(donnees: CreationInscription, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieInscription:
    i = await ServiceInscription(session).inscrire(donnees, utilisateur.id)
    return SortieInscription.model_validate(i)


@routeur.get("/", response_model=ListeInscriptions, summary="Lister les inscriptions", dependencies=[Depends(exiger_role(RoleEnum.ADMIN))])
async def lister(session: SessionDB, page: int = Query(1, ge=1), taille: int = Query(20, ge=1, le=100), statut: Optional[StatutInscription] = None) -> ListeInscriptions:
    return await ServiceInscription(session).lister(page=page, taille=taille, statut=statut)


@routeur.get("/mes-inscriptions", response_model=ListeInscriptions, summary="Mes inscriptions")
async def mes_inscriptions(session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> ListeInscriptions:
    return await ServiceInscription(session).lister(stagiaire_id=utilisateur.id)


@routeur.get("/{inscription_id}", response_model=SortieInscription, summary="Détail d'une inscription")
async def detail(inscription_id: str, session: SessionDB) -> SortieInscription:
    i = await ServiceInscription(session).obtenir_par_id(inscription_id)
    return SortieInscription.model_validate(i)


@routeur.put("/{inscription_id}/valider", response_model=SortieInscription, summary="Valider une inscription", dependencies=[Depends(exiger_role(RoleEnum.ADMIN))])
async def valider(inscription_id: str, donnees: RequeteValidation, session: SessionDB) -> SortieInscription:
    i = await ServiceInscription(session).valider(inscription_id, donnees)
    return SortieInscription.model_validate(i)


@routeur.put("/{inscription_id}/refuser", status_code=status.HTTP_204_NO_CONTENT, summary="Refuser une inscription", dependencies=[Depends(exiger_role(RoleEnum.ADMIN))])
async def refuser(inscription_id: str, donnees: RequeteRefus, session: SessionDB) -> None:
    await ServiceInscription(session).refuser(inscription_id, donnees)


@routeur.patch("/{inscription_id}/terminer", status_code=status.HTTP_204_NO_CONTENT, summary="Terminer un stage", dependencies=[Depends(exiger_role(RoleEnum.ADMIN))])
async def terminer(inscription_id: str, session: SessionDB) -> None:
    await ServiceInscription(session).terminer(inscription_id)