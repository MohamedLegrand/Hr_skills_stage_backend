"""
Chemin : Hr-skills-stage-backend/app/modules/attendance/models.py
------------------------------------------------------------------
Modèle SQLAlchemy — Table : presences
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import StatutPresence


class Presence(Base):
    __tablename__ = "presences"

    __table_args__ = (
        UniqueConstraint("inscription_id", "date_presence", name="uq_presence_jour"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    inscription_id = Column(String, ForeignKey("inscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    date_presence  = Column(Date, nullable=False, index=True)

    statut = Column(
        SAEnum(
            StatutPresence,
            values_callable=lambda x: [e.value for e in x],
            name="statutpresence",
            create_type=False,
        ),
        nullable=False, index=True,
    )
    commentaire    = Column(Text, nullable=True)
    enregistre_par = Column(String, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True)

    cree_le       = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    mis_a_jour_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    inscription = relationship("Inscription", back_populates="presences")
    encadreur   = relationship("Utilisateur", foreign_keys=[enregistre_par])

    @property
    def est_present(self) -> bool:
        return self.statut == StatutPresence.PRESENT

    def __repr__(self) -> str:
        return f"<Presence id={self.id} date={self.date_presence} statut={self.statut}>"