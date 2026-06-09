"""
Chemin : Hr-skills-stage-backend/app/modules/evaluation/router.py
Préfixe : /api/v1/evaluations
"""
from fastapi import APIRouter, Depends, status
from app.modules.evaluation.schemas import CreationEvaluation, MiseAJourEvaluation, SortieEvaluation
from app.modules.evaluation.service import ServiceEvaluation
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_EVALUATIONS

routeur = APIRouter(prefix=PREFIXE_EVALUATIONS, tags=["Évaluations"])


@routeur.post("/", response_model=SortieEvaluation, status_code=status.HTTP_201_CREATED, summary="Créer une évaluation",
              dependencies=[Depends(exiger_role(RoleEnum.ENCADREUR))])
async def creer(donnees: CreationEvaluation, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieEvaluation:
    e = await ServiceEvaluation(session).creer(donnees, utilisateur.id)
    return SortieEvaluation.model_validate(e)


@routeur.get("/{inscription_id}", response_model=list[SortieEvaluation], summary="Évaluations d'une inscription")
async def lister(inscription_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> list[SortieEvaluation]:
    return await ServiceEvaluation(session).lister_par_inscription(inscription_id)


@routeur.get("/detail/{evaluation_id}", response_model=SortieEvaluation, summary="Détail d'une évaluation")
async def detail(evaluation_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieEvaluation:
    e = await ServiceEvaluation(session).obtenir_par_id(evaluation_id)
    return SortieEvaluation.model_validate(e)


@routeur.put("/{evaluation_id}", response_model=SortieEvaluation, summary="Modifier une évaluation",
             dependencies=[Depends(exiger_role(RoleEnum.ENCADREUR))])
async def modifier(evaluation_id: str, donnees: MiseAJourEvaluation, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieEvaluation:
    e = await ServiceEvaluation(session).mettre_a_jour(evaluation_id, donnees, utilisateur.id)
    return SortieEvaluation.model_validate(e)