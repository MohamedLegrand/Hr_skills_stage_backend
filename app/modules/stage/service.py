"""
Chemin : Hr-skills-stage-backend/app/modules/stage/service.py
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.stage.crud import CrudOffre
from app.modules.stage.schemas import CreationOffre, MiseAJourOffre, ListeOffres, SortieOffre
from app.modules.stage.models import OffreStage
from app.core.exceptions import NonTrouve, StageComplet
from app.shared.enums import StatutOffre


class ServiceOffre:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudOffre(session)

    async def creer(self, donnees: CreationOffre, createur_id: str) -> OffreStage:
        return await self.crud.creer({
            "titre": donnees.titre, "domaine": donnees.domaine,
            "description": donnees.description, "date_debut": donnees.date_debut,
            "date_fin": donnees.date_fin, "places_dispo": donnees.places_dispo,
            "cree_par": createur_id,
        })

    async def obtenir_par_id(self, offre_id: str) -> OffreStage:
        offre = await self.crud.obtenir_par_id(offre_id)
        if not offre:
            raise NonTrouve("Offre de stage")
        return offre

    async def lister(self, page=1, taille=20, statut=None, domaine=None) -> ListeOffres:
        offres, total = await self.crud.lister(page, taille, statut, domaine)
        return ListeOffres(
            total=total, page=page, taille_page=taille,
            offres=[SortieOffre.model_validate(o) for o in offres],
        )

    async def mettre_a_jour(self, offre_id: str, donnees: MiseAJourOffre) -> OffreStage:
        await self.obtenir_par_id(offre_id)
        return await self.crud.mettre_a_jour(offre_id, donnees.model_dump(exclude_none=True))

    async def archiver(self, offre_id: str) -> None:
        await self.obtenir_par_id(offre_id)
        await self.crud.archiver(offre_id)

    async def verifier_disponibilite(self, offre_id: str) -> OffreStage:
        offre = await self.obtenir_par_id(offre_id)
        if offre.statut != StatutOffre.OUVERT or offre.places_dispo <= 0:
            raise StageComplet()
        return offre