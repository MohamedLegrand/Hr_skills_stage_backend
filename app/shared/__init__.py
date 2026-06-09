"""
shared/ — Code partagé entre tous les modules HR-Skills Stage
"""
from .enums import (
    RoleEnum,
    StatutInscription,
    StatutDocument,
    TypeDocument,
    StatutPaiement,
    ModePaiement,
    StatutPresence,
    StatutOffre,
    TypeNotification,
    TypeRapport,
    MoisEvaluation,
)

__all__ = [
    "RoleEnum",
    "StatutInscription",
    "StatutDocument",
    "TypeDocument",
    "StatutPaiement",
    "ModePaiement",
    "StatutPresence",
    "StatutOffre",
    "TypeNotification",
    "TypeRapport",
    "MoisEvaluation",
]