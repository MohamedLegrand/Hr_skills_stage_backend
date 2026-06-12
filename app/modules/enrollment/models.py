"""
Chemin : Hr-skills-stage-backend/app/modules/enrollment/models.py
------------------------------------------------------------------
Modèle SQLAlchemy — Table : inscriptions
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import StatutInscription


class Inscription(Base):
    __tablename__ = "inscriptions"

    __table_args__ = (
        UniqueConstraint("stagiaire_id", "offre_id", name="uq_stagiaire_offre"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    stagiaire_id = Column(String, ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True)
    offre_id     = Column(String, ForeignKey("offres_stage.id", ondelete="CASCADE"), nullable=False, index=True)
    encadreur_id = Column(String, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True, index=True)

    statut = Column(
        SAEnum(
            StatutInscription,
            values_callable=lambda x: [e.value for e in x],
            name="statutinscription",
            create_type=False,
        ),
        nullable=False, default=StatutInscription.EN_ATTENTE, index=True,
    )
    motif_refus     = Column(Text, nullable=True)
    date_soumission = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    date_validation = Column(DateTime(timezone=True), nullable=True)
    mis_a_jour_le   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    stagiaire  = relationship("Utilisateur", foreign_keys=[stagiaire_id], back_populates="inscriptions_stagiaire")
    encadreur  = relationship("Utilisateur", foreign_keys=[encadreur_id], back_populates="inscriptions_encadreur")
    offre      = relationship("OffreStage", back_populates="inscriptions")
    documents  = relationship("Document",  back_populates="inscription", cascade="all, delete-orphan")
    paiements  = relationship("Paiement",  back_populates="inscription", cascade="all, delete-orphan")
    presences  = relationship("Presence",  back_populates="inscription", cascade="all, delete-orphan")
    evaluations= relationship("Evaluation",back_populates="inscription", cascade="all, delete-orphan")
    convention = relationship("Convention",back_populates="inscription", uselist=False, cascade="all, delete-orphan")
    rapports   = relationship("Rapport",   back_populates="inscription", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Inscription id={self.id} stagiaire={self.stagiaire_id} statut={self.statut}>"