"""
Chemin : Hr-skills-stage-backend/app/modules/notification/models.py
--------------------------------------------------------------------
Modèle SQLAlchemy — Table : notifications
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import TypeNotification


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    utilisateur_id = Column(String, ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True)

    titre   = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    type_notif = Column(
        SAEnum(TypeNotification, name="typenotification", create_type=False),
        nullable=False, default=TypeNotification.INFO,
    )

    lien            = Column(String(500), nullable=True)
    lu              = Column(Boolean, nullable=False, default=False, index=True)
    lu_le           = Column(DateTime(timezone=True), nullable=True)
    envoye_par_mail = Column(Boolean, nullable=False, default=False)

    cree_le = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                     nullable=False, index=True)

    # Relations
    utilisateur = relationship("Utilisateur", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification id={self.id} titre={self.titre} lu={self.lu}>"