"""
Chemin : Hr-skills-stage-backend/app/modules/student/service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.student.schemas import TableauBordStagiaire
from app.modules.enrollment.crud import CrudInscription
from app.modules.document.crud import CrudDocument
from app.modules.payment.crud import CrudPaiement
from app.modules.enrollment.schemas import SortieInscription
from app.modules.document.schemas import SortieDocument
from app.modules.payment.schemas import SortiePaiement
from app.shared.enums import StatutDocument


class ServiceStagiaire:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def tableau_bord(self, stagiaire_id: str) -> TableauBordStagiaire:
        # Inscription active
        inscriptions, _ = await CrudInscription(self.session).lister(stagiaire_id=stagiaire_id)
        inscription = inscriptions[0] if inscriptions else None

        documents, paiements = [], []
        docs_valides = docs_total = 0

        if inscription:
            docs = await CrudDocument(self.session).lister_par_inscription(inscription.id)
            paiements_bruts = await CrudPaiement(self.session).lister_par_inscription(inscription.id)
            documents  = [SortieDocument.model_validate(d) for d in docs]
            paiements  = [SortiePaiement.model_validate(p) for p in paiements_bruts]
            docs_total   = len(docs)
            docs_valides = sum(1 for d in docs if d.statut == StatutDocument.VALIDE)

        progression = round(docs_valides * 100 / docs_total, 1) if docs_total > 0 else 0.0

        return TableauBordStagiaire(
            inscription=SortieInscription.model_validate(inscription) if inscription else None,
            documents=documents, paiements=paiements,
            progression_pct=progression,
            documents_valides=docs_valides, documents_total=docs_total,
        )