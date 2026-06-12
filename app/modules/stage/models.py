"""
Chemin : Hr-skills-stage-backend/app/modules/stage/models.py
-------------------------------------------------------------
Modèle SQLAlchemy — Table : offres_stage
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Date, DateTime, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import StatutOffre


class OffreStage(Base):
    __tablename__ = "offres_stage"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    titre        = Column(String(200), nullable=False)
    domaine      = Column(String(100), nullable=False, index=True)
    description  = Column(Text, nullable=True)
    date_debut   = Column(Date, nullable=False)
    date_fin     = Column(Date, nullable=False)
    places_dispo = Column(Integer, nullable=False, default=1)
    statut       = Column(
        SAEnum(
            StatutOffre,
            values_callable=lambda x: [e.value for e in x],
            name="statutoffre",
            create_type=False,
        ),
        nullable=False, default=StatutOffre.OUVERT, index=True,
    )
    cree_par = Column(String, nullable=True)  # FK vers utilisateurs.id

    cree_le       = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    mis_a_jour_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    inscriptions = relationship("Inscription", back_populates="offre", lazy="select")

    @property
    def est_disponible(self) -> bool:
        return self.statut == StatutOffre.OUVERT and self.places_dispo > 0

    def __repr__(self) -> str:
        return f"<OffreStage id={self.id} titre={self.titre} statut={self.statut}>"