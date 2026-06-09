import os
import uuid
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger("hr_skills")

PDF_DIR = "uploads/pdf"


def _init_styles():
    styles = getSampleStyleSheet()
    titre = ParagraphStyle(
        "titre",
        parent=styles["Heading1"],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#1a237e"),
    )
    sous_titre = ParagraphStyle(
        "sous_titre",
        parent=styles["Normal"],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor("#424242"),
    )
    corps = ParagraphStyle(
        "corps",
        parent=styles["Normal"],
        fontSize=11,
        leading=18,
        spaceAfter=10,
    )
    return styles, titre, sous_titre, corps


def generer_convention(data: dict) -> str:
    """
    Génère la convention de stage en PDF.
    data: {stagiaire_nom, stagiaire_prenom, email, stage_titre, encadreur_nom, date_debut, date_fin}
    Retourne le chemin local du fichier PDF.
    """
    os.makedirs(PDF_DIR, exist_ok=True)
    nom_fichier = f"convention_{uuid.uuid4()}.pdf"
    chemin = os.path.join(PDF_DIR, nom_fichier)

    doc = SimpleDocTemplate(chemin, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles, style_titre, style_sous_titre, style_corps = _init_styles()
    elements = []

    elements.append(Paragraph("HR-SKILLS SARL", style_titre))
    elements.append(Paragraph("CONVENTION DE STAGE", style_sous_titre))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a237e")))
    elements.append(Spacer(1, 0.5*cm))

    date_gen = datetime.now().strftime("%d/%m/%Y")
    elements.append(Paragraph(f"<b>Date de génération :</b> {date_gen}", style_corps))
    elements.append(Spacer(1, 0.4*cm))

    infos = [
        ["Stagiaire", f"{data.get('stagiaire_prenom', '')} {data.get('stagiaire_nom', '')}"],
        ["Email", data.get("email", "—")],
        ["Stage", data.get("stage_titre", "—")],
        ["Encadreur", data.get("encadreur_nom", "—")],
        ["Date de début", str(data.get("date_debut", "—"))],
        ["Date de fin", str(data.get("date_fin", "—"))],
    ]
    table = Table(infos, colWidths=[5*cm, 12*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eaf6")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9e9e9e")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 1*cm))

    elements.append(Paragraph(
        "La présente convention est établie entre Hr-Skills SARL et le stagiaire mentionné ci-dessus, "
        "pour un stage d'une durée définie selon les dates indiquées. Le stagiaire s'engage à respecter "
        "le règlement intérieur de l'entreprise et les directives de son encadreur.",
        style_corps
    ))
    elements.append(Spacer(1, 1.5*cm))

    signatures = [
        ["L'entreprise", "", "Le stagiaire"],
        ["\n\n\n_____________________", "", "\n\n\n_____________________"],
        ["Hr-Skills SARL", "", f"{data.get('stagiaire_prenom', '')} {data.get('stagiaire_nom', '')}"],
    ]
    table_sig = Table(signatures, colWidths=[6*cm, 5*cm, 6*cm])
    table_sig.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
    ]))
    elements.append(table_sig)

    doc.build(elements)
    logger.info(f"Convention générée : {chemin}")
    return chemin


def generer_attestation(data: dict) -> str:
    """
    Génère l'attestation de fin de stage en PDF.
    data: {stagiaire_nom, stagiaire_prenom, stage_titre, date_debut, date_fin, note_moyenne}
    Retourne le chemin local du fichier PDF.
    """
    os.makedirs(PDF_DIR, exist_ok=True)
    nom_fichier = f"attestation_{uuid.uuid4()}.pdf"
    chemin = os.path.join(PDF_DIR, nom_fichier)

    doc = SimpleDocTemplate(chemin, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles, style_titre, style_sous_titre, style_corps = _init_styles()
    elements = []

    elements.append(Paragraph("HR-SKILLS SARL", style_titre))
    elements.append(Paragraph("ATTESTATION DE FIN DE STAGE", style_sous_titre))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a237e")))
    elements.append(Spacer(1, 0.8*cm))

    prenom = data.get("stagiaire_prenom", "")
    nom = data.get("stagiaire_nom", "")
    stage = data.get("stage_titre", "")
    debut = data.get("date_debut", "")
    fin = data.get("date_fin", "")
    note = data.get("note_moyenne", "")

    texte = (
        f"La Direction de <b>Hr-Skills SARL</b> atteste que <b>M./Mme {prenom} {nom}</b> "
        f"a effectué un stage en <b>{stage}</b> du <b>{debut}</b> au <b>{fin}</b> "
        f"au sein de notre structure."
    )
    elements.append(Paragraph(texte, style_corps))
    elements.append(Spacer(1, 0.5*cm))

    if note:
        elements.append(Paragraph(
            f"À l'issue de ce stage, la note globale obtenue est de <b>{note}/20</b>.",
            style_corps
        ))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(
        "Cette attestation est délivrée pour servir et valoir ce que de droit.",
        style_corps
    ))
    elements.append(Spacer(1, 2*cm))

    date_gen = datetime.now().strftime("%d/%m/%Y")
    elements.append(Paragraph(f"Fait à Abidjan, le {date_gen}", style_corps))
    elements.append(Spacer(1, 1.5*cm))
    elements.append(Paragraph("<b>Le Directeur Général</b>", style_corps))
    elements.append(Paragraph("\n\n\n_____________________", style_corps))

    doc.build(elements)
    logger.info(f"Attestation générée : {chemin}")
    return chemin
