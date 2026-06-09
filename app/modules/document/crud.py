"""
Chemin : Hr-skills-stage-backend/app/modules/document/crud.py
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.document.models import Document
from app.shared.enums import StatutDocument, TypeDocument


class CrudDocument:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obtenir_par_id(self, document_id: str) -> Optional[Document]:
        r = await self.session.execute(select(Document).where(Document.id == document_id))
        return r.scalar_one_or_none()

    async def obtenir_par_inscription_et_type(self, inscription_id: str, type_code: TypeDocument) -> Optional[Document]:
        r = await self.session.execute(
            select(Document).where(Document.inscription_id == inscription_id, Document.type_code == type_code)
        )
        return r.scalar_one_or_none()

    async def lister_par_inscription(self, inscription_id: str) -> list[Document]:
        r = await self.session.execute(
            select(Document).where(Document.inscription_id == inscription_id).order_by(Document.soumis_le.desc())
        )
        return r.scalars().all()

    async def lister_en_attente(self) -> list[Document]:
        r = await self.session.execute(
            select(Document).where(Document.statut == StatutDocument.EN_ATTENTE).order_by(Document.soumis_le)
        )
        return r.scalars().all()

    async def creer(self, donnees: dict) -> Document:
        doc = Document(**donnees)
        self.session.add(doc)
        await self.session.flush()
        await self.session.refresh(doc)
        return doc

    async def changer_statut(self, document_id: str, statut: StatutDocument, traite_par: str, commentaire: str = None) -> None:
        valeurs = {"statut": statut, "traite_par": traite_par, "traite_le": datetime.now(timezone.utc)}
        if commentaire:
            valeurs["commentaire"] = commentaire
        await self.session.execute(update(Document).where(Document.id == document_id).values(**valeurs))
        await self.session.flush()

    async def mettre_a_jour_url(self, document_id: str, url: str) -> None:
        await self.session.execute(update(Document).where(Document.id == document_id).values(url_fichier=url))
        await self.session.flush()