"""
Chemin : Hr-skills-stage-backend/app/modules/auth/models.py
------------------------------------------------------------
Modèle SQLAlchemy — Table : tokens_reinitialisation
Stocke les tokens de réinitialisation de mot de passe.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base


class TokenReinitialisation(Base):
    """
    Token sécurisé pour la réinitialisation du mot de passe.
    Expire après 30 minutes et ne peut être utilisé qu'une seule fois.
    """
    __tablename__ = "tokens_reinitialisation"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    utilisateur_id = Column(
        String,
        ForeignKey("utilisateurs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token    = Column(String(255), nullable=False, unique=True, index=True)
    expire_le = Column(DateTime(timezone=True), nullable=False)
    utilise  = Column(Boolean, nullable=False, default=False)

    cree_le  = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    utilisateur = relationship("Utilisateur", foreign_keys=[utilisateur_id])

    @property
    def est_expire(self) -> bool:
        return datetime.now(timezone.utc) > self.expire_le

    @property
    def est_valide(self) -> bool:
        return not self.utilise and not self.est_expire

    def __repr__(self) -> str:
        return f"<TokenReinitialisation utilisateur={self.utilisateur_id} expire={self.expire_le}>"