"""
Chemin : Hr-skills-stage-backend/app/modules/report/schemas.py
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.shared.enums import TypeRapport


class RequeteRapport(BaseModel):
    inscription_id: str
    type_rapport:   TypeRapport


class SortieRapport(BaseModel):
    id:             str
    inscription_id: str
    type_rapport:   TypeRapport
    url_pdf:        Optional[str]
    genere_le:      datetime
    genere_par:     Optional[str]

    model_config = {"from_attributes": True}