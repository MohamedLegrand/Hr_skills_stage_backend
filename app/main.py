"""
Chemin : Hr-skills-stage-backend/app/main.py
---------------------------------------------
Point d'entrée principal de l'application FastAPI HR-Skills Stage.

Lancement :
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Auteur : TAKADJIO Mohamed — Chef UAT
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import obtenir_parametres
from app.database.connection import moteur
from app.database.session import fabrique_session
from app.middleware.cors import configurer_cors
from app.middleware.logging import configurer_journalisation
from app.middleware.error_handler import configurer_gestionnaires_erreurs
from app.middleware.rate_limiter import configurer_limite_debit
from app.shared.constants import NOM_PROJET, VERSION_API, DESCRIPTION_API
from app.utils.file_upload import initialiser_dossiers_uploads, DOSSIER_UPLOADS

# ── Import des modèles — découverte Alembic ───────────────────
import app.modules.auth.models           # noqa: F401
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

# ── Import des routers ────────────────────────────────────────
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
    - Démarrage : vérifie la connexion BDD sans bloquer si indisponible
    - Arrêt     : ferme proprement le moteur de connexion
    """
    # Initialisation des dossiers uploads en premier
    # (ne dépend pas de la BDD)
    initialiser_dossiers_uploads()

    logger.info("=" * 55)
    logger.info(f"  {NOM_PROJET} v{VERSION_API}")
    logger.info(f"  Environnement : {parametres.ENVIRONNEMENT.upper()}")
    logger.info("=" * 55)

    # Test de connexion BDD — ne bloque PAS le démarrage si indisponible
    # pool_pre_ping=True dans connection.py gère la reconnexion automatique
    try:
        async with moteur.connect() as connexion:
            resultat = await connexion.execute(text("SELECT current_database()"))
            nom_base = resultat.scalar()
        logger.info(f"✓ Base de données connectée : {nom_base}")
    except Exception as e:
        logger.warning(
            f"⚠ Base de données inaccessible au démarrage : {e}\n"
            f"  L'API démarre quand même — reconnexion automatique à chaque requête."
        )
        # Ne PAS faire raise — l'app démarre quand même
        # pool_pre_ping gère la reconnexion automatiquement

    logger.info("✓ Dossiers uploads initialisés")
    logger.info("✓ Application démarrée avec succès")
    logger.info("✓ Documentation : http://localhost:8000/docs")
    logger.info("=" * 55)

    yield  # ← L'application tourne ici

    # ── ARRÊT ─────────────────────────────────
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
        "name":  "TAKADJIO Mohamed — Developpeur Full Stack",
        "email": "takadjio@hr-skills.cm",
    },
    license_info={"name": "HR-Skills SARL — Usage interne"},
)

# ── Fichiers statiques — servir /uploads/ ─────────────────────
# check_dir=False évite le crash si le dossier n'existe pas encore
app.mount(
    "/uploads",
    StaticFiles(directory=str(DOSSIER_UPLOADS), check_dir=False),
    name="uploads",
)

# ─────────────────────────────────────────────
# MIDDLEWARES
# Ordre : le dernier ajouté s'exécute en premier
# ─────────────────────────────────────────────
configurer_gestionnaires_erreurs(app)   # 1. Erreurs globales
configurer_limite_debit(app)            # 2. Rate limiting
configurer_journalisation(app)          # 3. Logs requêtes
configurer_cors(app)                    # 4. CORS — exécuté en premier


# ─────────────────────────────────────────────
# ROUTERS MÉTIER
# ─────────────────────────────────────────────

app.include_router(routeur_auth)          # /api/v1/auth
app.include_router(routeur_utilisateur)   # /api/v1/utilisateurs
app.include_router(routeur_admin)         # /api/v1/admin
app.include_router(routeur_stagiaire)     # /api/v1/stagiaire
app.include_router(routeur_encadreur)     # /api/v1/encadreur
app.include_router(routeur_offre)         # /api/v1/offres-stage
app.include_router(routeur_inscription)   # /api/v1/inscriptions
app.include_router(routeur_document)      # /api/v1/documents
app.include_router(routeur_paiement)      # /api/v1/paiements
app.include_router(routeur_presence)      # /api/v1/presences
app.include_router(routeur_evaluation)    # /api/v1/evaluations
app.include_router(routeur_notification)  # /api/v1/notifications
app.include_router(routeur_convention)    # /api/v1/conventions
app.include_router(routeur_rapport)       # /api/v1/rapports
app.include_router(routeur_audit)         # /api/v1/audit


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