import uuid
import random
import string
from datetime import datetime, timezone


def generate_reference(prefix: str = "PAY") -> str:
    """Génère une référence unique pour un paiement."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    suffixe = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{timestamp}-{suffixe}"


def generate_uuid() -> str:
    return str(uuid.uuid4())


def paginate(query, page: int = 1, taille: int = 20):
    """Applique la pagination sur une requête SQLAlchemy."""
    total = query.count()
    items = query.offset((page - 1) * taille).limit(taille).all()
    return {
        "total": total,
        "page": page,
        "taille": taille,
        "pages": (total + taille - 1) // taille,
        "items": items,
    }


def mois_actuel() -> str:
    """Retourne le mois courant au format YYYY-MM."""
    return datetime.now(timezone.utc).strftime("%Y-%m")
