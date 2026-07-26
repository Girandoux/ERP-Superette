# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/produits.py
# ROLE : Services metier pour les produits
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

from typing import Any
import logging
import pandas as pd
from database import produits_db
from utils.calculs import get_statut_stock
from utils.helpers import clean_text,error_response,format_money,format_quantity,normalize_text,success_response,to_float,to_int
from utils.validation import validate_produit

logger=logging.getLogger("utils")

# ============================================================
# 1. PREPARATION DES DONNEES
# ============================================================


def prepare_produit_data(code_produit:Any,nom_produit:Any,categorie_id:Any,unite:Any,qte_par_carton:Any,stock_min:Any=0,actif:bool=True)->dict[str,Any]:
    """Prepare les donnees d'un produit avant enregistrement."""
    return {
        "code_produit":clean_text(code_produit).upper(),
        "nom_produit":clean_text(nom_produit),
        "categorie_id":to_int(categorie_id),
        "unite":clean_text(unite),
        "qte_par_carton":to_int(qte_par_carton,1),
        "stock_min":to_int(stock_min),
        "actif":bool(actif)
    }

def validate_produit_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire produit."""
    valid,errors=validate_produit(data)
    if not valid:
        return error_response("Produit invalide",errors)
    return success_response("Produit valide",data)

# ============================================================
# 2. OPERATIONS CRUD
# ============================================================


def list_produits(active_only:bool=False)->pd.DataFrame:
    """Retourne les produits."""
    return produits_db.get_all_products(active_only=active_only)

def list_active_produits()->pd.DataFrame:
    """Retourne les produits actifs."""
    return list_produits(active_only=True)

def get_produit(produit_id:int)->dict[str,Any]|None:
    """Retourne un produit par ID."""
    return produits_db.get_product_by_id(produit_id)

def get_produit_by_code(code_produit:Any)->dict[str,Any]|None:
    """Retourne un produit par code."""
    return produits_db.get_product_by_code(clean_text(code_produit).upper())

def get_next_code_produit(categorie_id:Any=None)->str:
    """Retourne le prochain code produit propose pour une categorie."""
    return produits_db.get_next_product_code(to_int(categorie_id) if categorie_id else None)

def search_produits(keyword:Any,active_only:bool=False)->pd.DataFrame:
    """Recherche un produit."""
    keyword=clean_text(keyword)
    return produits_db.search_products(keyword,active_only=active_only) if keyword else pd.DataFrame()

def create_produit(code_produit:Any,nom_produit:Any,categorie_id:Any,unite:Any,qte_par_carton:Any,stock_min:Any=0,actif:bool=True)->dict[str,Any]:
    """Cree un produit."""
    data=prepare_produit_data(code_produit,nom_produit,categorie_id,unite,qte_par_carton,stock_min,actif)
    check=validate_produit_form(data)
    if not check["success"]:
        return check
    ok=produits_db.create_product(data["code_produit"],data["nom_produit"],data["categorie_id"],data["unite"],data["qte_par_carton"],data["stock_min"],data["actif"])
    return success_response("Produit cree",data) if ok else error_response("Creation du produit impossible")

def update_produit(produit_id:int,code_produit:Any,nom_produit:Any,categorie_id:Any,unite:Any,qte_par_carton:Any,stock_min:Any=0,actif:bool=True)->dict[str,Any]:
    """Modifie un produit."""
    data=prepare_produit_data(code_produit,nom_produit,categorie_id,unite,qte_par_carton,stock_min,actif)
    check=validate_produit_form(data)
    if not check["success"]:
        return check
    ok=produits_db.update_product(produit_id,data["code_produit"],data["nom_produit"],data["categorie_id"],data["unite"],data["qte_par_carton"],data["stock_min"],data["actif"])
    return success_response("Produit modifie",data) if ok else error_response("Modification du produit impossible")

def activate_produit(produit_id:int)->dict[str,Any]:
    """Active un produit."""
    ok=produits_db.activate_product(produit_id)
    return success_response("Produit active") if ok else error_response("Activation du produit impossible")

def deactivate_produit(produit_id:int)->dict[str,Any]:
    """Desactive un produit."""
    ok=produits_db.deactivate_product(produit_id)
    return success_response("Produit desactive") if ok else error_response("Desactivation du produit impossible")


def can_delete_produit(produit_id:int)->dict[str,Any]:
    """Verifie si un produit peut etre supprime physiquement."""
    ok,message=produits_db.can_delete_product(produit_id)
    return success_response(message) if ok else error_response(message)

def delete_produit(produit_id:int)->dict[str,Any]:
    """Supprime definitivement un produit non utilise."""
    ok,message=produits_db.can_delete_product(produit_id)
    if not ok:
        return error_response(message)
    deleted=produits_db.delete_product(produit_id)
    return success_response("Produit supprime definitivement") if deleted else error_response("Suppression du produit impossible")

# ============================================================
# 3. STOCK ET AFFICHAGE
# ============================================================


def update_stock_min(produit_id:int,stock_min:Any)->dict[str,Any]:
    """Modifie le stock minimum."""
    stock_min=to_int(stock_min)
    if stock_min<0:
        return error_response("Le stock minimum ne peut pas etre negatif")
    ok=produits_db.update_stock_min(produit_id,stock_min)
    return success_response("Stock minimum modifie") if ok else error_response("Modification du stock minimum impossible")

def set_stock_produit(produit_id:int,nouveau_stock:Any)->dict[str,Any]:
    """Met a jour le stock actuel d'un produit."""
    nouveau_stock=to_int(nouveau_stock)
    if nouveau_stock<0:
        return error_response("Le stock ne peut pas etre negatif")
    ok=produits_db.update_stock(produit_id,nouveau_stock)
    return success_response("Stock modifie") if ok else error_response("Modification du stock impossible")

def add_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute des colonnes formatees pour Streamlit."""
    if df.empty:
        return df
    result=df.copy()
    if {"stock_actuel","stock_min"}.issubset(result.columns):
        result["statut_stock"]=result.apply(lambda r:get_statut_stock(r["stock_actuel"],r["stock_min"]),axis=1)
    if "stock_actuel" in result.columns:
        result["stock_affiche"]=result.apply(lambda r:format_quantity(r.get("stock_actuel",0),r.get("unite","")),axis=1)
    if "valeur_stock" in result.columns:
        result["valeur_stock_affiche"]=result["valeur_stock"].apply(format_money)
    return result

def get_produits_options(active_only:bool=True)->dict[str,int]:
    """Retourne les options selectbox {nom: id}."""
    df=list_produits(active_only=active_only)
    if df.empty:
        return {}
    return {f"{row['code_produit']} - {row['nom_produit']}":int(row["produit_id"]) for _,row in df.iterrows()}

def filter_produits_dataframe(df:pd.DataFrame,keyword:Any="",categorie_id:Any=None,active_only:bool=False)->pd.DataFrame:
    """Filtre un DataFrame de produits cote interface."""
    if df.empty:
        return df
    result=df.copy()
    if active_only and "actif" in result.columns:
        result=result[result["actif"]==True]
    if categorie_id and "categorie_id" in result.columns:
        result=result[result["categorie_id"]==to_int(categorie_id)]
    keyword=normalize_text(keyword)
    if keyword:
        mask=result.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
        result=result[mask]
    return result

def get_produits_kpis(active_only:bool=False)->dict[str,Any]:
    """Retourne les KPIs produits."""
    df=list_produits(active_only=active_only)
    if df.empty:
        return {"total_produits":0,"produits_actifs":0,"stock_total":0,"alertes_stock":0,"ruptures_stock":0}
    stock=df["stock_actuel"].fillna(0) if "stock_actuel" in df.columns else pd.Series(dtype=float)
    stock_min=df["stock_min"].fillna(0) if "stock_min" in df.columns else pd.Series(dtype=float)
    actifs=int(df["actif"].fillna(False).sum()) if "actif" in df.columns else len(df)
    return {
        "total_produits":len(df),
        "produits_actifs":actifs,
        "stock_total":float(stock.sum()) if not stock.empty else 0,
        "alertes_stock":int((stock<=stock_min).sum()) if not stock.empty else 0,
        "ruptures_stock":int((stock<=0).sum()) if not stock.empty else 0
    }

def get_prix_reference(produit:dict[str,Any]|None,default:float=0)->float:
    """Retourne un prix/cout de reference si present dans un produit."""
    if not produit:
        return default
    for key in ("pu_vente","prix_vente","pu_achat_piece","cout_unitaire"):
        if key in produit and produit.get(key) is not None:
            return to_float(produit.get(key),default)
    return default

__all__ = [
    "prepare_produit_data",
    "validate_produit_form",
    "list_produits",
    "list_active_produits",
    "get_produit",
    "get_produit_by_code",
    "get_next_code_produit",
    "search_produits",
    "create_produit",
    "update_produit",
    "activate_produit",
    "deactivate_produit",
    "can_delete_produit",
    "delete_produit",
    "update_stock_min",
    "set_stock_produit",
    "add_display_columns",
    "get_produits_options",
    "filter_produits_dataframe",
    "get_produits_kpis",
    "get_prix_reference",
]
