"""
Chemin : Hr-skills-stage-backend/app/modules/attendance/service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.attendance.crud import CrudPresence
from app.modules.attendance.schemas import MarquagePresence, SortiePresence, ResumePresences
from app.modules.attendance.models import Presence
from app.core.exceptions import NonTrouve, RequeteInvalide


class ServicePresence:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudPresence(session)

    async def marquer(self, donnees: MarquagePresence, encadreur_id: str) -> Presence:
        existante = await self.crud.obtenir_par_inscription_et_date(donnees.inscription_id, donnees.date_presence)
        if existante:
            await self.crud.mettre_a_jour(existante.id, {
                "statut": donnees.statut, "commentaire": donnees.commentaire,
                "enregistre_par": encadreur_id,
            })
            return await self.crud.obtenir_par_id(existante.id)
        return await self.crud.creer({
            "inscription_id": donnees.inscription_id, "date_presence": donnees.date_presence,
            "statut": donnees.statut, "commentaire": donnees.commentaire, "enregistre_par": encadreur_id,
        })

    async def lister_par_inscription(self, inscription_id: str) -> list[SortiePresence]:
        presences = await self.crud.lister_par_inscription(inscription_id)
        return [SortiePresence.model_validate(p) for p in presences]

    async def resume(self, inscription_id: str) -> ResumePresences:
        return ResumePresences(**await self.crud.calculer_resume(inscription_id))