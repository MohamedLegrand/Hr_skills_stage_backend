"""
Chemin : Hr-skills-stage-backend/app/modules/audit_log/schemas.py
-----------------------------------------------------------------
Schémas Pydantic pour le module journal d'audit.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class CreationJournalAudit(BaseModel):
    """
    Schéma interne utilisé par les services pour
    enregistrer une action dans le journal d'audit.
    Jamais exposé directement via l'API.
    """
    utilisateur_id:    Optional[str] = None
    action:            str           = Field(..., examples=["document.valide", "paiement.confirme"])
    table_cible:       Optional[str] = None
    enregistrement_id: Optional[str] = None
    anciennes_valeurs: Optional[Any] = None
    nouvelles_valeurs: Optional[Any] = None
    adresse_ip:        Optional[str] = None


class SortieJournalAudit(BaseModel):
    """
    Schéma de réponse API pour une entrée du journal d'audit.
    Réservé à l'administrateur.
    """
    id:                str
    utilisateur_id:    Optional[str]
    action:            str
    table_cible:       Optional[str]
    enregistrement_id: Optional[str]
    anciennes_valeurs: Optional[Any]
    nouvelles_valeurs: Optional[Any]
    adresse_ip:        Optional[str]
    effectue_le:       datetime

    model_config = {"from_attributes": True}


class FiltresJournalAudit(BaseModel):
    """Filtres disponibles pour la recherche dans le journal."""
    utilisateur_id:    Optional[str]      = None
    action:            Optional[str]      = None
    table_cible:       Optional[str]      = None
    enregistrement_id: Optional[str]      = None
    date_debut:        Optional[datetime] = None
    date_fin:          Optional[datetime] = None


class ListeJournalAudit(BaseModel):
    """Réponse paginée du journal d'audit."""
    total:     int
    page:      int
    taille_page: int
    journaux:  list[SortieJournalAudit]