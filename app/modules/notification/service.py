"""
Chemin : Hr-skills-stage-backend/app/modules/notification/service.py
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.notification.crud import CrudNotification
from app.modules.notification.schemas import CreationNotification, EnvoiGroupe, SortieNotification
from app.modules.notification.models import Notification
from app.core.exceptions import NonTrouve


class ServiceNotification:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud    = CrudNotification(session)

    async def envoyer(self, donnees: CreationNotification) -> Notification:
        return await self.crud.creer(donnees.model_dump())

    async def envoyer_groupe(self, donnees: EnvoiGroupe) -> int:
        count = 0
        for uid in donnees.utilisateur_ids:
            await self.crud.creer({
                "utilisateur_id": uid, "titre": donnees.titre,
                "message": donnees.message, "type_notif": donnees.type_notif, "lien": donnees.lien,
            })
            count += 1
        return count

    async def lister(self, utilisateur_id: str, non_lues_seulement=False) -> list[SortieNotification]:
        notifs = await self.crud.lister_par_utilisateur(utilisateur_id, non_lues_seulement)
        return [SortieNotification.model_validate(n) for n in notifs]

    async def marquer_lu(self, notif_id: str) -> None:
        n = await self.crud.obtenir_par_id(notif_id)
        if not n:
            raise NonTrouve("Notification")
        await self.crud.marquer_lu(notif_id)

    async def tout_marquer_lu(self, utilisateur_id: str) -> None:
        await self.crud.tout_marquer_lu(utilisateur_id)

    async def compter_non_lues(self, utilisateur_id: str) -> int:
        return await self.crud.compter_non_lues(utilisateur_id)