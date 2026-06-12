"""
Chemin : Hr-skills-stage-backend/app/modules/payment/models.py
---------------------------------------------------------------
Modèle SQLAlchemy — Table : paiements
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import StatutPaiement, ModePaiement


class Paiement(Base):
    __tablename__ = "paiements"

    __table_args__ = (
        UniqueConstraint("reference", name="uq_paiement_reference"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    inscription_id = Column(String, ForeignKey("inscriptions.id", ondelete="CASCADE"), nullable=False, index=True)

    montant = Column(Numeric(10, 2), nullable=False)
    devise  = Column(String(10), nullable=False, default="XAF")

    mode_paiement = Column(
        SAEnum(
            ModePaiement,
            values_callable=lambda x: [e.value for e in x],
            name="modepaiement",
            create_type=False,
        ),
        nullable=False,
    )
    statut = Column(
        SAEnum(
            StatutPaiement,
            values_callable=lambda x: [e.value for e in x],
            name="statutpaiement",
            create_type=False,
        ),
        nullable=False, default=StatutPaiement.EN_ATTENTE, index=True,
    )

    reference    = Column(String(100), unique=True, nullable=True, index=True)
    url_recu     = Column(String(500), nullable=True)
    meta_donnees = Column(JSONB, nullable=True)   # Payload brut du webhook

    initie_le     = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    confirme_le   = Column(DateTime(timezone=True), nullable=True)
    mis_a_jour_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    inscription = relationship("Inscription", back_populates="paiements")

    @property
    def est_confirme(self) -> bool:
        return self.statut == StatutPaiement.CONFIRME

    @property
    def montant_formate(self) -> str:
        return f"{self.montant:,.0f} {self.devise}"

    def __repr__(self) -> str:
        return f"<Paiement id={self.id} montant={self.montant} statut={self.statut}>"