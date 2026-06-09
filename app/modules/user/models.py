"""
Chemin : Hr-skills-stage-backend/app/modules/user/models.py
------------------------------------------------------------
Modèle SQLAlchemy — Table : utilisateurs
Conforme au schéma PostgreSQL hr_skills_stage.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.shared.enums import RoleEnum


class Utilisateur(Base):
    """
    Représente un utilisateur de la plateforme HR-Skills.
    Correspond à la table 'utilisateurs' dans hr_skills_stage.

    Trois types d'utilisateurs :
        - admin     : administrateur HR-Skills
        - encadreur : responsable en entreprise
        - stagiaire : étudiant en stage
    """

    __tablename__ = "utilisateurs"

    # ── Clé primaire ──────────────────────────────────────────
    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="Identifiant unique UUID",
    )

    # ── Informations personnelles ─────────────────────────────
    nom = Column(
        String(100),
        nullable=False,
        comment="Nom de famille",
    )

    prenom = Column(
        String(100),
        nullable=False,
        comment="Prénom",
    )

    courriel = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
        comment="Adresse email — utilisée pour la connexion",
    )

    mot_de_passe = Column(
        String(255),
        nullable=False,
        comment="Mot de passe hashé bcrypt — jamais en clair",
    )

    # ── Rôle et statut ────────────────────────────────────────
    role = Column(
        SAEnum(RoleEnum, name="roleenum", create_type=False),
        nullable=False,
        default=RoleEnum.STAGIAIRE,
        comment="Rôle : admin | encadreur | stagiaire",
    )

    est_actif = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Compte actif ou désactivé",
    )

    # ── Informations de contact ───────────────────────────────
    telephone = Column(
        String(25),
        nullable=True,
        comment="Numéro de téléphone",
    )

    url_photo = Column(
        String(500),
        nullable=True,
        comment="URL photo de profil — Supabase Storage",
    )

    # ── Horodatages ───────────────────────────────────────────
    derniere_connexion = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date et heure de la dernière connexion",
    )

    cree_le = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Date de création du compte",
    )

    mis_a_jour_le = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Date de dernière modification",
    )

    # ── Relations ─────────────────────────────────────────────
    inscriptions_stagiaire = relationship(
        "Inscription",
        foreign_keys="Inscription.stagiaire_id",
        back_populates="stagiaire",
        lazy="select",
    )

    inscriptions_encadreur = relationship(
        "Inscription",
        foreign_keys="Inscription.encadreur_id",
        back_populates="encadreur",
        lazy="select",
    )

    notifications = relationship(
        "Notification",
        back_populates="utilisateur",
        lazy="select",
        cascade="all, delete-orphan",
    )

    # ── Propriétés utilitaires ────────────────────────────────
    @property
    def nom_complet(self) -> str:
        """Retourne : Prénom NOM."""
        return f"{self.prenom} {self.nom.upper()}"

    @property
    def est_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN

    @property
    def est_encadreur(self) -> bool:
        return self.role == RoleEnum.ENCADREUR

    @property
    def est_stagiaire(self) -> bool:
        return self.role == RoleEnum.STAGIAIRE

    def __repr__(self) -> str:
        return (
            f"<Utilisateur id={self.id} "
            f"courriel={self.courriel} "
            f"role={self.role}>"
        )