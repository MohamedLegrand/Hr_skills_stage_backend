"""
Chemin : Hr-skills-stage-backend/app/modules/payment/service.py
"""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.payment.crud import CrudPaiement
from app.modules.payment.schemas import InitiationPaiement, ChargeWebhook, SortiePaiement, ListePaiements
from app.modules.payment.models import Paiement
from app.core.exceptions import NonTrouve, PaiementDejaConfirme
from app.shared.enums import StatutPaiement


class ServicePaiement:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudPaiement(session)

    async def initier(self, donnees: InitiationPaiement) -> Paiement:
        reference = f"HRS-{uuid.uuid4().hex[:12].upper()}"
        return await self.crud.creer({
            "inscription_id": donnees.inscription_id,
            "montant":        donnees.montant,
            "devise":         donnees.devise,
            "mode_paiement":  donnees.mode_paiement,
            "reference":      reference,
        })

    async def confirmer_webhook(self, donnees: ChargeWebhook) -> Paiement:
        paiement = await self.crud.obtenir_par_reference(donnees.reference)
        if not paiement:
            raise NonTrouve("Paiement")
        if paiement.statut == StatutPaiement.CONFIRME:
            raise PaiementDejaConfirme()

        # Générer le reçu PDF
        from app.utils.pdf_generator import generer_recu_paiement
        url_recu = await generer_recu_paiement(paiement)

        await self.crud.confirmer(paiement.id, url_recu)
        return await self.crud.obtenir_par_id(paiement.id)

    async def obtenir_par_id(self, paiement_id: str) -> Paiement:
        p = await self.crud.obtenir_par_id(paiement_id)
        if not p:
            raise NonTrouve("Paiement")
        return p

    async def historique_inscription(self, inscription_id: str) -> ListePaiements:
        paiements = await self.crud.lister_par_inscription(inscription_id)
        return ListePaiements(total=len(paiements), paiements=[SortiePaiement.model_validate(p) for p in paiements])

    async def lister_tous(self, page=1, taille=20, statut=None) -> ListePaiements:
        paiements, total = await self.crud.lister_tous(page, taille, statut)
        return ListePaiements(total=total, paiements=[SortiePaiement.model_validate(p) for p in paiements])