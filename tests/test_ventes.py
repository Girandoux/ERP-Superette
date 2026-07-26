# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : tests/test_ventes.py
# ROLE : Tests des ventes et lignes de vente
# AUTEUR : Girandoux Fandio
# ============================================================

from datetime import date

from utils import ventes
from utils.calculs import calcul_ligne_vente, calcul_total_vente

# ============================================================
# 1. CALCULS DES VENTES
# ============================================================

# Ces tests verifient les calculs effectues avant l'enregistrement d'une vente.

def test_calcul_ligne_vente():
    """Verifie montant, cout, marge et taux de marge."""
    result = calcul_ligne_vente(
        qte_vente=5,
        pu_vente=300,
        cout_unitaire=200,
    )
    assert result["montant_ligne"] == 1500
    assert result["cout_total"] == 1000
    assert result["marge"] == 500
    assert result["taux_marge"] == 33.33

def test_calcul_total_vente():
    """Verifie le total d'une vente."""
    lignes = [{"montant_ligne": 1500}, {"montant_ligne": 500}]
    assert calcul_total_vente(lignes) == 2000

# ============================================================
# 2. PREPARATION ET VALIDATION DES DONNEES
# ============================================================

def test_prepare_vente_data():
    """Verifie la preparation d'une vente."""
    data = ventes.prepare_vente_data(
        date(2026, 1, 1),
        vendeur_id=2,
    )
    assert data["date_vente"] == date(2026, 1, 1)
    assert data["vendeur_id"] == 2

def test_validate_ligne_vente_stock_insuffisant():
    """Verifie le refus si la quantite vendue depasse le stock."""
    data = ventes.prepare_ligne_vente_data(
        1,
        1,
        10,
        500,
        200,
        stock_disponible=3,
    )
    result = ventes.validate_ligne_vente_form(data)
    assert result["success"] is False
