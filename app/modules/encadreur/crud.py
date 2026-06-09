"""
Chemin : Hr-skills-stage-backend/app/modules/encadreur/crud.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
# Le module encadreur utilise directement CrudInscription et CrudEvaluation
# Pas de table dédiée — les encadreurs sont dans la table utilisateurs