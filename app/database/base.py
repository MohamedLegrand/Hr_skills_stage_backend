"""
Chemin : Hr-skills-stage-backend/app/database/base.py
------------------------------------------------------
Base déclarative SQLAlchemy.
Tous les modèles du projet héritent de cette classe Base.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Classe de base pour tous les modèles SQLAlchemy du projet.

    Fournit automatiquement :
        - id            : UUID généré automatiquement
        - cree_le       : horodatage de création
        - mis_a_jour_le : horodatage de dernière modification

    Utilisation dans un modèle :
        from app.database.base import Base

        class MonModele(Base):
            __tablename__ = "ma_table"
            nom: Mapped[str]
    """

    # Colonne id UUID commune à tous les modèles
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )

    # Horodatage de création — géré automatiquement par PostgreSQL
    cree_le: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Horodatage de dernière modification
    mis_a_jour_le: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def vers_dict(self) -> dict:
        """
        Convertit le modèle en dictionnaire.
        Utile pour le débogage et les logs.
        """
        return {
            colonne.name: getattr(self, colonne.name)
            for colonne in self.__table__.columns
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"