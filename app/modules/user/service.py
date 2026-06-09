"""
Chemin : Hr-skills-stage-backend/app/modules/user/service.py
-------------------------------------------------------------
Logique métier du module utilisateur.
Orchestre les opérations CRUD et applique les règles fonctionnelles.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.crud import CrudUtilisateur
from app.modules.user.models import Utilisateur
from app.modules.user.schemas import (
    CreationUtilisateur,
    MiseAJourUtilisateur,
    ChangementMotDePasse,
    ListeUtilisateurs,
    SortieUtilisateurSimple,
)
from app.core.security import hacher_mot_de_passe, verifier_mot_de_passe
from app.core.exceptions import (
    NonTrouve,
    EmailDejaUtilise,
    RequeteInvalide,
    AccesInterdit,
)
from app.shared.enums import RoleEnum


class ServiceUtilisateur:
    """
    Service métier pour la gestion des utilisateurs.

    Utilisation :
        service = ServiceUtilisateur(session)
        utilisateur = await service.creer_utilisateur(donnees)
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud = CrudUtilisateur(session)

    # ─────────────────────────────────────────
    # CRÉATION
    # ─────────────────────────────────────────

    async def creer_utilisateur(
        self,
        donnees: CreationUtilisateur,
        role_force: Optional[RoleEnum] = None,
    ) -> Utilisateur:
        """
        Crée un nouvel utilisateur après validation des règles métier.

        Règles :
            - L'email ne doit pas déjà exister
            - Le mot de passe est hashé avant insertion
            - Le rôle peut être forcé par l'admin
        """
        # Vérifier que le courriel n'est pas déjà utilisé
        if await self.crud.courriel_existe(donnees.courriel):
            raise EmailDejaUtilise()

        # Hacher le mot de passe
        hash_mdp = hacher_mot_de_passe(donnees.mot_de_passe)

        # Préparer les données
        donnees_insertion = {
            "nom":          donnees.nom,
            "prenom":       donnees.prenom,
            "courriel":     donnees.courriel,
            "mot_de_passe": hash_mdp,
            "telephone":    donnees.telephone,
            "role":         role_force or donnees.role,
        }

        return await self.crud.creer(donnees_insertion)

    # ─────────────────────────────────────────
    # LECTURE
    # ─────────────────────────────────────────

    async def obtenir_par_id(self, utilisateur_id: str) -> Utilisateur:
        """
        Retourne un utilisateur par son ID.
        Lève NonTrouve si l'utilisateur n'existe pas.
        """
        utilisateur = await self.crud.obtenir_par_id(utilisateur_id)
        if not utilisateur:
            raise NonTrouve("Utilisateur")
        return utilisateur

    async def obtenir_par_courriel(self, courriel: str) -> Utilisateur:
        """
        Retourne un utilisateur par son courriel.
        Lève NonTrouve si l'utilisateur n'existe pas.
        """
        utilisateur = await self.crud.obtenir_par_courriel(courriel)
        if not utilisateur:
            raise NonTrouve("Utilisateur")
        return utilisateur

    async def lister_utilisateurs(
        self,
        page: int = 1,
        taille_page: int = 20,
        role: Optional[RoleEnum] = None,
        est_actif: Optional[bool] = None,
    ) -> ListeUtilisateurs:
        """
        Retourne la liste paginée des utilisateurs.
        Réservé à l'administrateur.
        """
        utilisateurs, total = await self.crud.lister_tous(
            page=page,
            taille_page=taille_page,
            role=role,
            est_actif=est_actif,
        )

        return ListeUtilisateurs(
            total=total,
            page=page,
            taille_page=taille_page,
            utilisateurs=[
                SortieUtilisateurSimple.model_validate(u)
                for u in utilisateurs
            ],
        )

    async def lister_encadreurs(self) -> list[Utilisateur]:
        """Retourne tous les encadreurs actifs."""
        return await self.crud.lister_encadreurs()

    # ─────────────────────────────────────────
    # MISE À JOUR
    # ─────────────────────────────────────────

    async def mettre_a_jour_profil(
        self,
        utilisateur_id: str,
        donnees: MiseAJourUtilisateur,
        utilisateur_courant: Utilisateur,
    ) -> Utilisateur:
        """
        Met à jour le profil d'un utilisateur.

        Règles :
            - Un utilisateur peut modifier uniquement son propre profil
            - Un admin peut modifier n'importe quel profil
        """
        # Vérifier les droits
        if (
            utilisateur_courant.id != utilisateur_id
            and not utilisateur_courant.est_admin
        ):
            raise AccesInterdit(
                detail="Vous ne pouvez modifier que votre propre profil"
            )

        # Vérifier que l'utilisateur existe
        await self.obtenir_par_id(utilisateur_id)

        utilisateur_maj = await self.crud.mettre_a_jour(
            utilisateur_id,
            donnees.model_dump(exclude_none=True),
        )
        return utilisateur_maj

    async def changer_mot_de_passe(
        self,
        utilisateur_id: str,
        donnees: ChangementMotDePasse,
        utilisateur_courant: Utilisateur,
    ) -> None:
        """
        Change le mot de passe d'un utilisateur.

        Règles :
            - L'ancien mot de passe doit être correct
            - Le nouveau mot de passe ne doit pas être identique à l'ancien
        """
        # Vérifier les droits
        if utilisateur_courant.id != utilisateur_id:
            raise AccesInterdit(
                detail="Vous ne pouvez changer que votre propre mot de passe"
            )

        utilisateur = await self.obtenir_par_id(utilisateur_id)

        # Vérifier l'ancien mot de passe
        if not verifier_mot_de_passe(
            donnees.ancien_mot_de_passe,
            utilisateur.mot_de_passe,
        ):
            raise RequeteInvalide(detail="Ancien mot de passe incorrect")

        # Vérifier que le nouveau est différent
        if verifier_mot_de_passe(
            donnees.nouveau_mot_de_passe,
            utilisateur.mot_de_passe,
        ):
            raise RequeteInvalide(
                detail="Le nouveau mot de passe doit être différent de l'ancien"
            )

        nouveau_hash = hacher_mot_de_passe(donnees.nouveau_mot_de_passe)
        await self.crud.mettre_a_jour_mot_de_passe(utilisateur_id, nouveau_hash)

    async def mettre_a_jour_photo(
        self,
        utilisateur_id: str,
        url_photo: str,
    ) -> Utilisateur:
        """Met à jour la photo de profil."""
        await self.obtenir_par_id(utilisateur_id)
        await self.crud.mettre_a_jour_photo(utilisateur_id, url_photo)
        return await self.obtenir_par_id(utilisateur_id)

    # ─────────────────────────────────────────
    # ACTIVATION / DÉSACTIVATION
    # ─────────────────────────────────────────

    async def desactiver_compte(
        self,
        utilisateur_id: str,
        utilisateur_courant: Utilisateur,
    ) -> None:
        """
        Désactive un compte utilisateur.
        Réservé à l'administrateur.
        """
        if utilisateur_id == utilisateur_courant.id:
            raise RequeteInvalide(
                detail="Vous ne pouvez pas désactiver votre propre compte"
            )

        await self.obtenir_par_id(utilisateur_id)
        await self.crud.desactiver(utilisateur_id)

    async def activer_compte(self, utilisateur_id: str) -> None:
        """Réactive un compte désactivé. Réservé à l'administrateur."""
        await self.obtenir_par_id(utilisateur_id)
        await self.crud.activer(utilisateur_id)

    # ─────────────────────────────────────────
    # STATISTIQUES
    # ─────────────────────────────────────────

    async def statistiques_par_role(self) -> dict:
        """Retourne le nombre d'utilisateurs par rôle."""
        return await self.crud.compter_par_role()