"""
Chemin : Hr-skills-stage-backend/app/modules/enrollment/service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.enrollment.crud import CrudInscription
from app.modules.enrollment.schemas import CreationInscription, RequeteValidation, RequeteRefus, ListeInscriptions, SortieInscription
from app.modules.enrollment.models import Inscription
from app.modules.stage.service import ServiceOffre
from app.modules.stage.crud import CrudOffre
from app.core.exceptions import NonTrouve, DejaInscrit, RequeteInvalide
from app.shared.enums import StatutInscription


class ServiceInscription:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudInscription(session)

    async def inscrire(self, donnees: CreationInscription, stagiaire_id: str) -> Inscription:
        service_offre = ServiceOffre(self.session)
        await service_offre.verifier_disponibilite(donnees.offre_id)

        existante = await self.crud.obtenir_par_stagiaire_et_offre(stagiaire_id, donnees.offre_id)
        if existante:
            raise DejaInscrit()

        inscription = await self.crud.creer({"stagiaire_id": stagiaire_id, "offre_id": donnees.offre_id})
        await CrudOffre(self.session).decrementer_places(donnees.offre_id)
        return inscription

    async def obtenir_par_id(self, inscription_id: str) -> Inscription:
        i = await self.crud.obtenir_par_id(inscription_id)
        if not i:
            raise NonTrouve("Inscription")
        return i

    async def lister(self, page=1, taille=20, **filtres) -> ListeInscriptions:
        inscriptions, total = await self.crud.lister(page, taille, **filtres)
        return ListeInscriptions(
            total=total, page=page, taille_page=taille,
            inscriptions=[SortieInscription.model_validate(i) for i in inscriptions],
        )

    async def valider(self, inscription_id: str, donnees: RequeteValidation) -> Inscription:
        i = await self.obtenir_par_id(inscription_id)
        if i.statut != StatutInscription.EN_ATTENTE:
            raise RequeteInvalide(detail="Seule une inscription en attente peut être validée")
        await self.crud.mettre_a_jour_statut(inscription_id, StatutInscription.VALIDEE)
        await self.crud.assigner_encadreur(inscription_id, donnees.encadreur_id)
        return await self.obtenir_par_id(inscription_id)

    async def refuser(self, inscription_id: str, donnees: RequeteRefus) -> None:
        i = await self.obtenir_par_id(inscription_id)
        if i.statut != StatutInscription.EN_ATTENTE:
            raise RequeteInvalide(detail="Seule une inscription en attente peut être refusée")
        await self.crud.mettre_a_jour_statut(
            inscription_id, StatutInscription.REFUSEE,
            {"motif_refus": donnees.motif_refus},
        )

    async def terminer(self, inscription_id: str) -> None:
        await self.obtenir_par_id(inscription_id)
        await self.crud.mettre_a_jour_statut(inscription_id, StatutInscription.TERMINEE)