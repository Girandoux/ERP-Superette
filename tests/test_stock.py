# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : tests/test_stock.py
# ROLE : Tests des fonctions de stock
# AUTEUR : Girandoux Fandio
# ============================================================

from utils import stock
from utils.calculs import calcul_stock_final, get_statut_stock

# ============================================================
# 1. CALCULS DU STOCK
# ============================================================

# Les calculs valident l'evolution du stock et les seuils operationnels.

def test_calcul_stock_final():
    """Verifie le calcul du stock final."""
    assert calcul_stock_final(
        10,
        entrees=5,
        sorties=3,
        pertes=2,
        ajustements=1,
    ) == 11

def test_get_statut_stock():
    """Verifie les statuts de stock."""
    assert get_statut_stock(0, 5) == "RUPTURE"
    assert get_statut_stock(3, 5) == "ALERTE"
    assert get_statut_stock(10, 5) == "NORMAL"

# ============================================================
# 2. CONTROLES METIER DU STOCK
# ============================================================

# monkeypatch isole la regle de vente du stockage reel en base de donnees.

def test_can_sell_stock_disponible(monkeypatch):
    """Verifie qu'une vente est autorisee si le stock suffit."""
    monkeypatch.setattr(
        stock,
        "get_stock_actuel",
        lambda produit_id: 10,
    )
    result = stock.can_sell(produit_id=1, quantite=4)
    assert result["success"] is True

def test_can_sell_stock_insuffisant(monkeypatch):
    """Verifie qu'une vente est refusee si le stock est insuffisant."""
    monkeypatch.setattr(
        stock,
        "get_stock_actuel",
        lambda produit_id: 2,
    )
    result = stock.can_sell(produit_id=1, quantite=4)
    assert result["success"] is False
    assert "Stock insuffisant" in result["message"]
