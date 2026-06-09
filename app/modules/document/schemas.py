"""
Chemin : Hr-skills-stage-backend/app/modules/document/schemas.py
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.shared.enums import StatutDocument, TypeDocument


class SortieDocument(BaseModel):
    id:             str
    inscription_id: str
    type_code:      TypeDocument
    url_fichier:    str
    taille_octets:  Optional[int]
    statut:         StatutDocument
    commentaire:    Optional[str]
    soumis_le:      datetime
    traite_le:      Optional[datetime]
    traite_par:     Optional[str]

    model_config = {"from_attributes": True}


class RequeteRejet(BaseModel):
    commentaire: str


class ListeDocuments(BaseModel):
    total:     int
    documents: list[SortieDocument]