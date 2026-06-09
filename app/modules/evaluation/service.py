"""
Chemin : Hr-skills-stage-backend/app/modules/evaluation/service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.evaluation.crud import CrudEvaluation
from app.modules.evaluation.schemas import CreationEvaluation, MiseAJourEvaluation, SortieEvaluation
from app.modules.evaluation.models import Evaluation
from app.core.exceptions import NonTrouve, Conflit, AccesInterdit


class ServiceEvaluation:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudEvaluation(session)

    async def creer(self, donnees: CreationEvaluation, encadreur_id: str) -> Evaluation:
        existante = await self.crud.obtenir_par_inscription_et_mois(donnees.inscription_id, donnees.mois)
        if existante:
            raise Conflit(detail=f"Une évaluation existe déjà pour le mois {donnees.mois}")
        return await self.crud.creer({
            "inscription_id": donnees.inscription_id, "encadreur_id": encadreur_id,
            "mois": donnees.mois, "note_globale": donnees.note_globale,
            "note_technique": donnees.note_technique, "note_comportement": donnees.note_comportement,
            "note_ponctualite": donnees.note_ponctualite, "commentaire": donnees.commentaire,
            "recommande": donnees.recommande,
        })

    async def obtenir_par_id(self, evaluation_id: str) -> Evaluation:
        e = await self.crud.obtenir_par_id(evaluation_id)
        if not e:
            raise NonTrouve("Évaluation")
        return e

    async def lister_par_inscription(self, inscription_id: str) -> list[SortieEvaluation]:
        evals = await self.crud.lister_par_inscription(inscription_id)
        return [SortieEvaluation.model_validate(e) for e in evals]

    async def mettre_a_jour(self, evaluation_id: str, donnees: MiseAJourEvaluation, encadreur_id: str) -> Evaluation:
        e = await self.obtenir_par_id(evaluation_id)
        if e.encadreur_id != encadreur_id:
            raise AccesInterdit(detail="Vous ne pouvez modifier que vos propres évaluations")
        await self.crud.mettre_a_jour(evaluation_id, donnees.model_dump(exclude_none=True))
        return await self.obtenir_par_id(evaluation_id)