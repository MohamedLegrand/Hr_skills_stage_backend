"""
Chemin : Hr-skills-stage-backend/app/modules/evaluation/models.py
------------------------------------------------------------------
Modèle SQLAlchemy — Table : evaluations
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import MoisEvaluation


class Evaluation(Base):
    __tablename__ = "evaluations"

    __table_args__ = (
        UniqueConstraint("inscription_id", "mois", name="uq_evaluation_mois"),
        CheckConstraint("note_globale BETWEEN 0 AND 20", name="chk_note_globale"),
        CheckConstraint("mois BETWEEN 1 AND 3", name="chk_mois"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    inscription_id = Column(String, ForeignKey("inscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    encadreur_id   = Column(String, ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True)

    mois = Column(
        SAEnum(MoisEvaluation, name="moisevaluation", create_type=False),
        nullable=False, index=True,
    )

    note_globale      = Column(Numeric(4, 2), nullable=False)
    note_technique    = Column(Numeric(4, 2), nullable=True)
    note_comportement = Column(Numeric(4, 2), nullable=True)
    note_ponctualite  = Column(Numeric(4, 2), nullable=True)

    commentaire = Column(Text, nullable=True)
    recommande  = Column(Boolean, nullable=True)

    evalue_le     = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    mis_a_jour_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    inscription = relationship("Inscription", back_populates="evaluations")
    encadreur   = relationship("Utilisateur", foreign_keys=[encadreur_id])

    @property
    def mention(self) -> str:
        note = float(self.note_globale)
        if note >= 16: return "Très bien"
        if note >= 14: return "Bien"
        if note >= 12: return "Assez bien"
        if note >= 10: return "Passable"
        return "Insuffisant"

    def __repr__(self) -> str:
        return f"<Evaluation id={self.id} mois={self.mois} note={self.note_globale}>"