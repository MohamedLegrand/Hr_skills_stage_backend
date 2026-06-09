"""
Chemin : Hr-skills-stage-backend/app/modules/stage/schemas.py
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.shared.enums import StatutOffre


class CreationOffre(BaseModel):
    titre:       str        = Field(..., min_length=5, max_length=200)
    domaine:     str        = Field(..., min_length=2, max_length=100)
    description: str | None = None
    date_debut:  date
    date_fin:    date
    places_dispo: int       = Field(..., ge=1)

    @field_validator("date_fin")
    @classmethod
    def date_fin_apres_debut(cls, fin: date, info) -> date:
        debut = info.data.get("date_debut")
        if debut and fin <= debut:
            raise ValueError("La date de fin doit être postérieure à la date de début")
        return fin


class MiseAJourOffre(BaseModel):
    titre:        Optional[str] = Field(None, min_length=5, max_length=200)
    domaine:      Optional[str] = Field(None, min_length=2, max_length=100)
    description:  Optional[str] = None
    date_debut:   Optional[date] = None
    date_fin:     Optional[date] = None
    places_dispo: Optional[int]  = Field(None, ge=0)
    statut:       Optional[StatutOffre] = None


class SortieOffre(BaseModel):
    id:           str
    titre:        str
    domaine:      str
    description:  Optional[str]
    date_debut:   date
    date_fin:     date
    places_dispo: int
    statut:       StatutOffre
    cree_le:      datetime
    mis_a_jour_le: datetime

    model_config = {"from_attributes": True}


class ListeOffres(BaseModel):
    total:  int
    page:   int
    taille_page: int
    offres: list[SortieOffre]