"""
Chemin : Hr-skills-stage-backend/app/modules/enrollment/crud.py
"""
from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.enrollment.models import Inscription
from app.shared.enums import StatutInscription


class CrudInscription:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, inscription_id: str) -> Optional[Inscription]:
        r = await self.session.execute(select(Inscription).where(Inscription.id == inscription_id))
        return r.scalar_one_or_none()

    async def obtenir_par_stagiaire_et_offre(self, stagiaire_id: str, offre_id: str) -> Optional[Inscription]:
        r = await self.session.execute(
            select(Inscription).where(
                Inscription.stagiaire_id == stagiaire_id,
                Inscription.offre_id == offre_id,
            )
        )
        return r.scalar_one_or_none()

    async def lister(self, page=1, taille=20, statut=None, offre_id=None, stagiaire_id=None, encadreur_id=None):
        q  = select(Inscription)
        qt = select(func.count()).select_from(Inscription)
        filtres = []
        if statut:       filtres.append(Inscription.statut == statut)
        if offre_id:     filtres.append(Inscription.offre_id == offre_id)
        if stagiaire_id: filtres.append(Inscription.stagiaire_id == stagiaire_id)
        if encadreur_id: filtres.append(Inscription.encadreur_id == encadreur_id)
        if filtres:
            q = q.where(*filtres); qt = qt.where(*filtres)
        total = (await self.session.execute(qt)).scalar()
        q = q.order_by(Inscription.date_soumission.desc()).offset((page-1)*taille).limit(taille)
        r = await self.session.execute(q)
        return r.scalars().all(), total

    async def creer(self, donnees: dict) -> Inscription:
        inscription = Inscription(**donnees)
        self.session.add(inscription)
        await self.session.flush()
        await self.session.refresh(inscription)
        return inscription

    async def mettre_a_jour_statut(self, inscription_id: str, statut: StatutInscription, extra: dict = {}) -> None:
        from datetime import datetime, timezone
        valeurs = {"statut": statut, **extra}
        if statut == StatutInscription.VALIDEE:
            valeurs["date_validation"] = datetime.now(timezone.utc)
        await self.session.execute(update(Inscription).where(Inscription.id == inscription_id).values(**valeurs))
        await self.session.flush()

    async def assigner_encadreur(self, inscription_id: str, encadreur_id: str) -> None:
        await self.session.execute(
            update(Inscription).where(Inscription.id == inscription_id)
            .values(encadreur_id=encadreur_id, statut=StatutInscription.EN_COURS)
        )
        await self.session.flush()