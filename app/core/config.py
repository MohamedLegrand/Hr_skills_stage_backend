"""
Chemin : Hr-skills-stage-backend/app/core/config.py
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
from functools import lru_cache


class Parametres(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────
    NOM_APP:        str = "HR-Skills Stage API"
    APP_NAME:       str = "HR-Skills Stage API"
    VERSION:        str = "1.0.0"
    ENVIRONNEMENT:  str = "development"
    APP_ENV:        str = "development"
    DEBUG:          bool = True

    # ── Frontend ──────────────────────────────────────────────
    FRONTEND_URL:   str = "http://localhost:3000"

    # ── Base de données PostgreSQL local ──────────────────────
    DATABASE_URL:      str = ""
    DATABASE_URL_SYNC: str = ""
    DB_ECHO_SQL:       bool = False

    # ── JWT ───────────────────────────────────────────────────
    SECRET_KEY:                    str  = "changeme_minimum_32_chars_secret_key!!"
    ALGORITHME_JWT:                str  = "HS256"
    ALGORITHM:                     str  = "HS256"
    DUREE_JETON_ACCES_MINUTES:     int  = 1440
    ACCESS_TOKEN_EXPIRE_MINUTES:   int  = 1440
    DUREE_JETON_RAFRAICH_JOURS:    int  = 7
    REFRESH_TOKEN_EXPIRE_DAYS:     int  = 7
    DUREE_JETON_REINIT_MINUTES:    int  = 30

    # ── Stockage local ────────────────────────────────────────
    UPLOAD_DIR:     str = "uploads"

    # ── SMTP ──────────────────────────────────────────────────
    SMTP_HOTE:          str  = "smtp.gmail.com"
    SMTP_HOST:          str  = "smtp.gmail.com"
    SMTP_PORT:          int  = 587
    SMTP_UTILISATEUR:   str  = ""
    SMTP_USER:          str  = ""
    SMTP_MOT_DE_PASSE:  str  = ""
    SMTP_PASSWORD:      str  = ""
    SMTP_TLS:           bool = True
    EMAIL_EXPEDITEUR:   str  = "noreply@hr-skills.cm"
    EMAIL_FROM:         str  = "noreply@hr-skills.cm"
    NOM_EXPEDITEUR:     str  = "HR-Skills SARL"

    # ── CORS ──────────────────────────────────────────────────
    # Version CORRIGÉE : utiliser une chaîne puis la convertir
    ORIGINES_AUTORISEES_STR: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174"
    
    @property
    def ORIGINES_AUTORISEES(self) -> List[str]:
        """Convertit la chaîne en liste pour le CORS"""
        return [o.strip() for o in self.ORIGINES_AUTORISEES_STR.split(",") if o.strip()]

    # ── CinetPay ──────────────────────────────────────────────
    CINETPAY_API_KEY:          str = ""
    CINETPAY_SITE_ID:          str = ""
    CINETPAY_URL_NOTIFICATION: str = ""
    CINETPAY_URL_RETOUR:       str = ""

    # ── Stripe ────────────────────────────────────────────────
    STRIPE_CLE_PUBLIQUE: str = ""
    STRIPE_CLE_SECRETE:  str = ""
    STRIPE_CLE_WEBHOOK:  str = ""

    # ── Limites ───────────────────────────────────────────────
    LIMITE_REQUETES_MINUTE:   int = 100
    LIMITE_CONNEXIONS_MINUTE: int = 5
    LIMITE_UPLOAD_MINUTE:     int = 10
    TAILLE_MAX_FICHIER_MO:    int = 5

    # ── Propriétés calculées ──────────────────────────────────
    @property
    def est_production(self) -> bool:
        return (self.ENVIRONNEMENT or self.APP_ENV) == "production"

    @property
    def est_developpement(self) -> bool:
        return (self.ENVIRONNEMENT or self.APP_ENV) == "development"

    @property
    def taille_max_octets(self) -> int:
        return self.TAILLE_MAX_FICHIER_MO * 1024 * 1024

    @property
    def algorithme(self) -> str:
        return self.ALGORITHME_JWT or self.ALGORITHM

    @property
    def duree_acces_minutes(self) -> int:
        return self.DUREE_JETON_ACCES_MINUTES or self.ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def duree_rafraich_jours(self) -> int:
        return self.DUREE_JETON_RAFRAICH_JOURS or self.REFRESH_TOKEN_EXPIRE_DAYS

    @property
    def smtp_hote(self) -> str:
        return self.SMTP_HOTE or self.SMTP_HOST

    @property
    def smtp_utilisateur(self) -> str:
        return self.SMTP_UTILISATEUR or self.SMTP_USER

    @property
    def smtp_mot_de_passe(self) -> str:
        return self.SMTP_MOT_DE_PASSE or self.SMTP_PASSWORD

    @property
    def email_expediteur(self) -> str:
        return self.EMAIL_EXPEDITEUR or self.EMAIL_FROM


@lru_cache()
def obtenir_parametres() -> Parametres:
    return Parametres()


parametres = obtenir_parametres()