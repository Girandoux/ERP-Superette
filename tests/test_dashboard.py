# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : tests/test_dashboard.py
# ROLE : Tests des helpers Dashboard
# AUTEUR : Girandoux Fandio
# ============================================================

import pandas as pd

from utils import dashboard

# ============================================================
# 1. FORMATAGE DES INDICATEURS
# ============================================================

def test_format_dashboard_kpis():
    """Verifie que les montants sont formates."""
    kpis = {
        "chiffre_affaires": 10000,
        "benefice_net": 2500,
        "alertes_stock": 2,
    }
    result = dashboard.format_dashboard_kpis(kpis)
    assert result["chiffre_affaires_affiche"].endswith("FCFA")
    assert result["benefice_net_affiche"].endswith("FCFA")
    assert result["alertes_stock"] == 2

# ============================================================
# 2. CARTES ET DONNEES DU DASHBOARD
# ============================================================

# Les dependances SQL sont remplacees par des mocks pour tester uniquement
# la logique de preparation des donnees du dashboard.
def test_get_dashboard_cards(monkeypatch):
    """Verifie la creation des cartes dashboard."""
    monkeypatch.setattr(
        dashboard,
        "load_dashboard_kpis",
        lambda: {
        "chiffre_affaires": 1000,
        "benefice_net": 200,
        "valeur_stock": 5000,
        "solde_tresorerie": 800,
        "alertes_stock": 1,
        "ruptures_stock": 0,
        },
    )
    cards = dashboard.get_dashboard_cards()
    assert len(cards) == 6
    assert cards[0]["title"] == "Chiffre d'affaires"

def test_load_dashboard_data_error(monkeypatch):
    """Verifie la reponse si le dashboard SQL echoue."""
    def raise_error():
        raise RuntimeError("Erreur test")
    monkeypatch.setattr(
        dashboard.dashboard_db,
        "get_dashboard_data",
        raise_error,
    )
    result = dashboard.load_dashboard_data()
    assert "error" in result

def test_chart_data_mock(monkeypatch):
    """Verifie un chargement de donnees graphique mocke."""
    expected = pd.DataFrame(
        {"mois": ["2026-01"], "chiffre_affaires": [1000]}
    )
    monkeypatch.setattr(
        dashboard.dashboard_db,
        "get_ventes_mensuelles",
        lambda: expected,
    )
    assert dashboard.get_sales_chart_data().equals(expected)
