"""
Chemin : Hr-skills-stage-backend/app/modules/notification/router.py
Préfixe : /api/v1/notifications
"""
from fastapi import APIRouter, Depends, Query, status
from app.modules.notification.schemas import (
    EnvoiGroupe,
    SortieNotification,
)
from app.modules.notification.service import ServiceNotification
from app.core.dependencies import (
    SessionDB,
    obtenir_utilisateur_courant,
    exiger_role,
)
from app.modules.user.models import Utilisateur
from app.shared.enums import RoleEnum
from app.shared.constants import PREFIXE_NOTIFICATIONS

routeur = APIRouter(
    prefix=PREFIXE_NOTIFICATIONS,
    tags=["Notifications"],
)


@routeur.get(
    "/",
    response_model=list[SortieNotification],
    summary="Mes notifications",
)
async def mes_notifications(
    session: SessionDB,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_courant),
    non_lues_seulement: bool = Query(False),
) -> list[SortieNotification]:
    return await ServiceNotification(session).lister(
        utilisateur.id, non_lues_seulement
    )


@routeur.get(
    "/non-lues/count",
    summary="Nombre de notifications non lues",
)
async def compter_non_lues(
    session: SessionDB,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_courant),
) -> dict:
    count = await ServiceNotification(session).compter_non_lues(utilisateur.id)
    return {"non_lues": count}


@routeur.patch(
    "/{notif_id}/lire",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marquer une notification comme lue",
)
async def marquer_lu(
    notif_id: str,
    session: SessionDB,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_courant),
) -> None:
    await ServiceNotification(session).marquer_lu(notif_id)


@routeur.patch(
    "/tout-lire",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Tout marquer comme lu",
)
async def tout_marquer_lu(
    session: SessionDB,
    utilisateur: Utilisateur = Depends(obtenir_utilisateur_courant),
) -> None:
    await ServiceNotification(session).tout_marquer_lu(utilisateur.id)


@routeur.post(
    "/envoyer-groupe",
    summary="Envoi groupé",
    dependencies=[Depends(exiger_role(RoleEnum.ADMIN))],
)
async def envoyer_groupe(
    donnees: EnvoiGroupe,
    session: SessionDB,
) -> dict:
    count = await ServiceNotification(session).envoyer_groupe(donnees)
    return {"envoyes": count}