# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/dashboard.py
# ROLE : Services utilitaires pour la page Dashboard
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

from typing import Any
import logging
import pandas as pd
from database import dashboard_db
from utils.helpers import error_response,format_money,format_quantity,success_response,to_float

logger=logging.getLogger("utils")

# ============================================================
# 1. CHARGEMENT DES DONNEES
# ============================================================


def load_dashboard_data()->dict[str,Any]:
    """Charge toutes les donnees du dashboard."""
    try:
        return dashboard_db.get_dashboard_data()
    except Exception as error:
        logger.exception("Erreur chargement dashboard: %s",error)
        return {"kpis":{},"error":str(error)}

def load_dashboard_kpis()->dict[str,Any]:
    """Charge uniquement les KPIs globaux."""
    try:
        return dashboard_db.get_global_kpis()
    except Exception as error:
        logger.exception("Erreur KPIs dashboard: %s",error)
        return {}

def load_period_kpis(date_debut:str|None=None,date_fin:str|None=None)->dict[str,Any]:
    """Charge les KPIs d'une periode."""
    try:
        return dashboard_db.get_kpis_periode(date_debut,date_fin)
    except Exception as error:
        logger.exception("Erreur KPIs periode: %s",error)
        return {}

# ============================================================
# 2. FORMATAGE DES KPIS
# ============================================================


def format_dashboard_kpis(kpis:dict[str,Any])->dict[str,Any]:
    """Ajoute les valeurs formatees aux KPIs."""
    money_keys=["chiffre_affaires","total_achats","total_depenses","total_pertes","benefice_brut","benefice_net","valeur_stock","solde_tresorerie"]
    result=dict(kpis or {})
    for key in money_keys:
        if key in result:
            result[f"{key}_affiche"]=format_money(result.get(key,0))
    if "produits_actifs" in result:
        result["produits_actifs_affiche"]=format_quantity(result["produits_actifs"])
    return result

def get_dashboard_cards()->list[dict[str,Any]]:
    """Retourne les cartes principales du dashboard."""
    kpis=format_dashboard_kpis(load_dashboard_kpis())
    return [
        {"title":"Chiffre d'affaires","value":kpis.get("chiffre_affaires_affiche","0 FCFA"),"raw":to_float(kpis.get("chiffre_affaires",0))},
        {"title":"Benefice net","value":kpis.get("benefice_net_affiche","0 FCFA"),"raw":to_float(kpis.get("benefice_net",0))},
        {"title":"Valeur stock","value":kpis.get("valeur_stock_affiche","0 FCFA"),"raw":to_float(kpis.get("valeur_stock",0))},
        {"title":"Solde reel caisse","value":kpis.get("solde_tresorerie_affiche","0 FCFA"),"raw":to_float(kpis.get("solde_tresorerie",0))},
        {"title":"Alertes stock","value":kpis.get("alertes_stock",0),"raw":to_float(kpis.get("alertes_stock",0))},
        {"title":"Ruptures stock","value":kpis.get("ruptures_stock",0),"raw":to_float(kpis.get("ruptures_stock",0))}
    ]

def get_dashboard_status()->dict[str,Any]:
    """Retourne l'etat general du dashboard."""
    kpis=load_dashboard_kpis()
    if not kpis:
        return error_response("Dashboard indisponible")
    alerts=int(kpis.get("alertes_stock",0) or 0)
    ruptures=int(kpis.get("ruptures_stock",0) or 0)
    if ruptures>0:
        status="CRITIQUE"
    elif alerts>0:
        status="ALERTE"
    else:
        status="NORMAL"
    return success_response("Dashboard charge",{"status":status,"alertes_stock":alerts,"ruptures_stock":ruptures})

# ============================================================
# 3. TABLES DASHBOARD
# ============================================================


def get_sales_chart_data()->pd.DataFrame:
    """Retourne les ventes mensuelles."""
    return dashboard_db.get_ventes_mensuelles()

def get_purchases_chart_data()->pd.DataFrame:
    """Retourne les achats mensuels."""
    return dashboard_db.get_achats_mensuels()

def get_expenses_chart_data()->pd.DataFrame:
    """Retourne les depenses mensuelles."""
    return dashboard_db.get_depenses_mensuelles()

def get_losses_chart_data()->pd.DataFrame:
    """Retourne les pertes mensuelles."""
    return dashboard_db.get_pertes_mensuelles()

def get_top_products_sold(limit:int=10)->pd.DataFrame:
    """Retourne les meilleurs produits vendus."""
    return dashboard_db.get_top_produits_vendus(limit)

def get_top_products_bought(limit:int=10)->pd.DataFrame:
    """Retourne les meilleurs produits achetes."""
    return dashboard_db.get_top_produits_achetes(limit)

def get_stock_alerts()->pd.DataFrame:
    """Retourne les alertes stock."""
    return dashboard_db.get_alertes_stock()

def get_stock_by_category()->pd.DataFrame:
    """Retourne le stock par categorie."""
    return dashboard_db.get_repartition_stock_par_categorie()

def get_cashflow_recent()->pd.DataFrame:
    """Retourne les derniers mouvements de tresorerie."""
    return dashboard_db.get_flux_tresorerie()

__all__ = [
    "load_dashboard_data",
    "load_dashboard_kpis",
    "load_period_kpis",
    "format_dashboard_kpis",
    "get_dashboard_cards",
    "get_dashboard_status",
    "get_sales_chart_data",
    "get_purchases_chart_data",
    "get_expenses_chart_data",
    "get_losses_chart_data",
    "get_top_products_sold",
    "get_top_products_bought",
    "get_stock_alerts",
    "get_stock_by_category",
    "get_cashflow_recent",
]
