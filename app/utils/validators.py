import re
import os
from fastapi import HTTPException, status, UploadFile
from app.shared.constants import TAILLE_FICHIER_MAX_MB, EXTENSIONS_AUTORISEES

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
TEL_REGEX = re.compile(r"^\+?[0-9]{8,15}$")


def valider_email(email: str) -> str:
    if not EMAIL_REGEX.match(email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Email invalide : {email}",
        )
    return email.lower()


def valider_telephone(telephone: str) -> str:
    if not TEL_REGEX.match(telephone):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Numéro de téléphone invalide : {telephone}",
        )
    return telephone


def valider_fichier(fichier: UploadFile) -> UploadFile:
    ext = os.path.splitext(fichier.filename or "")[1].lower()
    if ext not in EXTENSIONS_AUTORISEES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Extension non autorisée : {ext}. Autorisées : {EXTENSIONS_AUTORISEES}",
        )
    return fichier


def valider_note(note: float) -> float:
    if not (0.0 <= note <= 20.0):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La note doit être comprise entre 0 et 20",
        )
    return note
