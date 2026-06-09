"""
Chemin : Hr-skills-stage-backend/app/modules/audit_log/models.py
-----------------------------------------------------------------
Modèle SQLAlchemy — Table : journaux_audit
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base


class JournalAudit(Base):
    __tablename__ = "journaux_audit"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    utilisateur_id    = Column(String, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True, index=True)
    action            = Column(String(100), nullable=False, index=True)
    table_cible       = Column(String(100), nullable=True)
    enregistrement_id = Column(String, nullable=True)

    anciennes_valeurs = Column(JSONB, nullable=True)
    nouvelles_valeurs = Column(JSONB, nullable=True)

    adresse_ip  = Column(String(45), nullable=True)
    effectue_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                         nullable=False, index=True)

    utilisateur = relationship("Utilisateur", foreign_keys=[utilisateur_id])

    def __repr__(self) -> str:
        return f"<JournalAudit id={self.id} action={self.action}>" 