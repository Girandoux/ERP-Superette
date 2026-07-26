# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : tests/test_achats.py
# ROLE : Tests des achats et lignes d'achat
# AUTEUR : Girandoux Fandio
# ============================================================

from datetime import date

from utils import achats
from utils.calculs import calcul_ligne_achat,calcul_total_facture

# ============================================================
# 1. CALCULS DES ACHATS
# ============================================================

# Ces tests verifient les formules utilisees avant l'enregistrement en base.
def test_calcul_ligne_achat():
    """Verifie quantite, prix piece et total achat."""
    result = calcul_ligne_achat(
        qte_cartons=2,
        qte_par_carton=12,
        pu_achat_carton=2400,
    )
    assert result["quantite_achat"] == 24
    assert result["pu_achat_piece"] == 200
    assert result["total_achat"] == 4800

def test_calcul_total_facture():
    """Verifie le total facture avec frais."""
    lignes = [{"total_achat": 1000}, {"total_achat": 2500}]
    assert calcul_total_facture(lignes, frais_enlevement=500) == 4000

# ============================================================
# 2. PREPARATION ET VALIDATION DES DONNEES
# ============================================================

def test_prepare_achat_data():
    """Verifie la normalisation d'une facture achat."""
    data = achats.prepare_achat_data(date(2026, 1, 1), " fac-001 ", 1, 100)
    assert data["numero_facture"] == "FAC-001"
    assert data["acheteur_id"] == 1
    assert data["frais_enlevement"] == 100

def test_validate_ligne_achat_dates_invalides():
    """Verifie que la peremption avant fabrication est refusee."""
    data = achats.prepare_ligne_achat_data(
        1,
        1,
        1,
        10,
        1000,
        date(2026, 2, 1),
        date(2026, 1, 1),
    )
    result = achats.validate_ligne_achat_form(data)
    assert result["success"] is False
