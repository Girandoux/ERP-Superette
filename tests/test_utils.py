# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : tests/test_utils.py
# ROLE : Tests des fonctions utilitaires generales
# AUTEUR : Girandoux Fandio
# ============================================================

from datetime import date

from utils.helpers import (
    clean_text,
    format_money,
    normalize_text,
    parse_date,
    safe_divide,
    slugify,
    to_float,
    to_int,
)
from utils.validation import (
    validate_categorie,
    validate_date_range,
    validate_produit,
)

# ============================================================
# 1. TESTS DES FONCTIONS UTILITAIRES
# ============================================================

# Ces tests couvrent le nettoyage, la normalisation, les conversions et les dates.

def test_clean_text():
    """Verifie le nettoyage des espaces."""
    assert clean_text("  Bonjour   Monde  ") == "Bonjour Monde"

def test_normalize_text_et_slugify():
    """Verifie la normalisation sans accents."""
    assert normalize_text("Catégorie Été") == "categorie ete"
    assert slugify("Catégorie Été") == "categorie_ete"

def test_conversions_et_division():
    """Verifie les conversions protegees."""
    assert to_int("10.8") == 10
    assert to_float("10.5") == 10.5
    assert safe_divide(10, 2) == 5
    assert safe_divide(10, 0) == 0

def test_format_money():
    """Verifie le formatage monetaire."""
    assert format_money(1500) == "1 500 FCFA"

def test_parse_date():
    """Verifie plusieurs formats de date."""
    assert parse_date("2026-01-31") == date(2026, 1, 31)
    assert parse_date("31/01/2026") == date(2026, 1, 31)

# ============================================================
# 2. TESTS DES VALIDATIONS METIER
# ============================================================

# Les validations confirment les regles metier sans modifier les donnees source.

def test_validate_categorie():
    """Verifie une categorie valide."""
    valid, errors = validate_categorie(
        {
            "code_categorie": "BOI",
            "nom_categorie": "Boisson",
        }
    )
    assert valid is True
    assert errors == []

def test_validate_produit_invalide():
    """Verifie un produit invalide sans categorie."""
    valid, errors = validate_produit(
        {
            "code_produit": "P01",
            "nom_produit": "Produit",
            "categorie_id": 0,
            "unite": "Piece",
            "qte_par_carton": 1,
            "stock_min": 0,
        }
    )
    assert valid is False
    assert errors

def test_validate_date_range():
    """Verifie qu'une periode incoherente est refusee."""
    valid, message = validate_date_range("2026-02-01", "2026-01-01")
    assert valid is False
    assert "date de fin" in message.lower()
