"""
Chemin : Hr-skills-stage-backend/app/modules/report/models.py
--------------------------------------------------------------
Modèle SQLAlchemy — Table : rapports
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import TypeRapport


class Rapport(Base):
    __tablename__ = "rapports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    inscription_id = Column(String, ForeignKey("inscriptions.id", ondelete="CASCADE"), nullable=False, index=True)

    type_rapport = Column(
        SAEnum(TypeRapport, name="typerapport", create_type=False),
        nullable=False, index=True,
    )

    url_pdf        = Column(String(500), nullable=True)
    donnees_export = Column(JSONB, nullable=True)   # Données brutes pour export CSV/Excel
    genere_par     = Column(String, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True)

    genere_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    inscription = relationship("Inscription", back_populates="rapports")
    generateur  = relationship("Utilisateur", foreign_keys=[genere_par])

    def __repr__(self) -> str:
        return f"<Rapport id={self.id} type={self.type_rapport}>" 