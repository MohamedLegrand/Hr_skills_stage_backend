"""
Chemin : Hr-skills-stage-backend/app/shared/constants.py
"""

# ── Projet ────────────────────────────────────────────────────
NOM_PROJET       = "HR-Skills Stage API"
VERSION_API      = "1.0.0"
DESCRIPTION_API  = "Plateforme de gestion des stages académiques — HR-Skills SARL"
NOM_ENTREPRISE   = "HR-Skills SARL"
VILLE            = "Yaoundé, Cameroun"
CONTACT_EMAIL    = "contact@hr-skills.cm"

# ── Préfixes routes ───────────────────────────────────────────
PREFIXE_API          = "/api/v1"
PREFIXE_AUTH         = "/api/v1/auth"
PREFIXE_UTILISATEURS = "/api/v1/utilisateurs"
PREFIXE_ADMIN        = "/api/v1/admin"
PREFIXE_STAGIAIRE    = "/api/v1/stagiaire"
PREFIXE_ENCADREUR    = "/api/v1/encadreur"
PREFIXE_OFFRES       = "/api/v1/offres-stage"
PREFIXE_INSCRIPTIONS = "/api/v1/inscriptions"
PREFIXE_DOCUMENTS    = "/api/v1/documents"
PREFIXE_PAIEMENTS    = "/api/v1/paiements"
PREFIXE_PRESENCES    = "/api/v1/presences"
PREFIXE_EVALUATIONS  = "/api/v1/evaluations"
PREFIXE_NOTIFICATIONS= "/api/v1/notifications"
PREFIXE_CONVENTIONS  = "/api/v1/conventions"
PREFIXE_RAPPORTS     = "/api/v1/rapports"
PREFIXE_AUDIT        = "/api/v1/audit"

# ── JWT ───────────────────────────────────────────────────────
DUREE_JETON_ACCES_MINUTES   = 60 * 24
DUREE_JETON_RAFRAICH_JOURS  = 7
ALGORITHME_JWT               = "HS256"
TYPE_JETON                   = "Bearer"

# ── Bcrypt ────────────────────────────────────────────────────
ROUNDS_BCRYPT = 12

# ── Fichiers ──────────────────────────────────────────────────
TAILLE_MAX_FICHIER_MO        = 5
TAILLE_MAX_FICHIER_OCTETS    = 5 * 1024 * 1024
TAILLE_FICHIER_MAX_MB        = 5                      # alias utilisé dans validators.py
TYPES_MIME_AUTORISES         = ["application/pdf"]
EXTENSIONS_AUTORISEES        = [".pdf"]               # utilisé dans validators.py
EXTENSION_AUTORISEE          = ".pdf"
DUREE_URL_SIGNEE_SECONDES    = 3600

# ── Buckets Supabase ──────────────────────────────────────────
BUCKET_DOCUMENTS    = "documents-stagiaires"
BUCKET_CONVENTIONS  = "conventions-stage"
BUCKET_RAPPORTS     = "rapports-attestations"
BUCKET_RECUS        = "recus-paiements"
BUCKET_PHOTOS       = "photos-profils"

# ── Pagination ────────────────────────────────────────────────
PAGE_PAR_DEFAUT        = 1
TAILLE_PAGE_DEFAUT     = 20
TAILLE_PAGE_MAX        = 100

# ── Stage ─────────────────────────────────────────────────────
DUREE_STAGE_MOIS      = 3
NB_EVALUATIONS_TOTAL  = 3
NOTE_MIN              = 0
NOTE_MAX              = 20
NOTE_PASSAGE          = 10

# ── Paiement ──────────────────────────────────────────────────
DEVISE_DEFAUT         = "XAF"
MONTANT_FRAIS_STAGE   = 50000
TIMEOUT_PAIEMENT_MIN  = 30

# ── Emails ───────────────────────────────────────────────────
EXPEDITEUR_NOM    = "HR-Skills SARL"
EXPEDITEUR_EMAIL  = "noreply@hr-skills.cm"

SUJET_INSCRIPTION_VALIDEE  = "Votre inscription au stage a été validée — HR-Skills"
SUJET_INSCRIPTION_REFUSEE  = "Résultat de votre candidature — HR-Skills"
SUJET_DOCUMENT_VALIDE      = "Document validé — HR-Skills Stage"
SUJET_DOCUMENT_REJETE      = "Document rejeté — action requise — HR-Skills Stage"
SUJET_PAIEMENT_CONFIRME    = "Confirmation de paiement — HR-Skills Stage"
SUJET_CONVENTION_PRETE     = "Votre convention de stage est disponible — HR-Skills"
SUJET_ATTESTATION_PRETE    = "Votre attestation de fin de stage — HR-Skills"

# ── Messages d'erreur ─────────────────────────────────────────
MSG_NON_AUTORISE           = "Authentification requise"
MSG_ACCES_INTERDIT         = "Vous n'avez pas les droits nécessaires pour cette action"
MSG_NON_TROUVE             = "Ressource introuvable"
MSG_VALIDATION_ECHOUEE     = "Les données soumises sont invalides"
MSG_SERVEUR_ERREUR         = "Une erreur interne s'est produite"
MSG_EMAIL_DEJA_UTILISE     = "Cette adresse email est déjà associée à un compte"
MSG_IDENTIFIANTS_INVALIDES = "Email ou mot de passe incorrect"
MSG_COMPTE_INACTIF         = "Ce compte a été désactivé"
MSG_FICHIER_TROP_GRAND     = f"Le fichier dépasse la taille maximale autorisée ({TAILLE_MAX_FICHIER_MO} Mo)"
MSG_TYPE_FICHIER_INVALIDE  = "Seuls les fichiers PDF sont acceptés"
MSG_DOCUMENT_DEJA_SOUMIS   = "Un document de ce type a déjà été soumis pour cette inscription"
MSG_PAIEMENT_DEJA_CONFIRME = "Ce paiement a déjà été confirmé"
MSG_STAGE_COMPLET          = "Cette offre de stage ne dispose plus de places disponibles"
MSG_DEJA_INSCRIT           = "Vous êtes déjà inscrit à cette offre de stage"

# ── HTTP codes ────────────────────────────────────────────────
HTTP_200_OK          = 200
HTTP_201_CREE        = 201
HTTP_204_VIDE        = 204
HTTP_400_INVALIDE    = 400
HTTP_401_NON_AUTH    = 401
HTTP_403_INTERDIT    = 403
HTTP_404_INTROUVABLE = 404
HTTP_409_CONFLIT     = 409
HTTP_422_VALIDATION  = 422
HTTP_500_ERREUR      = 500

# ── Rate limiting ─────────────────────────────────────────────
LIMITE_REQUETES_MINUTE   = 100
LIMITE_CONNEXIONS_MINUTE = 5
LIMITE_UPLOAD_MINUTE     = 10

# ── Logging ───────────────────────────────────────────────────
FORMAT_LOG          = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
FICHIER_LOG         = "uvicorn.log"
FICHIER_LOG_ERREURS = "uvicorn_err.log"