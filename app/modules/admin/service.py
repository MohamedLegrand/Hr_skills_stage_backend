"""
Chemin : Hr-skills-stage-backend/app/modules/admin/service.py
"""
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.admin.schemas import TableauBordAdmin


class ServiceAdmin:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def tableau_bord(self) -> TableauBordAdmin:
        r = await self.session.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM utilisateurs WHERE role = 'stagiaire' AND est_actif = TRUE)   AS total_stagiaires,
                (SELECT COUNT(*) FROM inscriptions WHERE statut = 'en_attente')                      AS inscriptions_en_attente,
                (SELECT COUNT(*) FROM inscriptions WHERE statut = 'en_cours')                        AS stages_en_cours,
                (SELECT COUNT(*) FROM inscriptions WHERE statut = 'terminee')                        AS stages_termines,
                (SELECT COUNT(*) FROM documents WHERE statut = 'en_attente')                         AS documents_a_valider,
                (SELECT COUNT(*) FROM paiements WHERE statut = 'confirme')                           AS paiements_confirmes,
                (SELECT COALESCE(SUM(montant), 0) FROM paiements WHERE statut = 'confirme')          AS total_recettes,
                (SELECT COUNT(*) FROM offres_stage WHERE statut = 'ouvert')                          AS offres_ouvertes
        """))
        row = r.fetchone()
        return TableauBordAdmin(
            total_stagiaires=row.total_stagiaires,
            inscriptions_en_attente=row.inscriptions_en_attente,
            stages_en_cours=row.stages_en_cours,
            stages_termines=row.stages_termines,
            documents_a_valider=row.documents_a_valider,
            paiements_confirmes=row.paiements_confirmes,
            total_recettes=float(row.total_recettes),
            offres_ouvertes=row.offres_ouvertes,
        )