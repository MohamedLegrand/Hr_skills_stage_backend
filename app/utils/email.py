import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import parametres

logger = logging.getLogger("hr_skills")


def envoyer_email(destinataire: str, sujet: str, corps_html: str) -> bool:
    """Envoie un email via SMTP. Retourne True si succès, False sinon."""
    if not parametres.SMTP_UTILISATEUR or not parametres.SMTP_MOT_DE_PASSE:
        logger.warning("SMTP non configuré — email non envoyé.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = sujet
        msg["From"] = parametres.EMAIL_EXPEDITEUR
        msg["To"] = destinataire
        msg.attach(MIMEText(corps_html, "html", "utf-8"))

        with smtplib.SMTP(parametres.SMTP_HOTE, parametres.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(parametres.SMTP_UTILISATEUR, parametres.SMTP_MOT_DE_PASSE)
            server.sendmail(parametres.SMTP_UTILISATEUR, destinataire, msg.as_string())

        logger.info(f"Email envoyé à {destinataire} : {sujet}")
        return True

    except Exception as e:
        logger.error(f"Échec envoi email à {destinataire} : {e}")
        return False


def email_bienvenue(nom: str, email: str) -> bool:
    corps = f"""
    <h2>Bienvenue sur Hr-Skills, {nom} !</h2>
    <p>Votre compte a été créé avec succès.</p>
    <p>Vous pouvez maintenant vous connecter et déposer votre candidature.</p>
    <br><p>L'équipe Hr-Skills</p>
    """
    return envoyer_email(email, "Bienvenue sur Hr-Skills", corps)


def email_validation_dossier(nom: str, email: str) -> bool:
    corps = f"""
    <h2>Dossier validé, {nom} !</h2>
    <p>Votre dossier de candidature a été validé par notre équipe.</p>
    <p>Vous pouvez maintenant procéder au paiement des frais de stage.</p>
    <br><p>L'équipe Hr-Skills</p>
    """
    return envoyer_email(email, "Dossier validé — Hr-Skills", corps)


def email_paiement_confirme(nom: str, email: str, reference: str) -> bool:
    corps = f"""
    <h2>Paiement confirmé, {nom} !</h2>
    <p>Votre paiement (référence : <strong>{reference}</strong>) a été confirmé.</p>
    <p>Votre stage est maintenant officiellement démarré.</p>
    <br><p>L'équipe Hr-Skills</p>
    """
    return envoyer_email(email, "Paiement confirmé — Hr-Skills", corps)
