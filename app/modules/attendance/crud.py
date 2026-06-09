"""
Chemin : Hr-skills-stage-backend/app/modules/attendance/crud.py
"""
from datetime import date
from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.attendance.models import Presence
from app.shared.enums import StatutPresence


class CrudPresence:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, presence_id: str) -> Optional[Presence]:
        r = await self.session.execute(select(Presence).where(Presence.id == presence_id))
        return r.scalar_one_or_none()

    async def obtenir_par_inscription_et_date(self, inscription_id: str, date_presence: date) -> Optional[Presence]:
        r = await self.session.execute(
            select(Presence).where(Presence.inscription_id == inscription_id, Presence.date_presence == date_presence)
        )
        return r.scalar_one_or_none()

    async def lister_par_inscription(self, inscription_id: str) -> list[Presence]:
        r = await self.session.execute(
            select(Presence).where(Presence.inscription_id == inscription_id).order_by(Presence.date_presence.desc())
        )
        return r.scalars().all()

    async def creer(self, donnees: dict) -> Presence:
        p = Presence(**donnees)
        self.session.add(p)
        await self.session.flush()
        await self.session.refresh(p)
        return p

    async def mettre_a_jour(self, presence_id: str, donnees: dict) -> None:
        await self.session.execute(update(Presence).where(Presence.id == presence_id).values(**donnees))
        await self.session.flush()

    async def calculer_resume(self, inscription_id: str) -> dict:
        r = await self.session.execute(
            select(
                func.count().filter(Presence.statut == StatutPresence.PRESENT).label("presents"),
                func.count().filter(Presence.statut == StatutPresence.ABSENT).label("absents"),
                func.count().filter(Presence.statut == StatutPresence.JUSTIFIE).label("justifies"),
                func.count().label("total"),
            ).where(Presence.inscription_id == inscription_id)
        )
        row = r.fetchone()
        taux = round(row.presents * 100 / row.total, 1) if row.total > 0 else 0.0
        return {
            "inscription_id": inscription_id,
            "jours_presents": row.presents, "jours_absents": row.absents,
            "jours_justifies": row.justifies, "total_jours": row.total,
            "taux_presence_pct": taux,
        }