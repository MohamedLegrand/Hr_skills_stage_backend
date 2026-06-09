"""
Chemin : Hr-skills-stage-backend/app/modules/encadreur/schemas.py
"""
from pydantic import BaseModel
from app.modules.enrollment.schemas import SortieInscription


class TableauBordEncadreur(BaseModel):
    total_stagiaires:    int
    stages_en_cours:     int
    evaluations_saisies: int
    inscriptions:        list[SortieInscription]