"""
Chemin : Hr-skills-stage-backend/app/modules/encadreur/service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.encadreur.schemas import TableauBordEncadreur
from app.modules.enrollment.crud import CrudInscription
from app.modules.evaluation.crud import CrudEvaluation
from app.modules.enrollment.schemas import SortieInscription
from app.shared.enums import StatutInscription


class ServiceEncadreur:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def tableau_bord(self, encadreur_id: str) -> TableauBordEncadreur:
        inscriptions, total = await CrudInscription(self.session).lister(encadreur_id=encadreur_id)
        en_cours = [i for i in inscriptions if i.statut == StatutInscription.EN_COURS]

        # Compter les évaluations saisies
        total_evals = 0
        for i in inscriptions:
            evals = await CrudEvaluation(self.session).lister_par_inscription(i.id)
            total_evals += len(evals)

        return TableauBordEncadreur(
            total_stagiaires=total,
            stages_en_cours=len(en_cours),
            evaluations_saisies=total_evals,
            inscriptions=[SortieInscription.model_validate(i) for i in inscriptions],
        )