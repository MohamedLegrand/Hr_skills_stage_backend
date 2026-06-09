"""
Chemin : Hr-skills-stage-backend/app/modules/payment/schemas.py
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
from app.shared.enums import StatutPaiement, ModePaiement


class InitiationPaiement(BaseModel):
    inscription_id: str
    montant:        float
    mode_paiement:  ModePaiement
    devise:         str = "XAF"


class ChargeWebhook(BaseModel):
    reference:    str
    statut:       str
    meta_donnees: Optional[Any] = None


class SortiePaiement(BaseModel):
    id:             str
    inscription_id: str
    montant:        float
    devise:         str
    mode_paiement:  ModePaiement
    statut:         StatutPaiement
    reference:      Optional[str]
    url_recu:       Optional[str]
    initie_le:      datetime
    confirme_le:    Optional[datetime]

    model_config = {"from_attributes": True}


class ListePaiements(BaseModel):
    total:     int
    paiements: list[SortiePaiement]