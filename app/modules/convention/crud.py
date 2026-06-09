"""
Chemin : Hr-skills-stage-backend/app/modules/convention/crud.py
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.convention.models import Convention


class CrudConvention:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, convention_id: str) -> Optional[Convention]:
        r = await self.session.execute(select(Convention).where(Convention.id == convention_id))
        return r.scalar_one_or_none()

    async def obtenir_par_inscription(self, inscription_id: str) -> Optional[Convention]:
        r = await self.session.execute(select(Convention).where(Convention.inscription_id == inscription_id))
        return r.scalar_one_or_none()

    async def creer(self, donnees: dict) -> Convention:
        c = Convention(**donnees)
        self.session.add(c)
        await self.session.flush()
        await self.session.refresh(c)
        return c