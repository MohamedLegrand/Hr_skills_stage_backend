"""
Chemin : Hr-skills-stage-backend/app/core/config.py
----------------------------------------------------
Compatible avec les noms de variables du fichier .env existant.
Supporte les deux conventions (anglais ET français) pour éviter
tout conflit entre .env et config.py.
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
    APP_NAME:       str = "HR-Skills Stage API"   # alias .env
    VERSION:        str = "1.0.0"

    # ENVIRONNEMENT accepte ENVIRONNEMENT ou APP_ENV depuis .env
    ENVIRONNEMENT:  str = "development"
    APP_ENV:        str = "development"            # alias .env

    DEBUG:          bool = True

    # ── Base de données ───────────────────────────────────────
    DATABASE_URL:      str = ""
    DATABASE_URL_SYNC: str = ""
    DB_ECHO_SQL:       bool = False

    # ── JWT ── supporte les deux nommages ─────────────────────
    SECRET_KEY:                    str = "changeme_minimum_32_chars_secret_key!!"
    ALGORITHME_JWT:                str = "HS256"
    ALGORITHM:                     str = "HS256"          # alias .env
    DUREE_JETON_ACCES_MINUTES:     int = 1440
    ACCESS_TOKEN_EXPIRE_MINUTES:   int = 1440             # alias .env
    DUREE_JETON_RAFRAICH_JOURS:    int = 7
    REFRESH_TOKEN_EXPIRE_DAYS:     int = 7                # alias .env

    # ── Supabase ── supporte les deux nommages ────────────────
    SUPABASE_URL:         str = ""
    SUPABASE_KEY:         str = ""                        # alias .env
    SUPABASE_ANON_KEY:    str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # ── CORS ──────────────────────────────────────────────────
    ORIGINES_AUTORISEES: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://hr-skills.cm",
    ]

    # ── SMTP ── supporte les deux nommages ────────────────────
    SMTP_HOTE:          str = "smtp.gmail.com"
    SMTP_HOST:          str = "smtp.gmail.com"            # alias .env
    SMTP_PORT:          int = 587
    SMTP_UTILISATEUR:   str = ""
    SMTP_USER:          str = ""                          # alias .env
    SMTP_MOT_DE_PASSE:  str = ""
    SMTP_PASSWORD:      str = ""                          # alias .env
    SMTP_TLS:           bool = True
    EMAIL_EXPEDITEUR:   str = "noreply@hr-skills.cm"
    EMAIL_FROM:         str = "noreply@hr-skills.cm"      # alias .env
    NOM_EXPEDITEUR:     str = "HR-Skills SARL"

    # ── CinetPay ──────────────────────────────────────────────
    CINETPAY_API_KEY:          str = ""
    CINETPAY_SITE_ID:          str = ""
    CINETPAY_URL_NOTIFICATION: str = ""
    CINETPAY_URL_RETOUR:       str = ""

    # ── Stripe ────────────────────────────────────────────────
    STRIPE_CLE_PUBLIQUE: str = ""
    STRIPE_CLE_SECRETE:  str = ""
    STRIPE_CLE_WEBHOOK:  str = ""

    # ── Frontend ──────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Réinitialisation mot de passe ─────────────────────────────
    DUREE_JETON_REINIT_MINUTES: int = 30

    # ── Limites ───────────────────────────────────────────────
    LIMITE_REQUETES_MINUTE: int = 100
    LIMITE_CONNEXIONS_MINUTE: int = 5
    LIMITE_UPLOAD_MINUTE: int = 10
    TAILLE_MAX_FICHIER_MO: int = 5

    # ── Propriétés calculées ──────────────────────────────────
    @property
    def est_production(self) -> bool:
        env = self.ENVIRONNEMENT or self.APP_ENV
        return env == "production"

    @property
    def est_developpement(self) -> bool:
        env = self.ENVIRONNEMENT or self.APP_ENV
        return env == "development"

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
    def supabase_key(self) -> str:
        return self.SUPABASE_ANON_KEY or self.SUPABASE_KEY

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