"""
Chemin : Hr-skills-stage-backend/app/modules/convention/models.py
------------------------------------------------------------------
Modèle SQLAlchemy — Table : conventions
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base


class Convention(Base):
    __tablename__ = "conventions"

    __table_args__ = (
        UniqueConstraint("inscription_id", name="uq_convention_inscription"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    inscription_id = Column(String, ForeignKey("inscriptions.id", ondelete="CASCADE"),
                            nullable=False, unique=True, index=True)
    url_pdf        = Column(String(500), nullable=False)
    generee_par    = Column(String, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True)

    generee_le    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    mis_a_jour_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    inscription = relationship("Inscription", back_populates="convention")
    generateur  = relationship("Utilisateur", foreign_keys=[generee_par])

    def __repr__(self) -> str:
        return f"<Convention id={self.id} inscription={self.inscription_id}>" 