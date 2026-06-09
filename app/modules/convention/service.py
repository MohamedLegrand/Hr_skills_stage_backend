"""
Chemin : Hr-skills-stage-backend/app/modules/convention/service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.convention.crud import CrudConvention
from app.modules.convention.schemas import SortieConvention
from app.modules.convention.models import Convention
from app.modules.enrollment.crud import CrudInscription
from app.core.exceptions import NonTrouve, Conflit
from app.shared.constants import BUCKET_CONVENTIONS


class ServiceConvention:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudConvention(session)

    async def generer(self, inscription_id: str, generee_par: str) -> Convention:
        existante = await self.crud.obtenir_par_inscription(inscription_id)
        if existante:
            raise Conflit(detail="Une convention existe déjà pour cette inscription")

        inscription = await CrudInscription(self.session).obtenir_par_id(inscription_id)
        if not inscription:
            raise NonTrouve("Inscription")

        from app.utils.pdf_generator import generer_convention_pdf
        from app.utils.file_upload import televerser_fichier

        contenu_pdf = await generer_convention_pdf(inscription)
        chemin = f"conventions/{inscription_id}/convention_stage.pdf"
        url_pdf = await televerser_fichier(contenu_pdf, chemin, BUCKET_CONVENTIONS)

        return await self.crud.creer({
            "inscription_id": inscription_id,
            "url_pdf": url_pdf,
            "generee_par": generee_par,
        })

    async def obtenir_par_inscription(self, inscription_id: str) -> Convention:
        c = await self.crud.obtenir_par_inscription(inscription_id)
        if not c:
            raise NonTrouve("Convention")
        return c