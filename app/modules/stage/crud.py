"""
Chemin : Hr-skills-stage-backend/app/modules/stage/crud.py
"""
from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.stage.models import OffreStage
from app.shared.enums import StatutOffre


class CrudOffre:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, offre_id: str) -> Optional[OffreStage]:
        r = await self.session.execute(select(OffreStage).where(OffreStage.id == offre_id))
        return r.scalar_one_or_none()

    async def lister(self, page=1, taille=20, statut=None, domaine=None):
        q = select(OffreStage)
        qt = select(func.count()).select_from(OffreStage)
        if statut:
            q = q.where(OffreStage.statut == statut)
            qt = qt.where(OffreStage.statut == statut)
        if domaine:
            q = q.where(OffreStage.domaine.ilike(f"%{domaine}%"))
            qt = qt.where(OffreStage.domaine.ilike(f"%{domaine}%"))
        total = (await self.session.execute(qt)).scalar()
        q = q.order_by(OffreStage.cree_le.desc()).offset((page-1)*taille).limit(taille)
        r = await self.session.execute(q)
        return r.scalars().all(), total

    async def creer(self, donnees: dict) -> OffreStage:
        offre = OffreStage(**donnees)
        self.session.add(offre)
        await self.session.flush()
        await self.session.refresh(offre)
        return offre

    async def mettre_a_jour(self, offre_id: str, donnees: dict) -> Optional[OffreStage]:
        donnees = {k: v for k, v in donnees.items() if v is not None}
        await self.session.execute(update(OffreStage).where(OffreStage.id == offre_id).values(**donnees))
        await self.session.flush()
        return await self.obtenir_par_id(offre_id)

    async def archiver(self, offre_id: str) -> None:
        await self.session.execute(
            update(OffreStage).where(OffreStage.id == offre_id).values(statut=StatutOffre.ARCHIVE)
        )
        await self.session.flush()

    async def decrementer_places(self, offre_id: str) -> None:
        offre = await self.obtenir_par_id(offre_id)
        if offre and offre.places_dispo > 0:
            await self.session.execute(
                update(OffreStage).where(OffreStage.id == offre_id)
                .values(places_dispo=OffreStage.places_dispo - 1)
            )
            if offre.places_dispo - 1 == 0:
                await self.session.execute(
                    update(OffreStage).where(OffreStage.id == offre_id).values(statut=StatutOffre.COMPLET)
                )
        await self.session.flush()