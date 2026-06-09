"""
Chemin : Hr-skills-stage-backend/app/modules/convention/schemas.py
"""
from datetime import datetime
from pydantic import BaseModel


class RequeteConvention(BaseModel):
    inscription_id: str


class SortieConvention(BaseModel):
    id:             str
    inscription_id: str
    url_pdf:        str
    generee_le:     datetime
    generee_par:    str | None

    model_config = {"from_attributes": True}