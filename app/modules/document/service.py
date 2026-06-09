"""
Chemin : Hr-skills-stage-backend/app/modules/document/service.py
"""
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.document.crud import CrudDocument
from app.modules.document.schemas import RequeteRejet, SortieDocument, ListeDocuments
from app.modules.document.models import Document
from app.core.exceptions import NonTrouve, DocumentDejaExistant, TypeFichierInvalide, FichierTropGrand, RequeteInvalide
from app.shared.enums import StatutDocument, TypeDocument
from app.shared.constants import TAILLE_MAX_FICHIER_OCTETS, TYPES_MIME_AUTORISES, BUCKET_DOCUMENTS


class ServiceDocument:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudDocument(session)

    async def deposer(self, inscription_id: str, type_code: TypeDocument, fichier: UploadFile) -> Document:
        # Validation type MIME
        if fichier.content_type not in TYPES_MIME_AUTORISES:
            raise TypeFichierInvalide()

        # Lecture et validation taille
        contenu = await fichier.read()
        if len(contenu) > TAILLE_MAX_FICHIER_OCTETS:
            raise FichierTropGrand()

        # Vérifier doublon — remplacer si rejeté, bloquer si en attente/validé
        existant = await self.crud.obtenir_par_inscription_et_type(inscription_id, type_code)
        if existant and existant.statut in [StatutDocument.EN_ATTENTE, StatutDocument.VALIDE]:
            raise DocumentDejaExistant()

        # Upload Supabase Storage
        from app.utils.file_upload import televerser_fichier
        chemin = f"{inscription_id}/{type_code.value}/{fichier.filename}"
        url = await televerser_fichier(contenu, chemin, BUCKET_DOCUMENTS)

        donnees = {
            "inscription_id": inscription_id,
            "type_code": type_code,
            "url_fichier": url,
            "taille_octets": len(contenu),
        }
        if existant:
            await self.crud.mettre_a_jour_url(existant.id, url)
            await self.crud.changer_statut(existant.id, StatutDocument.EN_ATTENTE, "")
            return await self.obtenir_par_id(existant.id)

        return await self.crud.creer(donnees)

    async def obtenir_par_id(self, document_id: str) -> Document:
        doc = await self.crud.obtenir_par_id(document_id)
        if not doc:
            raise NonTrouve("Document")
        return doc

    async def lister_par_inscription(self, inscription_id: str) -> ListeDocuments:
        docs = await self.crud.lister_par_inscription(inscription_id)
        return ListeDocuments(total=len(docs), documents=[SortieDocument.model_validate(d) for d in docs])

    async def valider(self, document_id: str, valideur_id: str) -> Document:
        doc = await self.obtenir_par_id(document_id)
        if doc.statut != StatutDocument.EN_ATTENTE:
            raise RequeteInvalide(detail="Seul un document en attente peut être validé")
        await self.crud.changer_statut(document_id, StatutDocument.VALIDE, valideur_id)
        return await self.obtenir_par_id(document_id)

    async def rejeter(self, document_id: str, donnees: RequeteRejet, rejeteur_id: str) -> Document:
        doc = await self.obtenir_par_id(document_id)
        if doc.statut != StatutDocument.EN_ATTENTE:
            raise RequeteInvalide(detail="Seul un document en attente peut être rejeté")
        await self.crud.changer_statut(document_id, StatutDocument.REJETE, rejeteur_id, donnees.commentaire)
        return await self.obtenir_par_id(document_id)