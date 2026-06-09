"""
Chemin : Hr-skills-stage-backend/app/modules/audit_log/service.py
-----------------------------------------------------------------
Logique métier du journal d'audit.
Ce service est appelé par tous les autres services pour
tracer automatiquement les actions importantes.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from typing import Optional, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit_log.crud import CrudJournalAudit
from app.modules.audit_log.models import JournalAudit
from app.modules.audit_log.schemas import (
    ListeJournalAudit,
    SortieJournalAudit,
    FiltresJournalAudit,
)
from app.core.exceptions import NonTrouve


# ─────────────────────────────────────────────
# ACTIONS STANDARDISÉES
# ─────────────────────────────────────────────
# Format : "module.action"
# Utiliser ces constantes dans tous les services
# pour garantir la cohérence des noms d'actions.

class Actions:
    # Utilisateur
    UTILISATEUR_CREE         = "utilisateur.cree"
    UTILISATEUR_CONNECTE     = "utilisateur.connecte"
    UTILISATEUR_DECONNECTE   = "utilisateur.deconnecte"
    UTILISATEUR_MIS_A_JOUR   = "utilisateur.mis_a_jour"
    UTILISATEUR_DESACTIVE    = "utilisateur.desactive"
    UTILISATEUR_ACTIVE       = "utilisateur.active"
    MOT_DE_PASSE_CHANGE      = "utilisateur.mdp_change"

    # Offre de stage
    OFFRE_CREEE              = "offre.creee"
    OFFRE_MODIFIEE           = "offre.modifiee"
    OFFRE_ARCHIVEE           = "offre.archivee"

    # Inscription
    INSCRIPTION_SOUMISE      = "inscription.soumise"
    INSCRIPTION_VALIDEE      = "inscription.validee"
    INSCRIPTION_REFUSEE      = "inscription.refusee"
    INSCRIPTION_TERMINEE     = "inscription.terminee"
    ENCADREUR_ASSIGNE        = "inscription.encadreur_assigne"

    # Document
    DOCUMENT_DEPOSE          = "document.depose"
    DOCUMENT_VALIDE          = "document.valide"
    DOCUMENT_REJETE          = "document.rejete"

    # Paiement
    PAIEMENT_INITIE          = "paiement.initie"
    PAIEMENT_CONFIRME        = "paiement.confirme"
    PAIEMENT_ECHOUE          = "paiement.echoue"

    # Présence
    PRESENCE_MARQUEE         = "presence.marquee"

    # Évaluation
    EVALUATION_CREEE         = "evaluation.creee"
    EVALUATION_MODIFIEE      = "evaluation.modifiee"

    # Convention
    CONVENTION_GENEREE       = "convention.generee"

    # Rapport / Attestation
    ATTESTATION_GENEREE      = "attestation.generee"
    RAPPORT_GENERE           = "rapport.genere"


class ServiceJournalAudit:
    """
    Service de gestion du journal d'audit.

    Utilisation dans un autre service :
        service_audit = ServiceJournalAudit(session)
        await service_audit.enregistrer(
            action=Actions.DOCUMENT_VALIDE,
            utilisateur_id=valideur.id,
            table_cible="documents",
            enregistrement_id=document.id,
            nouvelles_valeurs={"statut": "valide"},
            adresse_ip=requete.client.host,
        )
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudJournalAudit(session)

    # ─────────────────────────────────────────
    # ENREGISTREMENT D'UNE ACTION
    # ─────────────────────────────────────────

    async def enregistrer(
        self,
        action:            str,
        utilisateur_id:    Optional[str] = None,
        table_cible:       Optional[str] = None,
        enregistrement_id: Optional[str] = None,
        anciennes_valeurs: Optional[Any] = None,
        nouvelles_valeurs: Optional[Any] = None,
        adresse_ip:        Optional[str] = None,
    ) -> JournalAudit:
        """
        Enregistre une action dans le journal d'audit.
        Appelé dans les services après chaque opération importante.
        """
        return await self.crud.enregistrer({
            "utilisateur_id":    utilisateur_id,
            "action":            action,
            "table_cible":       table_cible,
            "enregistrement_id": enregistrement_id,
            "anciennes_valeurs": anciennes_valeurs,
            "nouvelles_valeurs": nouvelles_valeurs,
            "adresse_ip":        adresse_ip,
        })

    # ─────────────────────────────────────────
    # LECTURE
    # ─────────────────────────────────────────

    async def lister(
        self,
        page:    int = 1,
        taille:  int = 50,
        filtres: FiltresJournalAudit = None,
    ) -> ListeJournalAudit:
        """
        Retourne le journal paginé avec filtres optionnels.
        Réservé à l'administrateur.
        """
        kwargs = {}
        if filtres:
            kwargs = filtres.model_dump(exclude_none=True)

        journaux, total = await self.crud.lister(page=page, taille=taille, **kwargs)

        return ListeJournalAudit(
            total=total,
            page=page,
            taille_page=taille,
            journaux=[SortieJournalAudit.model_validate(j) for j in journaux],
        )

    async def obtenir_par_id(self, journal_id: str) -> JournalAudit:
        """Retourne une entrée du journal par son ID."""
        j = await self.crud.obtenir_par_id(journal_id)
        if not j:
            raise NonTrouve("Entrée du journal")
        return j

    async def historique_utilisateur(
        self,
        utilisateur_id: str,
        limite:         int = 20,
    ) -> list[SortieJournalAudit]:
        """Retourne les dernières actions d'un utilisateur."""
        journaux = await self.crud.lister_par_utilisateur(utilisateur_id, limite)
        return [SortieJournalAudit.model_validate(j) for j in journaux]

    async def historique_enregistrement(
        self,
        table_cible:       str,
        enregistrement_id: str,
    ) -> list[SortieJournalAudit]:
        """
        Retourne l'historique complet d'un enregistrement.
        Ex : toutes les actions sur le document avec cet ID.
        """
        journaux = await self.crud.lister_par_enregistrement(table_cible, enregistrement_id)
        return [SortieJournalAudit.model_validate(j) for j in journaux]

    async def statistiques_actions(self) -> list[dict]:
        """Retourne le nombre d'actions par type pour le tableau de bord."""
        return await self.crud.compter_actions_par_type()