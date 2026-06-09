"""
Chemin : Hr-skills-stage-backend/app/modules/payment/crud.py
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.payment.models import Paiement
from app.shared.enums import StatutPaiement


class CrudPaiement:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, paiement_id: str) -> Optional[Paiement]:
        r = await self.session.execute(select(Paiement).where(Paiement.id == paiement_id))
        return r.scalar_one_or_none()

    async def obtenir_par_reference(self, reference: str) -> Optional[Paiement]:
        r = await self.session.execute(select(Paiement).where(Paiement.reference == reference))
        return r.scalar_one_or_none()

    async def lister_par_inscription(self, inscription_id: str) -> list[Paiement]:
        r = await self.session.execute(
            select(Paiement).where(Paiement.inscription_id == inscription_id).order_by(Paiement.initie_le.desc())
        )
        return r.scalars().all()

    async def lister_tous(self, page=1, taille=20, statut=None):
        q  = select(Paiement)
        qt = select(func.count()).select_from(Paiement)
        if statut:
            q = q.where(Paiement.statut == statut)
            qt = qt.where(Paiement.statut == statut)
        total = (await self.session.execute(qt)).scalar()
        q = q.order_by(Paiement.initie_le.desc()).offset((page-1)*taille).limit(taille)
        r = await self.session.execute(q)
        return r.scalars().all(), total

    async def creer(self, donnees: dict) -> Paiement:
        p = Paiement(**donnees)
        self.session.add(p)
        await self.session.flush()
        await self.session.refresh(p)
        return p

    async def confirmer(self, paiement_id: str, url_recu: str = None) -> None:
        valeurs = {"statut": StatutPaiement.CONFIRME, "confirme_le": datetime.now(timezone.utc)}
        if url_recu:
            valeurs["url_recu"] = url_recu
        await self.session.execute(update(Paiement).where(Paiement.id == paiement_id).values(**valeurs))
        await self.session.flush()

    async def marquer_echoue(self, paiement_id: str) -> None:
        await self.session.execute(
            update(Paiement).where(Paiement.id == paiement_id).values(statut=StatutPaiement.ECHOUE)
        )
        await self.session.flush()