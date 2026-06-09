"""
Chemin : Hr-skills-stage-backend/app/modules/document/router.py
Préfixe : /api/v1/documents
"""
from fastapi import APIRouter, Depends, File, UploadFile, status
from app.modules.document.schemas import RequeteRejet, SortieDocument, ListeDocuments
from app.modules.document.service import ServiceDocument
from app.core.dependencies import SessionDB, obtenir_utilisateur_courant, exiger_role
from app.shared.enums import RoleEnum, TypeDocument
from app.shared.constants import PREFIXE_DOCUMENTS

routeur = APIRouter(prefix=PREFIXE_DOCUMENTS, tags=["Documents"])


@routeur.post("/{inscription_id}/{type_code}", response_model=SortieDocument, status_code=status.HTTP_201_CREATED, summary="Déposer un document")
async def deposer(
    inscription_id: str, type_code: TypeDocument,
    session: SessionDB, fichier: UploadFile = File(...),
    utilisateur=Depends(obtenir_utilisateur_courant),
) -> SortieDocument:
    doc = await ServiceDocument(session).deposer(inscription_id, type_code, fichier)
    return SortieDocument.model_validate(doc)


@routeur.get("/{inscription_id}", response_model=ListeDocuments, summary="Documents d'une inscription")
async def lister(inscription_id: str, session: SessionDB) -> ListeDocuments:
    return await ServiceDocument(session).lister_par_inscription(inscription_id)


@routeur.patch("/{document_id}/valider", response_model=SortieDocument, summary="Valider un document",
               dependencies=[Depends(exiger_role(RoleEnum.ADMIN, RoleEnum.ENCADREUR))])
async def valider(document_id: str, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieDocument:
    doc = await ServiceDocument(session).valider(document_id, utilisateur.id)
    return SortieDocument.model_validate(doc)


@routeur.patch("/{document_id}/rejeter", response_model=SortieDocument, summary="Rejeter un document",
               dependencies=[Depends(exiger_role(RoleEnum.ADMIN, RoleEnum.ENCADREUR))])
async def rejeter(document_id: str, donnees: RequeteRejet, session: SessionDB, utilisateur=Depends(obtenir_utilisateur_courant)) -> SortieDocument:
    doc = await ServiceDocument(session).rejeter(document_id, donnees, utilisateur.id)
    return SortieDocument.model_validate(doc)