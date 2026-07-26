# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/validation.py
# ROLE : Validations generales et metier
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

import re
from typing import Any

from utils.helpers import clean_text, parse_date, to_float, to_int

# ============================================================
# 1. VALIDATIONS GENERALES
# ============================================================


def is_empty(value: Any) -> bool:
    """Verifie si une valeur est vide."""
    return value is None or str(value).strip() == ""


def is_positive_number(value: Any, allow_zero: bool = True) -> bool:
    """Verifie si une valeur est un nombre positif."""
    number = to_float(value, default=-1)
    return number >= 0 if allow_zero else number > 0


def is_positive_int(value: Any, allow_zero: bool = True) -> bool:
    """Verifie si une valeur est un entier positif."""
    number = to_int(value, default=-1)
    return number >= 0 if allow_zero else number > 0


def is_valid_date(value: Any) -> bool:
    """Verifie si une valeur est une date valide."""
    return parse_date(value) is not None


def is_valid_code(
    value: Any,
    min_length: int = 2,
    max_length: int = 30,
) -> bool:
    """Verifie un code produit ou categorie."""
    text = clean_text(value)
    pattern = rf"[A-Za-z0-9_-]{{{min_length},{max_length}}}"
    return bool(re.fullmatch(pattern, text))


def require_fields(
    data: dict[str, Any],
    fields: list[str],
) -> list[str]:
    """Retourne la liste des champs obligatoires manquants."""
    return [field for field in fields if is_empty(data.get(field))]


def validate_required(
    data: dict[str, Any],
    fields: list[str],
) -> tuple[bool, list[str]]:
    """Verifie les champs obligatoires."""
    missing = require_fields(data, fields)
    return not missing, missing


# ============================================================
# 2. VALIDATIONS PRODUITS ET CATEGORIES
# ============================================================


def validate_categorie(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide une categorie."""
    errors = []
    missing = require_fields(
        data,
        ["code_categorie", "nom_categorie"],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    code_categorie = data.get("code_categorie")
    if code_categorie and not is_valid_code(code_categorie):
        errors.append(
            "Le code categorie doit contenir 2 a 30 caracteres "
            "sans espace."
        )

    return not errors, errors


def validate_produit(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide un produit."""
    errors = []
    missing = require_fields(
        data,
        [
            "code_produit",
            "nom_produit",
            "categorie_id",
            "unite",
        ],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    code_produit = data.get("code_produit")
    if code_produit and not is_valid_code(code_produit):
        errors.append(
            "Le code produit doit contenir 2 a 30 caracteres "
            "sans espace."
        )

    if not is_positive_int(
        data.get("categorie_id"),
        allow_zero=False,
    ):
        errors.append("La categorie est obligatoire.")

    if not is_positive_number(
        data.get("qte_par_carton", 1),
        allow_zero=False,
    ):
        errors.append(
            "La quantite par carton doit etre superieure a 0."
        )

    if not is_positive_number(data.get("stock_min", 0)):
        errors.append(
            "Le stock minimum ne peut pas etre negatif."
        )

    return not errors, errors


def validate_personne(
    data: dict[str, Any],
    field_name: str,
) -> tuple[bool, list[str]]:
    """Valide un acheteur ou un vendeur."""
    errors = []

    if is_empty(data.get(field_name)):
        errors.append(
            f"Le champ {field_name} est obligatoire."
        )

    return not errors, errors


# ============================================================
# 3. VALIDATIONS ACHATS ET VENTES
# ============================================================


def validate_achat(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide une facture d'achat."""
    errors = []
    missing = require_fields(
        data,
        ["date_achat", "numero_facture", "acheteur_id"],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    date_achat = data.get("date_achat")
    if date_achat and not is_valid_date(date_achat):
        errors.append("La date d'achat est invalide.")

    if not is_positive_int(
        data.get("acheteur_id"),
        allow_zero=False,
    ):
        errors.append("L'acheteur est obligatoire.")

    if not is_positive_number(
        data.get("frais_enlevement", 0)
    ):
        errors.append(
            "Les frais d'enlevement ne peuvent pas etre negatifs."
        )

    return not errors, errors


def validate_ligne_achat(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide une ligne d'achat."""
    errors = []
    missing = require_fields(
        data,
        [
            "achat_id",
            "produit_id",
            "qte_cartons",
            "qte_par_carton",
            "pu_achat_carton",
        ],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    for field in ["achat_id", "produit_id"]:
        if not is_positive_int(
            data.get(field),
            allow_zero=False,
        ):
            errors.append(f"{field} doit etre valide.")

    for field in [
        "qte_cartons",
        "qte_par_carton",
        "pu_achat_carton",
    ]:
        if not is_positive_number(
            data.get(field),
            allow_zero=False,
        ):
            errors.append(
                f"{field} doit etre superieur a 0."
            )

    date_fabrication = data.get("date_fabrication")
    date_peremption = data.get("date_peremption")

    if date_fabrication and not is_valid_date(
        date_fabrication
    ):
        errors.append(
            "La date de fabrication est invalide."
        )

    if date_peremption and not is_valid_date(
        date_peremption
    ):
        errors.append(
            "La date de peremption est invalide."
        )

    fabrication = parse_date(date_fabrication)
    peremption = parse_date(date_peremption)

    if fabrication and peremption and peremption < fabrication:
        errors.append(
            "La date de peremption doit etre apres "
            "la date de fabrication."
        )

    return not errors, errors


def validate_vente(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide une vente."""
    errors = []
    missing = require_fields(
        data,
        ["date_vente", "vendeur_id"],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    date_vente = data.get("date_vente")
    if date_vente and not is_valid_date(date_vente):
        errors.append("La date de vente est invalide.")

    if not is_positive_int(
        data.get("vendeur_id"),
        allow_zero=False,
    ):
        errors.append("Le vendeur est obligatoire.")

    return not errors, errors


def validate_ligne_vente(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide une ligne de vente."""
    errors = []
    missing = require_fields(
        data,
        [
            "vente_id",
            "produit_id",
            "qte_vente",
            "pu_vente",
        ],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    for field in ["vente_id", "produit_id"]:
        if not is_positive_int(
            data.get(field),
            allow_zero=False,
        ):
            errors.append(f"{field} doit etre valide.")

    for field in ["qte_vente", "pu_vente"]:
        if not is_positive_number(
            data.get(field),
            allow_zero=False,
        ):
            errors.append(
                f"{field} doit etre superieur a 0."
            )

    stock_disponible = data.get("stock_disponible")
    if (
        stock_disponible is not None
        and to_float(data.get("qte_vente"))
        > to_float(stock_disponible)
    ):
        errors.append(
            "La quantite vendue depasse le stock disponible."
        )

    return not errors, errors


# ============================================================
# 4. VALIDATIONS METIER
# ============================================================


def validate_depense(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide une depense."""
    errors = []
    missing = require_fields(
        data,
        ["date_depense", "categorie_depense", "montant"],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    date_depense = data.get("date_depense")
    if date_depense and not is_valid_date(date_depense):
        errors.append("La date de depense est invalide.")

    if not is_positive_number(
        data.get("montant"),
        allow_zero=False,
    ):
        errors.append(
            "Le montant doit etre superieur a 0."
        )

    return not errors, errors


def validate_perte(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide une perte."""
    errors = []
    missing = require_fields(
        data,
        [
            "date_perte",
            "produit_id",
            "qte_perte",
            "motif_perte",
        ],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    date_perte = data.get("date_perte")
    if date_perte and not is_valid_date(date_perte):
        errors.append("La date de perte est invalide.")

    if not is_positive_int(
        data.get("produit_id"),
        allow_zero=False,
    ):
        errors.append("Le produit est obligatoire.")

    if not is_positive_number(
        data.get("qte_perte"),
        allow_zero=False,
    ):
        errors.append(
            "La quantite perdue doit etre superieure a 0."
        )

    stock_disponible = data.get("stock_disponible")
    if (
        stock_disponible is not None
        and to_float(data.get("qte_perte"))
        > to_float(stock_disponible)
    ):
        errors.append(
            "La perte depasse le stock disponible."
        )

    return not errors, errors


def validate_inventaire(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide un inventaire."""
    errors = []
    missing = require_fields(
        data,
        [
            "date_inventaire",
            "produit_id",
            "stock_theorique",
            "stock_physique",
        ],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    date_inventaire = data.get("date_inventaire")
    if date_inventaire and not is_valid_date(
        date_inventaire
    ):
        errors.append(
            "La date d'inventaire est invalide."
        )

    if not is_positive_int(
        data.get("produit_id"),
        allow_zero=False,
    ):
        errors.append("Le produit est obligatoire.")

    if not is_positive_number(data.get("stock_theorique")):
        errors.append(
            "Le stock theorique ne peut pas etre negatif."
        )

    if not is_positive_number(data.get("stock_physique")):
        errors.append(
            "Le stock physique ne peut pas etre negatif."
        )

    return not errors, errors


def validate_tresorerie(
    data: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Valide un mouvement de tresorerie."""
    errors = []
    missing = require_fields(
        data,
        ["date_mouvement", "type_mouvement", "montant"],
    )

    if missing:
        errors.append(
            "Champs obligatoires manquants : "
            + ", ".join(missing)
        )

    date_mouvement = data.get("date_mouvement")
    if date_mouvement and not is_valid_date(
        date_mouvement
    ):
        errors.append(
            "La date de mouvement est invalide."
        )

    if not is_positive_number(
        data.get("montant"),
        allow_zero=False,
    ):
        errors.append(
            "Le montant doit etre superieur a 0."
        )

    return not errors, errors


def validate_date_range(
    date_debut: Any,
    date_fin: Any,
) -> tuple[bool, str]:
    """Valide une periode."""
    start = parse_date(date_debut)
    end = parse_date(date_fin)

    if date_debut and not start:
        return False, "La date de debut est invalide."

    if date_fin and not end:
        return False, "La date de fin est invalide."

    if start and end and end < start:
        return (
            False,
            "La date de fin doit etre apres la date de debut.",
        )

    return True, "Periode valide."


__all__ = [
    "is_empty",
    "is_positive_number",
    "is_positive_int",
    "is_valid_date",
    "is_valid_code",
    "require_fields",
    "validate_required",
    "validate_categorie",
    "validate_produit",
    "validate_personne",
    "validate_achat",
    "validate_ligne_achat",
    "validate_vente",
    "validate_ligne_vente",
    "validate_depense",
    "validate_perte",
    "validate_inventaire",
    "validate_tresorerie",
    "validate_date_range",
]
