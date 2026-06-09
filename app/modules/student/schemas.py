"""
Chemin : Hr-skills-stage-backend/app/modules/student/schemas.py
"""
from pydantic import BaseModel
from typing import Optional
from app.modules.enrollment.schemas import SortieInscription
from app.modules.document.schemas import SortieDocument
from app.modules.payment.schemas import SortiePaiement


class TableauBordStagiaire(BaseModel):
    inscription:       Optional[SortieInscription]
    documents:         list[SortieDocument]
    paiements:         list[SortiePaiement]
    progression_pct:   float
    documents_valides: int
    documents_total:   int