# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/stock.py
# ROLE : Services metier pour le stock
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from typing import Any
import logging
import pandas as pd
from database import stock_db
from utils.calculs import calcul_qte_cartons_possible,calcul_valeur_stock,get_statut_stock
from utils.helpers import error_response,format_money,format_quantity,success_response,to_float,to_int

logger=logging.getLogger("utils")

# ============================================================
# 1. CONSULTATION ET INDICATEURS DU STOCK
# ============================================================

def get_stock(produit_id:int)->dict[str,Any]|None:
    """Retourne le stock d'un produit."""
    return stock_db.get_stock_by_product(produit_id)

def get_stock_actuel(produit_id:int)->int:
    """Retourne la quantite en stock."""
    return stock_db.get_current_stock(produit_id)

def list_stock(active_only:bool=True)->pd.DataFrame:
    """Retourne tout le stock."""
    return stock_db.get_all_stock(active_only=active_only)

def list_alertes_stock()->pd.DataFrame:
    """Retourne les produits en alerte stock."""
    return stock_db.get_low_stock_products()

def list_ruptures_stock()->pd.DataFrame:
    """Retourne les produits en rupture."""
    return stock_db.get_out_of_stock_products()

def get_stock_kpis()->dict[str,Any]:
    """Retourne les KPIs stock."""
    return stock_db.get_stock_kpis()

def get_valeur_stock()->float:
    """Retourne la valeur totale du stock."""
    return stock_db.get_stock_value()

# ============================================================
# 2. MOUVEMENTS MANUELS DU STOCK
# ============================================================

def set_stock(produit_id:int,nouveau_stock:Any)->dict[str,Any]:
    """Fixe le stock d'un produit."""
    nouveau_stock=to_int(nouveau_stock)
    if nouveau_stock<0:
        return error_response("Le stock ne peut pas etre negatif")
    ok=stock_db.set_stock(produit_id,nouveau_stock)
    return success_response("Stock mis a jour") if ok else error_response("Mise a jour du stock impossible")

def add_stock(produit_id:int,quantite:Any)->dict[str,Any]:
    """Ajoute une quantite au stock."""
    quantite=to_int(quantite)
    if quantite<=0:
        return error_response("La quantite doit etre superieure a 0")
    ok=stock_db.add_stock(produit_id,quantite)
    return success_response("Stock augmente") if ok else error_response("Ajout au stock impossible")

def remove_stock(produit_id:int,quantite:Any)->dict[str,Any]:
    """Retire une quantite du stock."""
    quantite=to_int(quantite)
    if quantite<=0:
        return error_response("La quantite doit etre superieure a 0")
    stock_actuel=get_stock_actuel(produit_id)
    if quantite>stock_actuel:
        return error_response("Stock insuffisant")
    ok=stock_db.remove_stock(produit_id,quantite)
    return success_response("Stock diminue") if ok else error_response("Retrait du stock impossible")

# Controle la disponibilite du stock avant une vente ou une perte.
def can_sell(produit_id:int,quantite:Any)->dict[str,Any]:
    """Verifie si une vente est possible avec le stock actuel."""
    quantite=to_float(quantite)
    stock_actuel=get_stock_actuel(produit_id)
    if quantite<=0:
        return error_response("La quantite doit etre superieure a 0")
    if quantite>stock_actuel:
        return error_response("Stock insuffisant",{"stock_actuel":stock_actuel,"quantite_demandee":quantite})
    return success_response("Stock disponible",{"stock_actuel":stock_actuel,"quantite_demandee":quantite})

def can_register_loss(produit_id:int,quantite:Any)->dict[str,Any]:
    """Verifie si une perte est possible avec le stock actuel."""
    return can_sell(produit_id,quantite)

# ============================================================
# 3. AFFICHAGE, FILTRES ET SYNTHESE
# ============================================================

# Ajoute uniquement des informations calculees pour l'affichage :
# statut, valeur du stock et nombre de cartons disponibles.
def add_stock_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute des colonnes formatees pour Streamlit."""
    if df.empty:
        return df
    result=df.copy()
    if {"stock_actuel","stock_min"}.issubset(result.columns):
        result["statut_stock"]=result.apply(lambda r:get_statut_stock(r["stock_actuel"],r["stock_min"]),axis=1)
    if "stock_actuel" in result.columns:
        result["stock_affiche"]=result.apply(lambda r:format_quantity(r.get("stock_actuel",0),r.get("unite","")),axis=1)
    if {"stock_actuel","pu_achat_piece"}.issubset(result.columns):
        result["valeur_stock"]=result.apply(lambda r:calcul_valeur_stock(r["stock_actuel"],r["pu_achat_piece"]),axis=1)
        result["valeur_stock_affiche"]=result["valeur_stock"].apply(format_money)
    if {"stock_actuel","qte_par_carton"}.issubset(result.columns):
        result["cartons_disponibles"]=result.apply(lambda r:calcul_qte_cartons_possible(r["stock_actuel"],r["qte_par_carton"]),axis=1)
    return result

def filter_stock_dataframe(df:pd.DataFrame,statut:str|None=None,categorie:str|None=None)->pd.DataFrame:
    """Filtre un DataFrame de stock."""
    if df.empty:
        return df
    result=add_stock_display_columns(df)
    if statut and "statut_stock" in result.columns:
        result=result[result["statut_stock"].str.upper()==statut.upper()]
    if categorie and "nom_categorie" in result.columns:
        result=result[result["nom_categorie"].astype(str)==categorie]
    return result

def get_stock_resume()->dict[str,Any]:
    """Retourne un resume complet du stock."""
    kpis=get_stock_kpis()
    return {
        "total_produits":int(kpis.get("total_produits",0)),
        "produits_actifs":int(kpis.get("produits_actifs",0)),
        "quantite_stock":float(kpis.get("quantite_stock",0)),
        "stock_faible":int(kpis.get("stock_faible",0)),
        "rupture":int(kpis.get("rupture",0)),
        "valeur_stock":float(kpis.get("valeur_stock",0)),
        "valeur_stock_affiche":format_money(kpis.get("valeur_stock",0))
    }

def get_stock_status_counts()->dict[str,int]:
    """Compte les produits par statut de stock."""
    df=list_stock(active_only=True)
    if df.empty:
        return {"NORMAL":0,"ALERTE":0,"RUPTURE":0}
    df=add_stock_display_columns(df)
    counts=df["statut_stock"].value_counts().to_dict() if "statut_stock" in df.columns else {}
    return {"NORMAL":int(counts.get("NORMAL",0)),"ALERTE":int(counts.get("ALERTE",0)),"RUPTURE":int(counts.get("RUPTURE",0))}

__all__ = [
    "get_stock",
    "get_stock_actuel",
    "list_stock",
    "list_alertes_stock",
    "list_ruptures_stock",
    "get_stock_kpis",
    "get_valeur_stock",
    "set_stock",
    "add_stock",
    "remove_stock",
    "can_sell",
    "can_register_loss",
    "add_stock_display_columns",
    "filter_stock_dataframe",
    "get_stock_resume",
    "get_stock_status_counts",
]
