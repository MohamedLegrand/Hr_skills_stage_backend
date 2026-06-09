"""
Chemin : Hr-skills-stage-backend/app/modules/report/service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.report.crud import CrudRapport
from app.modules.report.schemas import SortieRapport
from app.modules.report.models import Rapport
from app.modules.enrollment.crud import CrudInscription
from app.core.exceptions import NonTrouve
from app.shared.enums import TypeRapport
from app.shared.constants import BUCKET_RAPPORTS


class ServiceRapport:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudRapport(session)

    async def generer_attestation(self, inscription_id: str, generateur_id: str) -> Rapport:
        inscription = await CrudInscription(self.session).obtenir_par_id(inscription_id)
        if not inscription:
            raise NonTrouve("Inscription")

        from app.utils.pdf_generator import generer_attestation_fin
        from app.utils.file_upload import televerser_fichier

        contenu = await generer_attestation_fin(inscription)
        chemin  = f"attestations/{inscription_id}/attestation_fin.pdf"
        url_pdf = await televerser_fichier(contenu, chemin, BUCKET_RAPPORTS)

        return await self.crud.creer({
            "inscription_id": inscription_id,
            "type_rapport":   TypeRapport.ATTESTATION_FIN,
            "url_pdf":        url_pdf,
            "genere_par":     generateur_id,
        })

    async def lister_par_inscription(self, inscription_id: str) -> list[SortieRapport]:
        rapports = await self.crud.lister_par_inscription(inscription_id)
        return [SortieRapport.model_validate(r) for r in rapports]

    async def obtenir_par_id(self, rapport_id: str) -> Rapport:
        r = await self.crud.obtenir_par_id(rapport_id)
        if not r:
            raise NonTrouve("Rapport")
        return r