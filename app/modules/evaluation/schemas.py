"""
Chemin : Hr-skills-stage-backend/app/modules/evaluation/schemas.py
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.shared.enums import MoisEvaluation


class CreationEvaluation(BaseModel):
    inscription_id:    str
    mois:              MoisEvaluation
    note_globale:      float = Field(..., ge=0, le=20)
    note_technique:    Optional[float] = Field(None, ge=0, le=20)
    note_comportement: Optional[float] = Field(None, ge=0, le=20)
    note_ponctualite:  Optional[float] = Field(None, ge=0, le=20)
    commentaire:       Optional[str]   = None
    recommande:        Optional[bool]  = None


class MiseAJourEvaluation(BaseModel):
    note_globale:      Optional[float] = Field(None, ge=0, le=20)
    note_technique:    Optional[float] = Field(None, ge=0, le=20)
    note_comportement: Optional[float] = Field(None, ge=0, le=20)
    note_ponctualite:  Optional[float] = Field(None, ge=0, le=20)
    commentaire:       Optional[str]   = None
    recommande:        Optional[bool]  = None


class SortieEvaluation(BaseModel):
    id:                str
    inscription_id:    str
    encadreur_id:      str
    mois:              MoisEvaluation
    note_globale:      float
    note_technique:    Optional[float]
    note_comportement: Optional[float]
    note_ponctualite:  Optional[float]
    commentaire:       Optional[str]
    recommande:        Optional[bool]
    evalue_le:         datetime

    model_config = {"from_attributes": True}