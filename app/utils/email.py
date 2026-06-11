"""
Chemin : Hr-skills-stage-backend/app/utils/email.py
-----------------------------------------------------
Envoi d'emails transactionnels via SMTP asynchrone (aiosmtplib).
Paramètres SMTP lus depuis app/core/config.py.
Aucune exception ne se propage vers l'appelant — les erreurs sont loggées.
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import parametres

logger = logging.getLogger("hr_skills")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers de mise en page HTML
# ──────────────────────────────────────────────────────────────────────────────

_COULEUR_PRINCIPALE = "#1B3A6B"
_COULEUR_SUCCES     = "#28a745"
_COULEUR_DANGER     = "#dc3545"

_CSS_BOUTON = (
    "display:inline-block;"
    f"background:{_COULEUR_PRINCIPALE};"
    "color:#ffffff;"
    "padding:14px 32px;"
    "border-radius:8px;"
    "text-decoration:none;"
    "font-size:15px;"
    "font-weight:bold;"
    "letter-spacing:0.3px;"
)

_CSS_CONTAINER = (
    "font-family:Arial,sans-serif;"
    "max-width:600px;"
    "margin:0 auto;"
    "padding:32px 24px;"
    "color:#333333;"
)

_CSS_EN_TETE = (
    f"background:{_COULEUR_PRINCIPALE};"
    "padding:20px 24px;"
    "border-radius:8px 8px 0 0;"
    "text-align:center;"
)

_CSS_CORPS = (
    "background:#ffffff;"
    "padding:32px 24px;"
    "border:1px solid #e0e0e0;"
    "border-top:none;"
    "border-radius:0 0 8px 8px;"
)


def _en_tete_html() -> str:
    return f"""
    <div style="{_CSS_EN_TETE}">
        <span style="color:#ffffff;font-size:22px;font-weight:bold;
                     font-family:Arial,sans-serif;letter-spacing:1px;">
            HR-Skills
        </span>
    </div>
    """


def _pied_page_html() -> str:
    return """
    <div style="text-align:center;margin-top:32px;padding-top:16px;
                border-top:1px solid #eeeeee;">
        <p style="color:#aaaaaa;font-size:12px;margin:4px 0;">
            HR-Skills SARL &mdash; Yaoundé, Cameroun
        </p>
        <p style="color:#aaaaaa;font-size:12px;margin:4px 0;">
            <a href="https://hr-skills.cm"
               style="color:#1B3A6B;text-decoration:none;">hr-skills.cm</a>
        </p>
    </div>
    """


def _enveloppe(contenu: str) -> str:
    """Entoure le contenu avec l'en-tête et le pied de page HR-Skills."""
    return f"""
    <div style="{_CSS_CONTAINER}">
        {_en_tete_html()}
        <div style="{_CSS_CORPS}">
            {contenu}
            {_pied_page_html()}
        </div>
    </div>
    """


def _bouton(texte: str, lien: str) -> str:
    return f"""
    <div style="text-align:center;margin:32px 0;">
        <a href="{lien}" style="{_CSS_BOUTON}">{texte}</a>
    </div>
    """


def _badge(texte: str, couleur: str) -> str:
    return (
        f'<span style="color:{couleur};font-weight:bold;">{texte}</span>'
    )


def _bloc_motif(motif: str) -> str:
    return f"""
    <div style="background:#fff8e1;border-left:4px solid #ffc107;
                padding:12px 16px;border-radius:4px;margin:16px 0;">
        <p style="margin:0;font-size:14px;">
            <strong>Motif :</strong> {motif}
        </p>
    </div>
    """


def _ligne_tableau(libelle: str, valeur: str) -> str:
    return f"""
    <tr>
        <td style="padding:10px 12px;border:1px solid #dee2e6;
                   background:#f8f9fa;width:40%;font-weight:bold;
                   font-size:14px;">{libelle}</td>
        <td style="padding:10px 12px;border:1px solid #dee2e6;
                   font-size:14px;">{valeur}</td>
    </tr>
    """


# ──────────────────────────────────────────────────────────────────────────────
# Fonction centrale d'envoi SMTP
# ──────────────────────────────────────────────────────────────────────────────

async def envoyer_email(
    destinataire: str,
    sujet: str,
    corps_html: str,
) -> bool:
    """
    Envoie un email HTML via SMTP asynchrone (aiosmtplib).

    - Retourne True si l'envoi réussit, False sinon.
    - Ne lève jamais d'exception : les erreurs sont loggées.
    - Si SMTP_USER ou SMTP_PASSWORD est vide, l'envoi est ignoré (log warning).
    """
    smtp_user = parametres.smtp_utilisateur
    smtp_pass = parametres.smtp_mot_de_passe

    if not smtp_user or not smtp_pass:
        logger.warning(
            "SMTP non configuré (SMTP_USER/SMTP_PASSWORD manquants) "
            "— email non envoyé à %s.",
            destinataire,
        )
        return False

    expediteur = f"{parametres.NOM_EXPEDITEUR} <{parametres.email_expediteur}>"

    message = MIMEMultipart("alternative")
    message["Subject"] = sujet
    message["From"]    = expediteur
    message["To"]      = destinataire
    message.attach(MIMEText(corps_html, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            message,
            hostname=parametres.smtp_hote,
            port=parametres.SMTP_PORT,
            username=smtp_user,
            password=smtp_pass,
            start_tls=parametres.SMTP_TLS,
        )
        logger.info("Email envoyé à %s | sujet : %s", destinataire, sujet)
        return True

    except aiosmtplib.SMTPAuthenticationError as exc:
        logger.error(
            "Échec authentification SMTP pour %s : %s", destinataire, exc
        )
    except aiosmtplib.SMTPConnectError as exc:
        logger.error(
            "Impossible de joindre le serveur SMTP (%s:%s) : %s",
            parametres.smtp_hote, parametres.SMTP_PORT, exc,
        )
    except aiosmtplib.SMTPException as exc:
        logger.error("Erreur SMTP — %s : %s", destinataire, exc)
    except Exception as exc:
        logger.error(
            "Erreur inattendue lors de l'envoi à %s : %s", destinataire, exc
        )

    return False


# ──────────────────────────────────────────────────────────────────────────────
# Emails métier
# ──────────────────────────────────────────────────────────────────────────────

async def envoyer_email_inscription_validee(
    courriel: str,
    nom_complet: str,
) -> bool:
    """Notifie le stagiaire que son inscription a été acceptée."""
    corps = _enveloppe(f"""
        <h2 style="color:{_COULEUR_PRINCIPALE};margin-top:0;">
            Inscription validée !
        </h2>
        <p>Bonjour <strong>{nom_complet}</strong>,</p>
        <p>
            Nous avons le plaisir de vous informer que votre dossier d'inscription
            a été {_badge("validé", _COULEUR_SUCCES)} par notre équipe.
        </p>
        <p>
            Vous pouvez maintenant vous connecter à votre espace stagiaire
            et procéder au paiement des frais de stage pour finaliser votre admission.
        </p>
        {_bouton("Accéder à mon espace", f"{parametres.FRONTEND_URL}/connexion")}
        <p>Bienvenue au sein de HR-Skills !</p>
        <p style="margin-bottom:0;">
            Cordialement,<br/>
            <strong>L'équipe HR-Skills</strong>
        </p>
    """)
    return await envoyer_email(
        courriel,
        "Votre inscription est validée — HR-Skills",
        corps,
    )


async def envoyer_email_inscription_refusee(
    courriel: str,
    nom_complet: str,
    motif: str,
) -> bool:
    """Notifie le stagiaire que son inscription a été refusée."""
    corps = _enveloppe(f"""
        <h2 style="color:{_COULEUR_PRINCIPALE};margin-top:0;">
            Décision concernant votre inscription
        </h2>
        <p>Bonjour <strong>{nom_complet}</strong>,</p>
        <p>
            Après examen de votre dossier, nous regrettons de vous informer
            que votre demande d'inscription n'a pas pu être acceptée.
        </p>
        {_bloc_motif(motif)}
        <p>
            Si vous pensez que cette décision est une erreur ou si vous souhaitez
            obtenir plus d'informations, n'hésitez pas à nous contacter
            en répondant directement à cet email.
        </p>
        <p style="margin-bottom:0;">
            Cordialement,<br/>
            <strong>L'équipe HR-Skills</strong>
        </p>
    """)
    return await envoyer_email(
        courriel,
        "Décision sur votre inscription — HR-Skills",
        corps,
    )


async def envoyer_email_document_valide(
    courriel: str,
    nom_complet: str,
    type_document: str,
) -> bool:
    """Notifie le stagiaire qu'un document soumis a été validé."""
    corps = _enveloppe(f"""
        <h2 style="color:{_COULEUR_PRINCIPALE};margin-top:0;">
            Document validé
        </h2>
        <p>Bonjour <strong>{nom_complet}</strong>,</p>
        <p>
            Votre document <strong>« {type_document} »</strong>
            a été {_badge("validé", _COULEUR_SUCCES)} par notre équipe.
        </p>
        <p>
            Connectez-vous à votre espace pour consulter l'avancement
            de votre dossier.
        </p>
        {_bouton("Voir mon dossier", f"{parametres.FRONTEND_URL}/mon-dossier")}
        <p style="margin-bottom:0;">
            Cordialement,<br/>
            <strong>L'équipe HR-Skills</strong>
        </p>
    """)
    return await envoyer_email(
        courriel,
        f"Document validé : {type_document} — HR-Skills",
        corps,
    )


async def envoyer_email_document_rejete(
    courriel: str,
    nom_complet: str,
    type_document: str,
    motif: str,
) -> bool:
    """Notifie le stagiaire qu'un document soumis a été rejeté."""
    corps = _enveloppe(f"""
        <h2 style="color:{_COULEUR_PRINCIPALE};margin-top:0;">
            Document rejeté — action requise
        </h2>
        <p>Bonjour <strong>{nom_complet}</strong>,</p>
        <p>
            Votre document <strong>« {type_document} »</strong>
            a été {_badge("rejeté", _COULEUR_DANGER)}.
        </p>
        {_bloc_motif(motif)}
        <p>
            Veuillez soumettre une version corrigée depuis votre espace stagiaire
            dans les plus brefs délais afin de ne pas retarder le traitement
            de votre dossier.
        </p>
        {_bouton("Corriger mon document", f"{parametres.FRONTEND_URL}/mon-dossier")}
        <p style="margin-bottom:0;">
            Cordialement,<br/>
            <strong>L'équipe HR-Skills</strong>
        </p>
    """)
    return await envoyer_email(
        courriel,
        f"Document rejeté : {type_document} — HR-Skills",
        corps,
    )


async def envoyer_email_paiement_confirme(
    courriel: str,
    nom_complet: str,
    montant: str,
    reference: str,
) -> bool:
    """Notifie le stagiaire que son paiement a été confirmé."""
    corps = _enveloppe(f"""
        <h2 style="color:{_COULEUR_PRINCIPALE};margin-top:0;">
            Paiement confirmé
        </h2>
        <p>Bonjour <strong>{nom_complet}</strong>,</p>
        <p>
            Votre paiement a bien été reçu et enregistré.
            Votre stage est maintenant officiellement confirmé.
        </p>
        <table style="border-collapse:collapse;width:100%;margin:20px 0;">
            {_ligne_tableau("Référence de paiement", f"<code>{reference}</code>")}
            {_ligne_tableau("Montant réglé", montant)}
        </table>
        <p style="font-size:13px;color:#666666;">
            Conservez ce récapitulatif comme justificatif de paiement.
        </p>
        {_bouton("Accéder à mon espace", f"{parametres.FRONTEND_URL}/mon-espace")}
        <p style="margin-bottom:0;">
            Merci de votre confiance,<br/>
            <strong>L'équipe HR-Skills</strong>
        </p>
    """)
    return await envoyer_email(
        courriel,
        f"Confirmation de paiement (réf. {reference}) — HR-Skills",
        corps,
    )


async def envoyer_email_reinitialisation_mdp(
    courriel: str,
    nom_complet: str,
    token: str,
) -> bool:
    """
    Envoie le lien de réinitialisation de mot de passe.
    Le lien est valable DUREE_JETON_REINIT_MINUTES minutes (défaut : 30).
    """
    lien = f"{parametres.FRONTEND_URL}/reinitialiser-mdp?token={token}"
    duree = parametres.DUREE_JETON_REINIT_MINUTES

    corps = _enveloppe(f"""
        <h2 style="color:{_COULEUR_PRINCIPALE};margin-top:0;">
            Réinitialisation de votre mot de passe
        </h2>
        <p>Bonjour <strong>{nom_complet}</strong>,</p>
        <p>
            Vous avez demandé la réinitialisation de votre mot de passe
            sur la plateforme HR-Skills.
        </p>
        <p>
            Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe.
            <strong>Ce lien expire dans {duree} minutes.</strong>
        </p>
        {_bouton("Réinitialiser mon mot de passe", lien)}
        <p style="font-size:13px;color:#666666;">
            Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
            Votre mot de passe ne sera pas modifié.
        </p>
        <p style="font-size:12px;color:#aaaaaa;word-break:break-all;">
            Ou copiez ce lien dans votre navigateur :<br/>
            <a href="{lien}" style="color:{_COULEUR_PRINCIPALE};">{lien}</a>
        </p>
        <p style="margin-bottom:0;">
            Cordialement,<br/>
            <strong>L'équipe HR-Skills</strong>
        </p>
    """)
    return await envoyer_email(
        courriel,
        "Réinitialisation de votre mot de passe — HR-Skills",
        corps,
    )
