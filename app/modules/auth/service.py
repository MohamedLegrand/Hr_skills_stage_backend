"""
Chemin : Hr-skills-stage-backend/app/modules/auth/service.py
-------------------------------------------------------------
Logique métier pour l'authentification et la réinitialisation
du mot de passe.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas import (
    RequeteConnexion,
    RequeteInscription,
    ReponseJeton,
    RequeteMotDePasseOublie,
    RequeteReinitialiserMDP,
    ReponseSimple,
)
from app.modules.auth.crud import CrudTokenReinitialisation
from app.modules.user.crud import CrudUtilisateur
from app.modules.user.schemas import CreationUtilisateur, SortieUtilisateur
from app.modules.user.service import ServiceUtilisateur
from app.core.security import verifier_mot_de_passe, hacher_mot_de_passe
from app.core.jwt import (
    creer_jeton_acces,
    creer_jeton_rafraichissement,
    valider_jeton_rafraichissement,
)
from app.core.exceptions import (
    IdentifiantsInvalides,
    CompteInactif,
    NonTrouve,
    RequeteInvalide,
)
from app.shared.enums import RoleEnum


class ServiceAuth:
    def __init__(self, session: AsyncSession):
        self.session      = session
        self.crud_user    = CrudUtilisateur(session)
        self.crud_token   = CrudTokenReinitialisation(session)

    # ─────────────────────────────────────────
    # CONNEXION
    # ─────────────────────────────────────────

    async def connecter(self, donnees: RequeteConnexion) -> ReponseJeton:
        utilisateur = await self.crud_user.obtenir_par_courriel(donnees.courriel)

        if not utilisateur:
            raise IdentifiantsInvalides()

        if not verifier_mot_de_passe(donnees.mot_de_passe, utilisateur.mot_de_passe):
            raise IdentifiantsInvalides()

        if not utilisateur.est_actif:
            raise CompteInactif()

        await self.crud_user.mettre_a_jour_derniere_connexion(utilisateur.id)

        return ReponseJeton(
            jeton_acces=creer_jeton_acces(
                utilisateur_id=utilisateur.id,
                role=utilisateur.role.value,
                courriel=utilisateur.courriel,
            ),
            jeton_rafraichissement=creer_jeton_rafraichissement(
                utilisateur_id=utilisateur.id
            ),
            utilisateur=SortieUtilisateur.model_validate(utilisateur),
        )

    # ─────────────────────────────────────────
    # INSCRIPTION STAGIAIRE
    # ─────────────────────────────────────────

    async def inscrire_stagiaire(self, donnees: RequeteInscription) -> ReponseJeton:
        creation = CreationUtilisateur(
            nom=donnees.nom,
            prenom=donnees.prenom,
            courriel=donnees.courriel,
            mot_de_passe=donnees.mot_de_passe,
            confirmation_mdp=donnees.confirmation_mdp,
            telephone=donnees.telephone,
            role=RoleEnum.STAGIAIRE,
        )
        service = ServiceUtilisateur(self.session)
        utilisateur = await service.creer_utilisateur(
            creation, role_force=RoleEnum.STAGIAIRE
        )

        return ReponseJeton(
            jeton_acces=creer_jeton_acces(
                utilisateur_id=utilisateur.id,
                role=utilisateur.role.value,
                courriel=utilisateur.courriel,
            ),
            jeton_rafraichissement=creer_jeton_rafraichissement(
                utilisateur_id=utilisateur.id
            ),
            utilisateur=SortieUtilisateur.model_validate(utilisateur),
        )

    # ─────────────────────────────────────────
    # RAFRAÎCHISSEMENT DU JETON
    # ─────────────────────────────────────────

    async def rafraichir_jeton(self, jeton_refresh: str) -> ReponseJeton:
        utilisateur_id = valider_jeton_rafraichissement(jeton_refresh)
        utilisateur = await self.crud_user.obtenir_par_id(utilisateur_id)

        if not utilisateur:
            raise NonTrouve("Utilisateur")

        if not utilisateur.est_actif:
            raise CompteInactif()

        return ReponseJeton(
            jeton_acces=creer_jeton_acces(
                utilisateur_id=utilisateur.id,
                role=utilisateur.role.value,
                courriel=utilisateur.courriel,
            ),
            jeton_rafraichissement=creer_jeton_rafraichissement(
                utilisateur_id=utilisateur.id
            ),
            utilisateur=SortieUtilisateur.model_validate(utilisateur),
        )

    # ─────────────────────────────────────────
    # MOT DE PASSE OUBLIÉ — ÉTAPE 1
    # ─────────────────────────────────────────

    async def mot_de_passe_oublie(
        self, donnees: RequeteMotDePasseOublie
    ) -> ReponseSimple:
        """
        Génère un token de réinitialisation et envoie un email.

        Règle de sécurité : même si l'email n'existe pas, on retourne
        toujours le même message pour ne pas révéler les comptes existants.
        """
        utilisateur = await self.crud_user.obtenir_par_courriel(donnees.courriel)

        if utilisateur and utilisateur.est_actif:
            # Créer le token
            token_obj = await self.crud_token.creer_token(utilisateur.id)

            # Envoyer l'email de réinitialisation
            await self._envoyer_email_reinitialisation(
                courriel=utilisateur.courriel,
                nom_complet=utilisateur.nom_complet,
                token=token_obj.token,
            )

        # Toujours retourner le même message (sécurité)
        return ReponseSimple(
            succes=True,
            message=(
                "Si cette adresse email est associée à un compte, "
                "vous recevrez un email avec les instructions de réinitialisation."
            ),
        )

    async def _envoyer_email_reinitialisation(
        self, courriel: str, nom_complet: str, token: str
    ) -> None:
        from app.utils.email import envoyer_email_reinitialisation_mdp
        await envoyer_email_reinitialisation_mdp(
            courriel=courriel,
            nom_complet=nom_complet,
            token=token,
        )

    # ─────────────────────────────────────────
    # MOT DE PASSE OUBLIÉ — ÉTAPE 2
    # ─────────────────────────────────────────

    async def reinitialiser_mot_de_passe(
        self, donnees: RequeteReinitialiserMDP
    ) -> ReponseSimple:
        """
        Vérifie le token et met à jour le mot de passe.

        Règles :
        - Le token doit exister
        - Le token ne doit pas être expiré (30 minutes)
        - Le token ne doit pas avoir déjà été utilisé
        """
        # Récupérer le token
        token_obj = await self.crud_token.obtenir_par_token(donnees.token)

        if not token_obj:
            raise RequeteInvalide(
                detail="Lien de réinitialisation invalide ou expiré"
            )

        # Vérifier que le token est encore valide
        if not token_obj.est_valide:
            if token_obj.utilise:
                raise RequeteInvalide(
                    detail="Ce lien a déjà été utilisé. "
                           "Demandez un nouveau lien de réinitialisation."
                )
            raise RequeteInvalide(
                detail="Ce lien a expiré (valable 30 minutes). "
                       "Demandez un nouveau lien de réinitialisation."
            )

        # Récupérer l'utilisateur
        utilisateur = await self.crud_user.obtenir_par_id(token_obj.utilisateur_id)

        if not utilisateur or not utilisateur.est_actif:
            raise RequeteInvalide(
                detail="Lien de réinitialisation invalide"
            )

        # Hasher et sauvegarder le nouveau mot de passe
        nouveau_hash = hacher_mot_de_passe(donnees.nouveau_mot_de_passe)
        await self.crud_user.mettre_a_jour_mot_de_passe(
            utilisateur.id, nouveau_hash
        )

        # Marquer le token comme utilisé
        await self.crud_token.marquer_utilise(token_obj.id)

        # Invalider TOUS les jetons JWT existants — déconnecter les sessions actives
        # (En production : ajouter le token à une blacklist Redis)

        return ReponseSimple(
            succes=True,
            message="Mot de passe réinitialisé avec succès. "
                    "Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.",
        )