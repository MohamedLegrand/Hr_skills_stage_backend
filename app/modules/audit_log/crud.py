"""
Chemin : Hr-skills-stage-backend/app/modules/audit_log/crud.py
---------------------------------------------------------------
Opérations BDD sur la table 'journaux_audit'.
Le journal est en écriture seule — pas de mise à jour, pas de suppression.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from typing import Optional
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit_log.models import JournalAudit


class CrudJournalAudit:
    """
    Classe CRUD pour le journal d'audit.

    Règle importante : le journal est IMMUABLE.
    On peut seulement créer et lire — jamais modifier ni supprimer.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ─────────────────────────────────────────
    # ÉCRITURE
    # ─────────────────────────────────────────

    async def enregistrer(self, donnees: dict) -> JournalAudit:
        """
        Enregistre une nouvelle entrée dans le journal d'audit.

        Utilisation dans un service :
            await CrudJournalAudit(session).enregistrer({
                "utilisateur_id": utilisateur.id,
                "action": "document.valide",
                "table_cible": "documents",
                "enregistrement_id": document.id,
                "nouvelles_valeurs": {"statut": "valide"},
                "adresse_ip": "127.0.0.1",
            })
        """
        entree = JournalAudit(**donnees)
        self.session.add(entree)
        await self.session.flush()
        await self.session.refresh(entree)
        return entree

    # ─────────────────────────────────────────
    # LECTURE
    # ─────────────────────────────────────────

    async def obtenir_par_id(self, journal_id: str) -> Optional[JournalAudit]:
        """Retourne une entrée du journal par son ID."""
        r = await self.session.execute(
            select(JournalAudit).where(JournalAudit.id == journal_id)
        )
        return r.scalar_one_or_none()

    async def lister(
        self,
        page:             int = 1,
        taille:           int = 50,
        utilisateur_id:   Optional[str]      = None,
        action:           Optional[str]      = None,
        table_cible:      Optional[str]      = None,
        enregistrement_id: Optional[str]     = None,
        date_debut:       Optional[datetime] = None,
        date_fin:         Optional[datetime] = None,
    ) -> tuple[list[JournalAudit], int]:
        """
        Retourne le journal d'audit paginé avec filtres optionnels.
        Trié du plus récent au plus ancien.
        """
        q  = select(JournalAudit)
        qt = select(func.count()).select_from(JournalAudit)

        # ── Filtres ──
        if utilisateur_id:
            q  = q.where(JournalAudit.utilisateur_id == utilisateur_id)
            qt = qt.where(JournalAudit.utilisateur_id == utilisateur_id)

        if action:
            # Recherche partielle — ex: "document" trouve "document.valide", "document.rejete"
            q  = q.where(JournalAudit.action.ilike(f"%{action}%"))
            qt = qt.where(JournalAudit.action.ilike(f"%{action}%"))

        if table_cible:
            q  = q.where(JournalAudit.table_cible == table_cible)
            qt = qt.where(JournalAudit.table_cible == table_cible)

        if enregistrement_id:
            q  = q.where(JournalAudit.enregistrement_id == enregistrement_id)
            qt = qt.where(JournalAudit.enregistrement_id == enregistrement_id)

        if date_debut:
            q  = q.where(JournalAudit.effectue_le >= date_debut)
            qt = qt.where(JournalAudit.effectue_le >= date_debut)

        if date_fin:
            q  = q.where(JournalAudit.effectue_le <= date_fin)
            qt = qt.where(JournalAudit.effectue_le <= date_fin)

        # Total
        total = (await self.session.execute(qt)).scalar()

        # Pagination — plus récent en premier
        decalage = (page - 1) * taille
        q = q.order_by(JournalAudit.effectue_le.desc()).offset(decalage).limit(taille)

        r = await self.session.execute(q)
        return r.scalars().all(), total

    async def lister_par_utilisateur(
        self,
        utilisateur_id: str,
        limite: int = 20,
    ) -> list[JournalAudit]:
        """Retourne les dernières actions d'un utilisateur spécifique."""
        r = await self.session.execute(
            select(JournalAudit)
            .where(JournalAudit.utilisateur_id == utilisateur_id)
            .order_by(JournalAudit.effectue_le.desc())
            .limit(limite)
        )
        return r.scalars().all()

    async def lister_par_enregistrement(
        self,
        table_cible:      str,
        enregistrement_id: str,
    ) -> list[JournalAudit]:
        """
        Retourne l'historique complet d'un enregistrement spécifique.
        Utile pour voir toutes les actions sur un document ou un paiement.
        """
        r = await self.session.execute(
            select(JournalAudit)
            .where(
                JournalAudit.table_cible      == table_cible,
                JournalAudit.enregistrement_id == enregistrement_id,
            )
            .order_by(JournalAudit.effectue_le.desc())
        )
        return r.scalars().all()

    async def compter_actions_par_type(self) -> list[dict]:
        """
        Retourne le nombre d'actions par type.
        Utile pour les statistiques du tableau de bord admin.
        """
        r = await self.session.execute(
            select(
                JournalAudit.action,
                func.count().label("total"),
            )
            .group_by(JournalAudit.action)
            .order_by(func.count().desc())
        )
        return [{"action": row.action, "total": row.total} for row in r]