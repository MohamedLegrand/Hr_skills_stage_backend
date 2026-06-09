import os
import uuid
import logging
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

logger = logging.getLogger("hr_skills")

UPLOAD_DIR = "uploads"


async def upload_fichier(fichier: UploadFile, dossier: str = "documents") -> str:
    """
    Upload un fichier localement (dev) ou vers Supabase Storage (prod).
    Retourne l'URL d'accès au fichier.
    """
    if settings.APP_ENV == "production" and settings.SUPABASE_URL:
        return await _upload_supabase(fichier, dossier)
    return await _upload_local(fichier, dossier)


async def _upload_local(fichier: UploadFile, dossier: str) -> str:
    """Sauvegarde le fichier localement dans uploads/."""
    try:
        ext = os.path.splitext(fichier.filename or "fichier")[1]
        nom_unique = f"{uuid.uuid4()}{ext}"
        chemin_dossier = os.path.join(UPLOAD_DIR, dossier)
        os.makedirs(chemin_dossier, exist_ok=True)
        chemin_fichier = os.path.join(chemin_dossier, nom_unique)

        contenu = await fichier.read()
        async with aiofiles.open(chemin_fichier, "wb") as f:
            await f.write(contenu)

        return f"/uploads/{dossier}/{nom_unique}"
    except Exception as e:
        logger.error(f"Erreur upload local : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'enregistrement du fichier",
        )


async def _upload_supabase(fichier: UploadFile, dossier: str) -> str:
    """Upload vers Supabase Storage via l'API REST."""
    import httpx

    try:
        ext = os.path.splitext(fichier.filename or "fichier")[1]
        nom_unique = f"{dossier}/{uuid.uuid4()}{ext}"
        contenu = await fichier.read()

        url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{nom_unique}"
        headers = {
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": fichier.content_type or "application/octet-stream",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, content=contenu, headers=headers)
            resp.raise_for_status()

        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{nom_unique}"

    except Exception as e:
        logger.error(f"Erreur upload Supabase : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'upload vers le stockage",
        )
