"""
Chemin : Hr-skills-stage-backend/app/main.py
---------------------------------------------
Point d'entrée principal de l'application FastAPI HR-Skills Stage.

Lancement :
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Auteur : TAKADJIO Mohamed — Developpeur Full Stack
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import obtenir_parametres
from app.database.connection import moteur
from app.database.session import fabrique_session
from app.middleware.cors import configurer_cors
from app.middleware.logging import configurer_journalisation
from app.middleware.error_handler import configurer_gestionnaires_erreurs
from app.middleware.rate_limiter import configurer_limite_debit
from app.shared.constants import NOM_PROJET, VERSION_API, DESCRIPTION_API

# ─────────────────────────────────────────────
# IMPORT DES MODÈLES — découverte Alembic
# ─────────────────────────────────────────────
import app.modules.auth.models           # noqa: F401  ← AJOUTÉ (tokens_reinitialisation)
import app.modules.user.models           # noqa: F401
import app.modules.stage.models          # noqa: F401
import app.modules.enrollment.models     # noqa: F401
import app.modules.document.models       # noqa: F401
import app.modules.payment.models        # noqa: F401
import app.modules.attendance.models     # noqa: F401
import app.modules.evaluation.models     # noqa: F401
import app.modules.notification.models   # noqa: F401
import app.modules.convention.models     # noqa: F401
import app.modules.report.models         # noqa: F401
import app.modules.audit_log.models      # noqa: F401

# ─────────────────────────────────────────────
# IMPORT DES ROUTERS
# ─────────────────────────────────────────────
from app.modules.auth.router          import routeur as routeur_auth
from app.modules.user.router          import routeur as routeur_utilisateur
from app.modules.admin.router         import routeur as routeur_admin
from app.modules.student.router       import routeur as routeur_stagiaire
from app.modules.encadreur.router     import routeur as routeur_encadreur
from app.modules.stage.router         import routeur as routeur_offre
from app.modules.enrollment.router    import routeur as routeur_inscription
from app.modules.document.router      import routeur as routeur_document
from app.modules.payment.router       import routeur as routeur_paiement
from app.modules.attendance.router    import routeur as routeur_presence
from app.modules.evaluation.router    import routeur as routeur_evaluation
from app.modules.notification.router  import routeur as routeur_notification
from app.modules.convention.router    import routeur as routeur_convention
from app.modules.report.router        import routeur as routeur_rapport
from app.modules.audit_log.router     import routeur as routeur_audit

parametres = obtenir_parametres()
logger     = logging.getLogger("hr_skills")


# ─────────────────────────────────────────────
# CYCLE DE VIE — DÉMARRAGE / ARRÊT
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application.
    - Démarrage : vérifie la connexion à la base de données
    - Arrêt     : ferme proprement le moteur de connexion
    """
    # ── DÉMARRAGE ──────────────────────────────
    logger.info("=" * 55)
    logger.info(f"  {NOM_PROJET} v{VERSION_API}")
    logger.info(f"  Environnement : {parametres.ENVIRONNEMENT.upper()}")
    logger.info("=" * 55)

    try:
        async with moteur.connect() as connexion:
            resultat = await connexion.execute(text("SELECT current_database()"))
            nom_base = resultat.scalar()
        logger.info(f"✓ Base de données connectée : {nom_base}")
    except Exception as e:
        logger.error(f"✗ Échec de connexion BDD : {e}")
        raise

    logger.info("✓ Application démarrée avec succès")
    logger.info("✓ Documentation : http://localhost:8000/docs")
    logger.info("=" * 55)

    yield  # ← L'application tourne ici

    # ── ARRÊT ──────────────────────────────────
    logger.info("Arrêt de l'application en cours...")
    await moteur.dispose()
    logger.info("✓ Connexions BDD fermées proprement")


# ─────────────────────────────────────────────
# INSTANCE FASTAPI
# ─────────────────────────────────────────────

app = FastAPI(
    title=NOM_PROJET,
    version=VERSION_API,
    description=DESCRIPTION_API,
    lifespan=lifespan,
    docs_url="/docs"            if not parametres.est_production else None,
    redoc_url="/redoc"          if not parametres.est_production else None,
    openapi_url="/openapi.json" if not parametres.est_production else None,
    contact={
        "name":  "TAKADJIO Mohamed — Chef UAT",
        "email": "takadjio@hr-skills.cm",
    },
    license_info={
        "name": "HR-Skills SARL — Usage interne",
    },
)


# ─────────────────────────────────────────────
# MIDDLEWARES
# Ordre important : le dernier ajouté s'exécute en premier
# ─────────────────────────────────────────────

configurer_gestionnaires_erreurs(app)   # 1. Erreurs globales
configurer_limite_debit(app)            # 2. Rate limiting
configurer_journalisation(app)          # 3. Logs requêtes
configurer_cors(app)                    # 4. CORS — exécuté en premier


# ─────────────────────────────────────────────
# ROUTERS MÉTIER
# ─────────────────────────────────────────────

# ── Authentification ──────────────────────────
app.include_router(routeur_auth)

# ── Utilisateurs ──────────────────────────────
app.include_router(routeur_utilisateur)

# ── Administration ────────────────────────────
app.include_router(routeur_admin)

# ── Espaces dédiés ────────────────────────────
app.include_router(routeur_stagiaire)
app.include_router(routeur_encadreur)

# ── Offres de stage ───────────────────────────
app.include_router(routeur_offre)

# ── Inscriptions ──────────────────────────────
app.include_router(routeur_inscription)

# ── Documents ─────────────────────────────────
app.include_router(routeur_document)

# ── Paiements ─────────────────────────────────
app.include_router(routeur_paiement)

# ── Présences ─────────────────────────────────
app.include_router(routeur_presence)

# ── Évaluations ───────────────────────────────
app.include_router(routeur_evaluation)

# ── Notifications ─────────────────────────────
app.include_router(routeur_notification)

# ── Conventions ───────────────────────────────
app.include_router(routeur_convention)

# ── Rapports & Attestations ───────────────────
app.include_router(routeur_rapport)

# ── Journal d'audit ───────────────────────────
app.include_router(routeur_audit)


# ─────────────────────────────────────────────
# ENDPOINTS SYSTÈME
# ─────────────────────────────────────────────

@app.get(
    "/health",
    tags=["Système"],
    summary="État de l'application et de la base de données",
)
async def sante() -> JSONResponse:
    """
    Vérifie que l'API et PostgreSQL sont opérationnels.
    Accessible sans authentification.
    """
    try:
        async with fabrique_session() as session:
            resultat = await session.execute(
                text("SELECT current_database(), version()")
            )
            ligne      = resultat.fetchone()
            nom_base   = ligne[0]
            version_pg = ligne[1].split(",")[0]

        return JSONResponse(
            status_code=200,
            content={
                "succes":        True,
                "statut":        200,
                "application":   NOM_PROJET,
                "version":       VERSION_API,
                "environnement": parametres.ENVIRONNEMENT,
                "base_de_donnees": {
                    "nom":     nom_base,
                    "version": version_pg,
                    "statut":  "connectée",
                },
            },
        )

    except Exception as e:
        logger.error(f"Health check échoué : {e}")
        return JSONResponse(
            status_code=503,
            content={
                "succes":  False,
                "statut":  503,
                "message": "Base de données inaccessible",
                "base_de_donnees": {"statut": "déconnectée"},
            },
        )


@app.get(
    "/",
    tags=["Système"],
    summary="Accueil de l'API",
    include_in_schema=False,
)
async def accueil() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "message":       f"Bienvenue sur {NOM_PROJET}",
            "version":       VERSION_API,
            "documentation": "/docs",
            "sante":         "/health",
        },
    )