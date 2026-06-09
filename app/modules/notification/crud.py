"""
Chemin : Hr-skills-stage-backend/app/modules/notification/crud.py
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.notification.models import Notification


class CrudNotification:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, notif_id: str) -> Optional[Notification]:
        r = await self.session.execute(select(Notification).where(Notification.id == notif_id))
        return r.scalar_one_or_none()

    async def lister_par_utilisateur(self, utilisateur_id: str, non_lues_seulement=False) -> list[Notification]:
        q = select(Notification).where(Notification.utilisateur_id == utilisateur_id)
        if non_lues_seulement:
            q = q.where(Notification.lu == False)
        q = q.order_by(Notification.cree_le.desc())
        r = await self.session.execute(q)
        return r.scalars().all()

    async def compter_non_lues(self, utilisateur_id: str) -> int:
        r = await self.session.execute(
            select(func.count()).where(Notification.utilisateur_id == utilisateur_id, Notification.lu == False)
        )
        return r.scalar()

    async def creer(self, donnees: dict) -> Notification:
        n = Notification(**donnees)
        self.session.add(n)
        await self.session.flush()
        await self.session.refresh(n)
        return n

    async def marquer_lu(self, notif_id: str) -> None:
        await self.session.execute(
            update(Notification).where(Notification.id == notif_id)
            .values(lu=True, lu_le=datetime.now(timezone.utc))
        )
        await self.session.flush()

    async def tout_marquer_lu(self, utilisateur_id: str) -> None:
        await self.session.execute(
            update(Notification).where(Notification.utilisateur_id == utilisateur_id, Notification.lu == False)
            .values(lu=True, lu_le=datetime.now(timezone.utc))
        )
        await self.session.flush()