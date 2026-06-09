"""
shared/enums.py
---------------
Tous les enums du projet HR-Skills Stage.
Utilisés dans les modèles SQLAlchemy, les schémas Pydantic et les services.

Auteur : TAKADJIO Mohamed — Chef UAT
"""

from enum import Enum


# ─────────────────────────────────────────────
# RÔLES UTILISATEUR
# ─────────────────────────────────────────────
class RoleEnum(str, Enum):
    ADMIN      = "admin"
    ENCADREUR  = "encadreur"
    STAGIAIRE  = "stagiaire"


# ─────────────────────────────────────────────
# STATUTS D'INSCRIPTION
# ─────────────────────────────────────────────
class StatutInscription(str, Enum):
    EN_ATTENTE = "en_attente"   # Candidature soumise, non traitée
    VALIDEE    = "validee"      # Acceptée par l'admin
    REFUSEE    = "refusee"      # Rejetée par l'admin
    EN_COURS   = "en_cours"     # Stage en cours d'exécution
    TERMINEE   = "terminee"     # Stage terminé et clôturé


# ─────────────────────────────────────────────
# STATUTS DE DOCUMENT
# ─────────────────────────────────────────────
class StatutDocument(str, Enum):
    EN_ATTENTE = "en_attente"   # Déposé, en attente de validation
    VALIDE     = "valide"       # Validé par admin ou encadreur
    REJETE     = "rejete"       # Rejeté avec motif obligatoire


# ─────────────────────────────────────────────
# TYPES DE DOCUMENT
# ─────────────────────────────────────────────
class TypeDocument(str, Enum):
    CV              = "cv"
    LETTRE_MOTIV    = "lettre_motiv"
    CNI             = "cni"
    RELEVE_NOTES    = "releve_notes"
    CONVENTION      = "convention"
    RAPPORT_STAGE   = "rapport_stage"
    ATTESTATION_FIN = "attestation_fin"


# ─────────────────────────────────────────────
# STATUTS DE PAIEMENT
# ─────────────────────────────────────────────
class StatutPaiement(str, Enum):
    EN_ATTENTE = "en_attente"   # Initié, en attente de confirmation
    CONFIRME   = "confirme"     # Confirmé via webhook passerelle
    ECHOUE     = "echoue"       # Échec de la transaction
    REMBOURSE  = "rembourse"    # Remboursé


# ─────────────────────────────────────────────
# MODES DE PAIEMENT
# ─────────────────────────────────────────────
class ModePaiement(str, Enum):
    MTN_MOBILE_MONEY = "mtn_mobile_money"
    ORANGE_MONEY     = "orange_money"
    MOOV             = "moov"
    CARTE_BANCAIRE   = "carte_bancaire"
    VIREMENT         = "virement"
    AUTRE            = "autre"


# ─────────────────────────────────────────────
# STATUTS DE PRÉSENCE
# ─────────────────────────────────────────────
class StatutPresence(str, Enum):
    PRESENT   = "present"    # Stagiaire présent
    ABSENT    = "absent"     # Absent sans justification
    JUSTIFIE  = "justifie"   # Absent avec justification acceptée
    FERIE     = "ferie"      # Jour férié ou congé officiel


# ─────────────────────────────────────────────
# STATUTS D'OFFRE DE STAGE
# ─────────────────────────────────────────────
class StatutOffre(str, Enum):
    OUVERT   = "ouvert"    # Places disponibles
    COMPLET  = "complet"   # Plus de place disponible
    ARCHIVE  = "archive"   # Offre terminée ou désactivée


# ─────────────────────────────────────────────
# TYPES DE NOTIFICATION
# ─────────────────────────────────────────────
class TypeNotification(str, Enum):
    INFO          = "info"
    SUCCES        = "succes"
    AVERTISSEMENT = "avertissement"
    ERREUR        = "erreur"


# ─────────────────────────────────────────────
# TYPES DE RAPPORT
# ─────────────────────────────────────────────
class TypeRapport(str, Enum):
    RAPPORT_STAGE   = "rapport_stage"
    ATTESTATION_FIN = "attestation_fin"
    BILAN_MENSUEL   = "bilan_mensuel"
    EXPORT_CSV      = "export_csv"


# ─────────────────────────────────────────────
# MOIS D'ÉVALUATION
# ─────────────────────────────────────────────
class MoisEvaluation(int, Enum):
    PREMIER    = 1   # Premier mois de stage
    DEUXIEME   = 2   # Deuxième mois de stage
    TROISIEME  = 3   # Troisième mois de stage