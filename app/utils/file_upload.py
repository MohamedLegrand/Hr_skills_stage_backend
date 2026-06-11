"""
Chemin : Hr-skills-stage-backend/app/utils/file_upload.py
----------------------------------------------------------
Gestion du stockage local de fichiers sous uploads/{bucket}/{chemin}.
Toutes les opérations I/O sont asynchrones via aiofiles.
Aucun appel Supabase ou cloud — stockage disque uniquement.
"""

import logging
import os
from pathlib import Path

import aiofiles
import aiofiles.os

from app.core.config import parametres

logger = logging.getLogger("hr_skills")

# ──────────────────────────────────────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────────────────────────────────────

# Racine du projet : Hr-skills-stage-backend/
RACINE_PROJET: Path = Path(__file__).parents[2]

# Répertoire de stockage des fichiers
DOSSIER_UPLOADS: Path = RACINE_PROJET / "uploads"

# Buckets autorisés — cohérent avec app/shared/constants.py
BUCKETS_AUTORISES: frozenset[str] = frozenset({
    "documents-stagiaires",
    "conventions-stage",
    "rapports-attestations",
    "recus-paiements",
    "photos-profils",
})


# ──────────────────────────────────────────────────────────────────────────────
# Helpers internes
# ──────────────────────────────────────────────────────────────────────────────

def _valider_bucket(bucket: str) -> None:
    """Lève ValueError si le bucket n'est pas dans la liste autorisée."""
    if bucket not in BUCKETS_AUTORISES:
        raise ValueError(
            f"Bucket invalide : '{bucket}'. "
            f"Buckets autorisés : {sorted(BUCKETS_AUTORISES)}"
        )


def _chemin_disque(chemin: str, bucket: str) -> Path:
    """Retourne le chemin absolu sur le disque pour un fichier donné."""
    return DOSSIER_UPLOADS / bucket / chemin


def _url_locale(chemin: str, bucket: str) -> str:
    """Retourne l'URL d'accès publique au fichier (servie par FastAPI StaticFiles)."""
    # Normalise les séparateurs Windows en slash URL
    chemin_normalise = chemin.replace("\\", "/")
    return f"/uploads/{bucket}/{chemin_normalise}"


# ──────────────────────────────────────────────────────────────────────────────
# API publique
# ──────────────────────────────────────────────────────────────────────────────

async def televerser_fichier(
    contenu: bytes,
    chemin: str,
    bucket: str,
) -> str:
    """
    Sauvegarde ``contenu`` dans uploads/{bucket}/{chemin}.

    - Crée les sous-dossiers manquants automatiquement.
    - Retourne l'URL locale d'accès au fichier ( /uploads/{bucket}/{chemin} ).
    - Lève ValueError si le bucket n'est pas autorisé.
    - Lève OSError si l'écriture échoue (propagée à l'appelant).

    Paramètres
    ----------
    contenu : bytes
        Contenu binaire du fichier à écrire.
    chemin : str
        Chemin relatif dans le bucket, ex. ``"2024/01/cv_dupont.pdf"``.
    bucket : str
        Nom du bucket de destination.
    """
    _valider_bucket(bucket)

    destination = _chemin_disque(chemin, bucket)
    dossier_parent = destination.parent

    # Création asynchrone du dossier si nécessaire
    await aiofiles.os.makedirs(str(dossier_parent), exist_ok=True)

    async with aiofiles.open(destination, "wb") as f:
        await f.write(contenu)

    url = _url_locale(chemin, bucket)
    logger.info(
        "Fichier téléversé : bucket=%s chemin=%s taille=%d octets",
        bucket, chemin, len(contenu),
    )
    return url


async def supprimer_fichier(chemin: str, bucket: str) -> bool:
    """
    Supprime uploads/{bucket}/{chemin} du disque.

    - Retourne True si la suppression réussit.
    - Retourne True si le fichier n'existe pas (idempotent).
    - Retourne False en cas d'erreur inattendue (loggée).
    - Lève ValueError si le bucket n'est pas autorisé.
    """
    _valider_bucket(bucket)

    cible = _chemin_disque(chemin, bucket)

    try:
        await aiofiles.os.remove(str(cible))
        logger.info("Fichier supprimé : bucket=%s chemin=%s", bucket, chemin)
        return True

    except FileNotFoundError:
        logger.warning(
            "Suppression ignorée — fichier introuvable : bucket=%s chemin=%s",
            bucket, chemin,
        )
        return True  # déjà absent → opération considérée réussie

    except PermissionError as exc:
        logger.error(
            "Permission refusée pour supprimer bucket=%s chemin=%s : %s",
            bucket, chemin, exc,
        )
        return False

    except OSError as exc:
        logger.error(
            "Erreur OS lors de la suppression bucket=%s chemin=%s : %s",
            bucket, chemin, exc,
        )
        return False


def obtenir_url_fichier(chemin: str, bucket: str) -> str:
    """
    Retourne l'URL d'accès publique au fichier sans I/O.

    - Lève ValueError si le bucket n'est pas autorisé.
    - Ne vérifie pas l'existence du fichier sur le disque.
    """
    _valider_bucket(bucket)
    return _url_locale(chemin, bucket)


async def lire_fichier(chemin: str, bucket: str) -> bytes:
    """
    Lit et retourne le contenu binaire de uploads/{bucket}/{chemin}.

    - Lève ValueError si le bucket n'est pas autorisé.
    - Lève FileNotFoundError si le fichier est absent.
    - Lève OSError pour toute autre erreur de lecture.
    """
    _valider_bucket(bucket)

    source = _chemin_disque(chemin, bucket)

    async with aiofiles.open(source, "rb") as f:
        contenu = await f.read()

    logger.debug(
        "Fichier lu : bucket=%s chemin=%s taille=%d octets",
        bucket, chemin, len(contenu),
    )
    return contenu


# ──────────────────────────────────────────────────────────────────────────────
# Initialisation au démarrage
# ──────────────────────────────────────────────────────────────────────────────

def initialiser_dossiers_uploads() -> None:
    """
    Crée la structure de dossiers uploads/ au démarrage de l'application.
    Appelée depuis le lifespan de main.py.

    uploads/
    ├── documents-stagiaires/
    ├── conventions-stage/
    ├── rapports-attestations/
    ├── recus-paiements/
    └── photos-profils/
    """
    for bucket in BUCKETS_AUTORISES:
        dossier = DOSSIER_UPLOADS / bucket
        dossier.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Dossiers uploads initialisés dans : %s",
        DOSSIER_UPLOADS,
    )
