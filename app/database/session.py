"""
Chemin : Hr-skills-stage-backend/app/database/session.py
---------------------------------------------------------
Factory de sessions SQLAlchemy asynchrones.
Fournit la dépendance obtenir_session() utilisée
dans tous les routers via Depends().

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.database.connection import moteur


# Factory de sessions asynchrones
fabrique_session = async_sessionmaker(
    bind=moteur,
    class_=AsyncSession,
    expire_on_commit=False,   # Les objets restent accessibles après commit
    autocommit=False,
    autoflush=False,
)


async def obtenir_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dépendance FastAPI qui fournit une session de base de données.

    - Ouvre une session à chaque requête HTTP
    - Effectue le commit automatique si aucune erreur
    - Effectue le rollback en cas d'exception
    - Ferme la session dans tous les cas (finally)

    Utilisation dans un router :
        from app.database.session import obtenir_session
        from sqlalchemy.ext.asyncio import AsyncSession
        from fastapi import Depends

        @router.get("/exemple")
        async def exemple(session: AsyncSession = Depends(obtenir_session)):
            ...

    Ou via le raccourci depuis core/dependencies.py :
        async def exemple(session: SessionDB):
            ...
    """
    async with fabrique_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def obtenir_session_test() -> AsyncGenerator[AsyncSession, None]:
    """
    Session dédiée aux tests — sans commit automatique.
    Chaque test repart d'un état propre grâce au rollback final.

    Utilisation dans conftest.py :
        @pytest.fixture
        async def session(app):
            async for s in obtenir_session_test():
                yield s
    """
    async with fabrique_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()