"""
Chemin : Hr-skills-stage-backend/app/modules/attendance/schemas.py
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.shared.enums import StatutPresence


class MarquagePresence(BaseModel):
    inscription_id: str
    date_presence:  date
    statut:         StatutPresence
    commentaire:    Optional[str] = None


class SortiePresence(BaseModel):
    id:             str
    inscription_id: str
    date_presence:  date
    statut:         StatutPresence
    commentaire:    Optional[str]
    enregistre_par: Optional[str]
    cree_le:        datetime

    model_config = {"from_attributes": True}


class ResumePresences(BaseModel):
    inscription_id:   str
    jours_presents:   int
    jours_absents:    int
    jours_justifies:  int
    total_jours:      int
    taux_presence_pct: float