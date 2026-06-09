"""
Chemin : Hr-skills-stage-backend/app/modules/notification/schemas.py
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.shared.enums import TypeNotification


class CreationNotification(BaseModel):
    utilisateur_id: str
    titre:          str
    message:        str
    type_notif:     TypeNotification = TypeNotification.INFO
    lien:           Optional[str]    = None


class EnvoiGroupe(BaseModel):
    utilisateur_ids: list[str]
    titre:           str
    message:         str
    type_notif:      TypeNotification = TypeNotification.INFO
    lien:            Optional[str]    = None


class SortieNotification(BaseModel):
    id:             str
    utilisateur_id: str
    titre:          str
    message:        str
    type_notif:     TypeNotification
    lien:           Optional[str]
    lu:             bool
    lu_le:          Optional[datetime]
    cree_le:        datetime

    model_config = {"from_attributes": True}