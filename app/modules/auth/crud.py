"""
Chemin : Hr-skills-stage-backend/app/modules/auth/crud.py
----------------------------------------------------------
Opérations BDD pour les tokens de réinitialisation de mot de passe.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import TokenReinitialisation


DUREE_TOKEN_MINUTES = 30


class CrudTokenReinitialisation:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def creer_token(self, utilisateur_id: str) -> TokenReinitialisation:
        """
        Génère un token sécurisé de 64 caractères hex.
        Invalide automatiquement les anciens tokens de cet utilisateur.
        """
        # Invalider les anciens tokens de cet utilisateur
        await self.invalider_tokens_utilisateur(utilisateur_id)

        token = secrets.token_urlsafe(48)   # 64 caractères URL-safe

        entree = TokenReinitialisation(
            utilisateur_id=utilisateur_id,
            token=token,
            expire_le=datetime.now(timezone.utc) + timedelta(minutes=DUREE_TOKEN_MINUTES),
        )
        self.session.add(entree)
        await self.session.flush()
        await self.session.refresh(entree)
        return entree

    async def obtenir_par_token(self, token: str) -> Optional[TokenReinitialisation]:
        """Retourne un token par sa valeur ou None s'il n'existe pas."""
        r = await self.session.execute(
            select(TokenReinitialisation).where(
                TokenReinitialisation.token == token
            )
        )
        return r.scalar_one_or_none()

    async def marquer_utilise(self, token_id: str) -> None:
        """Marque le token comme utilisé — il ne peut plus être réutilisé."""
        await self.session.execute(
            update(TokenReinitialisation)
            .where(TokenReinitialisation.id == token_id)
            .values(utilise=True)
        )
        await self.session.flush()

    async def invalider_tokens_utilisateur(self, utilisateur_id: str) -> None:
        """Invalide tous les tokens actifs d'un utilisateur."""
        await self.session.execute(
            update(TokenReinitialisation)
            .where(
                TokenReinitialisation.utilisateur_id == utilisateur_id,
                TokenReinitialisation.utilise == False,
            )
            .values(utilise=True)
        )
        await self.session.flush()