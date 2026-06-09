"""
Chemin : Hr-skills-stage-backend/app/modules/report/crud.py
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.report.models import Rapport
from app.shared.enums import TypeRapport


class CrudRapport:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, rapport_id: str) -> Optional[Rapport]:
        r = await self.session.execute(select(Rapport).where(Rapport.id == rapport_id))
        return r.scalar_one_or_none()

    async def lister_par_inscription(self, inscription_id: str) -> list[Rapport]:
        r = await self.session.execute(
            select(Rapport).where(Rapport.inscription_id == inscription_id).order_by(Rapport.genere_le.desc())
        )
        return r.scalars().all()

    async def creer(self, donnees: dict) -> Rapport:
        rp = Rapport(**donnees)
        self.session.add(rp)
        await self.session.flush()
        await self.session.refresh(rp)
        return rp