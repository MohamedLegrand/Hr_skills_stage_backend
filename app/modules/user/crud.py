"""
Chemin : Hr-skills-stage-backend/app/modules/user/crud.py
----------------------------------------------------------
Opérations CRUD sur la table 'utilisateurs'.
Toutes les interactions directes avec la base de données.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.models import Utilisateur
from app.shared.enums import RoleEnum


class CrudUtilisateur:
    """
    Classe regroupant toutes les opérations BDD
    sur la table utilisateurs.

    Utilisation :
        crud = CrudUtilisateur(session)
        utilisateur = await crud.obtenir_par_id("uuid-ici")
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─────────────────────────────────────────
    # LECTURE
    # ─────────────────────────────────────────

    async def obtenir_par_id(self, utilisateur_id: str) -> Optional[Utilisateur]:
        """Retourne un utilisateur par son ID ou None s'il n'existe pas."""
        resultat = await self.session.execute(
            select(Utilisateur).where(Utilisateur.id == utilisateur_id)
        )
        return resultat.scalar_one_or_none()

    async def obtenir_par_courriel(self, courriel: str) -> Optional[Utilisateur]:
        """Retourne un utilisateur par son adresse email ou None."""
        resultat = await self.session.execute(
            select(Utilisateur).where(
                Utilisateur.courriel == courriel.lower().strip()
            )
        )
        return resultat.scalar_one_or_none()

    async def courriel_existe(self, courriel: str) -> bool:
        """Vérifie si une adresse email est déjà utilisée."""
        resultat = await self.session.execute(
            select(func.count()).where(
                Utilisateur.courriel == courriel.lower().strip()
            )
        )
        return resultat.scalar() > 0

    async def lister_tous(
        self,
        page: int = 1,
        taille_page: int = 20,
        role: Optional[RoleEnum] = None,
        est_actif: Optional[bool] = None,
    ) -> tuple[list[Utilisateur], int]:
        """
        Retourne la liste paginée des utilisateurs avec filtres optionnels.
        Retourne un tuple (liste, total).
        """
        requete = select(Utilisateur)
        requete_total = select(func.count()).select_from(Utilisateur)

        # Filtres optionnels
        if role is not None:
            requete = requete.where(Utilisateur.role == role)
            requete_total = requete_total.where(Utilisateur.role == role)

        if est_actif is not None:
            requete = requete.where(Utilisateur.est_actif == est_actif)
            requete_total = requete_total.where(Utilisateur.est_actif == est_actif)

        # Total
        total = (await self.session.execute(requete_total)).scalar()

        # Pagination
        decalage = (page - 1) * taille_page
        requete = (
            requete
            .order_by(Utilisateur.cree_le.desc())
            .offset(decalage)
            .limit(taille_page)
        )

        resultat = await self.session.execute(requete)
        return resultat.scalars().all(), total

    async def lister_encadreurs(self) -> list[Utilisateur]:
        """Retourne tous les encadreurs actifs."""
        resultat = await self.session.execute(
            select(Utilisateur).where(
                Utilisateur.role == RoleEnum.ENCADREUR,
                Utilisateur.est_actif == True,
            ).order_by(Utilisateur.nom)
        )
        return resultat.scalars().all()

    # ─────────────────────────────────────────
    # CRÉATION
    # ─────────────────────────────────────────

    async def creer(self, donnees: dict) -> Utilisateur:
        """
        Crée un nouvel utilisateur en base de données.

        Les données doivent inclure le mot_de_passe déjà hashé.
        """
        # Normaliser le courriel en minuscules
        if "courriel" in donnees:
            donnees["courriel"] = donnees["courriel"].lower().strip()

        utilisateur = Utilisateur(**donnees)
        self.session.add(utilisateur)
        await self.session.flush()   # Génère l'ID sans commit
        await self.session.refresh(utilisateur)
        return utilisateur

    # ─────────────────────────────────────────
    # MISE À JOUR
    # ─────────────────────────────────────────

    async def mettre_a_jour(
        self,
        utilisateur_id: str,
        donnees: dict,
    ) -> Optional[Utilisateur]:
        """
        Met à jour les champs fournis d'un utilisateur.
        Retourne l'utilisateur mis à jour ou None s'il n'existe pas.
        """
        # Supprimer les valeurs None pour ne mettre à jour que ce qui est fourni
        donnees_nettoyees = {k: v for k, v in donnees.items() if v is not None}

        if not donnees_nettoyees:
            return await self.obtenir_par_id(utilisateur_id)

        await self.session.execute(
            update(Utilisateur)
            .where(Utilisateur.id == utilisateur_id)
            .values(**donnees_nettoyees)
        )
        await self.session.flush()
        return await self.obtenir_par_id(utilisateur_id)

    async def mettre_a_jour_mot_de_passe(
        self,
        utilisateur_id: str,
        nouveau_hash: str,
    ) -> None:
        """Met à jour uniquement le mot de passe hashé."""
        await self.session.execute(
            update(Utilisateur)
            .where(Utilisateur.id == utilisateur_id)
            .values(mot_de_passe=nouveau_hash)
        )
        await self.session.flush()

    async def mettre_a_jour_derniere_connexion(
        self,
        utilisateur_id: str,
    ) -> None:
        """Enregistre la date/heure de la dernière connexion."""
        from datetime import datetime, timezone
        await self.session.execute(
            update(Utilisateur)
            .where(Utilisateur.id == utilisateur_id)
            .values(derniere_connexion=datetime.now(timezone.utc))
        )
        await self.session.flush()

    async def mettre_a_jour_photo(
        self,
        utilisateur_id: str,
        url_photo: str,
    ) -> None:
        """Met à jour l'URL de la photo de profil."""
        await self.session.execute(
            update(Utilisateur)
            .where(Utilisateur.id == utilisateur_id)
            .values(url_photo=url_photo)
        )
        await self.session.flush()

    # ─────────────────────────────────────────
    # ACTIVATION / DÉSACTIVATION
    # ─────────────────────────────────────────

    async def desactiver(self, utilisateur_id: str) -> None:
        """Désactive un compte sans le supprimer (soft delete)."""
        await self.session.execute(
            update(Utilisateur)
            .where(Utilisateur.id == utilisateur_id)
            .values(est_actif=False)
        )
        await self.session.flush()

    async def activer(self, utilisateur_id: str) -> None:
        """Réactive un compte désactivé."""
        await self.session.execute(
            update(Utilisateur)
            .where(Utilisateur.id == utilisateur_id)
            .values(est_actif=True)
        )
        await self.session.flush()

    # ─────────────────────────────────────────
    # STATISTIQUES
    # ─────────────────────────────────────────

    async def compter_par_role(self) -> dict:
        """Retourne le nombre d'utilisateurs par rôle."""
        resultat = await self.session.execute(
            select(Utilisateur.role, func.count().label("total"))
            .group_by(Utilisateur.role)
        )
        return {ligne.role.value: ligne.total for ligne in resultat}