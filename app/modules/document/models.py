"""
Chemin : Hr-skills-stage-backend/app/modules/document/models.py
----------------------------------------------------------------
Modèle SQLAlchemy — Table : documents
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, BigInteger, DateTime, Text, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import StatutDocument, TypeDocument


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    inscription_id = Column(String, ForeignKey("inscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    type_code      = Column(
        SAEnum(
            TypeDocument,
            values_callable=lambda x: [e.value for e in x],
            name="typedocument",
            create_type=False,
        ),
        nullable=False, index=True,
    )
    url_fichier   = Column(String(500), nullable=False)
    taille_octets = Column(BigInteger, nullable=True)

    statut = Column(
        SAEnum(
            StatutDocument,
            values_callable=lambda x: [e.value for e in x],
            name="statutdocument",
            create_type=False,
        ),
        nullable=False, default=StatutDocument.EN_ATTENTE, index=True,
    )
    commentaire = Column(Text, nullable=True)   # Motif de rejet obligatoire
    traite_par  = Column(String, ForeignKey("utilisateurs.id", ondelete="SET NULL"), nullable=True)

    soumis_le     = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    traite_le     = Column(DateTime(timezone=True), nullable=True)
    mis_a_jour_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    inscription  = relationship("Inscription", back_populates="documents")
    valideur     = relationship("Utilisateur", foreign_keys=[traite_par])

    @property
    def est_valide(self) -> bool:
        return self.statut == StatutDocument.VALIDE

    @property
    def est_rejete(self) -> bool:
        return self.statut == StatutDocument.REJETE

    def __repr__(self) -> str:
        return f"<Document id={self.id} type={self.type_code} statut={self.statut}>"