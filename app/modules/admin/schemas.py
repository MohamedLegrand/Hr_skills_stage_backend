"""
Chemin : Hr-skills-stage-backend/app/modules/admin/schemas.py
"""
from pydantic import BaseModel


class TableauBordAdmin(BaseModel):
    total_stagiaires:       int
    inscriptions_en_attente: int
    stages_en_cours:        int
    stages_termines:        int
    documents_a_valider:    int
    paiements_confirmes:    int
    total_recettes:         float
    offres_ouvertes:        int