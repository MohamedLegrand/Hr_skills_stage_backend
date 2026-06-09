"""
Chemin : Hr-skills-stage-backend/app/modules/enrollment/schemas.py
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.shared.enums import StatutInscription
from app.modules.user.schemas import SortieUtilisateurSimple
from app.modules.stage.schemas import SortieOffre


class CreationInscription(BaseModel):
    offre_id: str


class RequeteValidation(BaseModel):
    encadreur_id: str


class RequeteRefus(BaseModel):
    motif_refus: str


class SortieInscription(BaseModel):
    id:              str
    stagiaire_id:    str
    offre_id:        str
    encadreur_id:    Optional[str]
    statut:          StatutInscription
    motif_refus:     Optional[str]
    date_soumission: datetime
    date_validation: Optional[datetime]
    mis_a_jour_le:   datetime
    stagiaire:       Optional[SortieUtilisateurSimple] = None
    offre:           Optional[SortieOffre]             = None

    model_config = {"from_attributes": True}


class ListeInscriptions(BaseModel):
    total:        int
    page:         int
    taille_page:  int
    inscriptions: list[SortieInscription]