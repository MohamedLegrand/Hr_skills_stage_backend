"""
Chemin : Hr-skills-stage-backend/app/modules/evaluation/crud.py
"""
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.evaluation.models import Evaluation
from app.shared.enums import MoisEvaluation


class CrudEvaluation:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, evaluation_id: str) -> Optional[Evaluation]:
        r = await self.session.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
        return r.scalar_one_or_none()

    async def obtenir_par_inscription_et_mois(self, inscription_id: str, mois: MoisEvaluation) -> Optional[Evaluation]:
        r = await self.session.execute(
            select(Evaluation).where(Evaluation.inscription_id == inscription_id, Evaluation.mois == mois)
        )
        return r.scalar_one_or_none()

    async def lister_par_inscription(self, inscription_id: str) -> list[Evaluation]:
        r = await self.session.execute(
            select(Evaluation).where(Evaluation.inscription_id == inscription_id).order_by(Evaluation.mois)
        )
        return r.scalars().all()

    async def creer(self, donnees: dict) -> Evaluation:
        e = Evaluation(**donnees)
        self.session.add(e)
        await self.session.flush()
        await self.session.refresh(e)
        return e

    async def mettre_a_jour(self, evaluation_id: str, donnees: dict) -> None:
        donnees = {k: v for k, v in donnees.items() if v is not None}
        await self.session.execute(update(Evaluation).where(Evaluation.id == evaluation_id).values(**donnees))
        await self.session.flush()