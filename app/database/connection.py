"""
Chemin : Hr-skills-stage-backend/app/database/connection.py
------------------------------------------------------------
Création du moteur de connexion SQLAlchemy async
vers la base de données PostgreSQL / Supabase.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import NullPool

from app.core.config import obtenir_parametres

parametres = obtenir_parametres()


def creer_moteur() -> AsyncEngine:
    """
    Crée et retourne le moteur SQLAlchemy asynchrone.

    - En production  : pool de connexions standard
    - En test        : NullPool pour éviter les conflits entre tests
    """
    options = {
        "echo": parametres.DB_ECHO_SQL,
        "future": True,
    }

    # NullPool en mode test pour éviter les conflits de transactions
    if parametres.ENVIRONNEMENT == "test":
        options["poolclass"] = NullPool
    else:
        options["pool_pre_ping"] = True   # Vérifie la connexion avant usage
        options["pool_size"] = 10          # Connexions simultanées max
        options["max_overflow"] = 20       # Connexions supplémentaires autorisées
        options["pool_recycle"] = 3600     # Recycle les connexions après 1h

    return create_async_engine(parametres.DATABASE_URL, **options)


# Instance unique du moteur partagée dans tout le projet
moteur: AsyncEngine = creer_moteur()