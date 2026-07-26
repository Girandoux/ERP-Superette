# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/ventes.py
# ROLE : Services metier pour les ventes et lignes de vente
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

from typing import Any
import logging
import pandas as pd
from database import ventes_db,lignes_vente_db
from utils.calculs import calcul_ligne_vente,calcul_total_vente
from utils.helpers import clean_text,error_response,format_money,get_date_id,normalize_text,success_response,to_float,to_int
from utils.validation import validate_vente,validate_ligne_vente,validate_date_range

logger=logging.getLogger("utils")

# ============================================================
# 1. PREPARATION DES DONNEES
# ============================================================


def prepare_vente_data(date_vente:Any,vendeur_id:Any)->dict[str,Any]:
    """Prepare les donnees d'une vente."""
    date_value=get_date_id(date_vente)
    return {"date_vente":date_value,"date_id":date_value,"vendeur_id":to_int(vendeur_id)}

def prepare_ligne_vente_data(vente_id:Any,produit_id:Any,qte_vente:Any,pu_vente:Any,cout_unitaire:Any=None,stock_disponible:Any=None,type_vente:Any="Normale")->dict[str,Any]:
    """Prepare les donnees d'une ligne de vente."""
    cout=None if cout_unitaire in (None,"") else to_float(cout_unitaire)
    calculs=calcul_ligne_vente(qte_vente,pu_vente,cout or 0)
    data={
        "vente_id":to_int(vente_id),
        "produit_id":to_int(produit_id),
        "qte_vente":to_int(qte_vente),
        "pu_vente":to_float(pu_vente),
        "cout_unitaire":cout,
        "montant_ligne":calculs["montant_ligne"],
        "cout_total":calculs["cout_total"],
        "marge":calculs["marge"],
        "taux_marge":calculs["taux_marge"],
        "type_vente":clean_text(type_vente) or "Normale"
    }
    if stock_disponible is not None:
        data["stock_disponible"]=to_float(stock_disponible)
    return data

def validate_vente_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire vente."""
    valid,errors=validate_vente(data)
    if not valid:
        return error_response("Vente invalide",errors)
    return success_response("Vente valide",data)

def validate_ligne_vente_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire ligne de vente."""
    valid,errors=validate_ligne_vente(data)
    if not valid:
        return error_response("Ligne de vente invalide",errors)
    return success_response("Ligne de vente valide",data)

# ============================================================
# 2. VENTES
# ============================================================


def list_ventes()->pd.DataFrame:
    """Retourne toutes les ventes."""
    return ventes_db.get_all_ventes()

def get_vente(vente_id:int)->dict[str,Any]|None:
    """Retourne une vente par ID."""
    return ventes_db.get_vente_by_id(vente_id)

def get_last_vente()->dict[str,Any]|None:
    """Retourne la derniere vente."""
    return ventes_db.get_last_vente()

def search_ventes(keyword:Any)->pd.DataFrame:
    """Recherche une vente."""
    keyword=clean_text(keyword)
    return ventes_db.search_ventes(keyword) if keyword else pd.DataFrame()

def list_ventes_by_vendeur(vendeur_id:int)->pd.DataFrame:
    """Retourne les ventes d'un vendeur."""
    return ventes_db.get_ventes_by_vendeur(vendeur_id)

def list_ventes_by_date(date_debut:Any,date_fin:Any)->pd.DataFrame:
    """Retourne les ventes sur une periode."""
    ok,message=validate_date_range(date_debut,date_fin)
    if not ok:
        logger.warning(message)
        return pd.DataFrame()
    return ventes_db.get_ventes_by_date(get_date_id(date_debut),get_date_id(date_fin))

def create_vente(date_vente:Any,vendeur_id:Any)->dict[str,Any]:
    """Cree une vente."""
    data=prepare_vente_data(date_vente,vendeur_id)
    check=validate_vente_form(data)
    if not check["success"]:
        return check
    valid,message=ventes_db.can_save_vente(data["date_vente"],data["vendeur_id"])
    if not valid:
        return error_response(message,data)
    ok=ventes_db.create_vente(data["date_vente"],data["vendeur_id"])
    return success_response("Vente creee",data) if ok else error_response("Creation de la vente impossible")

def update_vente(vente_id:int,date_vente:Any,vendeur_id:Any)->dict[str,Any]:
    """Modifie une vente."""
    data=prepare_vente_data(date_vente,vendeur_id)
    check=validate_vente_form(data)
    if not check["success"]:
        return check
    valid,message=ventes_db.can_save_vente(data["date_vente"],data["vendeur_id"])
    if not valid:
        return error_response(message,data)
    ok=ventes_db.update_vente(vente_id,data["date_vente"],data["vendeur_id"])
    return success_response("Vente modifiee",data) if ok else error_response("Modification de la vente impossible")

def delete_vente(vente_id:int)->dict[str,Any]:
    """Supprime une vente."""
    valid,message=ventes_db.can_delete_vente(vente_id)
    if not valid:
        return error_response(message)
    ok=ventes_db.delete_vente(vente_id)
    return success_response("Vente supprimee") if ok else error_response("Suppression de la vente impossible")

# ============================================================
# 3. LIGNES DE VENTE
# ============================================================


def list_lignes_vente()->pd.DataFrame:
    """Retourne toutes les lignes de vente."""
    return lignes_vente_db.get_all_lignes_vente()

def list_lignes_by_vente(vente_id:int)->pd.DataFrame:
    """Retourne les lignes d'une vente."""
    return lignes_vente_db.get_lignes_by_vente(vente_id)

def get_ligne_vente(ligne_vente_id:int)->dict[str,Any]|None:
    """Retourne une ligne de vente."""
    return lignes_vente_db.get_ligne_vente_by_id(ligne_vente_id)


def get_last_sale_price_before_sale(produit_id:Any,vente_id:Any=None,date_vente:Any=None,exclude_ligne_id:Any=None)->float:
    """Retourne le dernier prix de vente avant la date de vente."""
    return float(lignes_vente_db.get_last_sale_price_before_sale(
        to_int(produit_id),
        to_int(vente_id) if vente_id else None,
        get_date_id(date_vente) if date_vente else None,
        to_int(exclude_ligne_id) if exclude_ligne_id else None
    ) or 0)

def get_last_purchase_cost_before_sale(produit_id:Any,vente_id:Any=None,date_vente:Any=None)->float:
    """Retourne le dernier cout d'achat avant la date de vente."""
    return float(lignes_vente_db.get_last_purchase_cost_before_sale(to_int(produit_id),to_int(vente_id) if vente_id else None,get_date_id(date_vente) if date_vente else None) or 0)

def search_lignes_vente(vente_id:int|None=None,produit_id:int|None=None,keyword:Any=None,start_date:Any=None,end_date:Any=None)->pd.DataFrame:
    """Recherche les lignes de vente."""
    return lignes_vente_db.search_lignes_vente(
        vente_id=vente_id,
        produit_id=produit_id,
        keyword=clean_text(keyword) if keyword else None,
        start_date=get_date_id(start_date) if start_date else None,
        end_date=get_date_id(end_date) if end_date else None
    )

def create_ligne_vente(vente_id:Any,produit_id:Any,qte_vente:Any,pu_vente:Any,cout_unitaire:Any=None,type_vente:Any="Normale")->dict[str,Any]:
    """Cree une ligne de vente."""
    data=prepare_ligne_vente_data(vente_id,produit_id,qte_vente,pu_vente,cout_unitaire,type_vente=type_vente)
    check=validate_ligne_vente_form(data)
    if not check["success"]:
        return check
    valid,message=lignes_vente_db.validate_ligne_vente_data(data["vente_id"],data["produit_id"],data["qte_vente"],data["pu_vente"],data["cout_unitaire"],type_vente=data["type_vente"])
    if not valid:
        return error_response(message,data)
    if lignes_vente_db.product_already_in_vente(data["vente_id"],data["produit_id"],type_vente=data["type_vente"]):
        return error_response("Ce produit existe deja dans cette vente.",data)
    ok=lignes_vente_db.create_ligne_vente(data["vente_id"],data["produit_id"],data["qte_vente"],data["pu_vente"],data["cout_unitaire"],data["type_vente"])
    return success_response("Ligne de vente creee",data) if ok else error_response("Creation de la ligne de vente impossible")

def update_ligne_vente(ligne_vente_id:int,vente_id:Any,produit_id:Any,qte_vente:Any,pu_vente:Any,cout_unitaire:Any=None,type_vente:Any="Normale")->dict[str,Any]:
    """Modifie une ligne de vente."""
    data=prepare_ligne_vente_data(vente_id,produit_id,qte_vente,pu_vente,cout_unitaire,type_vente=type_vente)
    check=validate_ligne_vente_form(data)
    if not check["success"]:
        return check
    old_line=lignes_vente_db.get_ligne_vente_by_id(ligne_vente_id)
    old_qte=int(old_line.get("qte_vente",0)) if old_line else 0
    old_produit_id=old_line.get("produit_id") if old_line else None
    valid,message=lignes_vente_db.validate_ligne_vente_data(data["vente_id"],data["produit_id"],data["qte_vente"],data["pu_vente"],data["cout_unitaire"],old_qte=old_qte,old_produit_id=old_produit_id,type_vente=data["type_vente"])
    if not valid:
        return error_response(message,data)
    if lignes_vente_db.product_already_in_vente(data["vente_id"],data["produit_id"],exclude_id=ligne_vente_id,type_vente=data["type_vente"]):
        return error_response("Ce produit existe deja dans cette vente.",data)
    ok=lignes_vente_db.update_ligne_vente(ligne_vente_id,data["vente_id"],data["produit_id"],data["qte_vente"],data["pu_vente"],data["cout_unitaire"],data["type_vente"])
    return success_response("Ligne de vente modifiee",data) if ok else error_response("Modification de la ligne de vente impossible")

def delete_ligne_vente(ligne_vente_id:int)->dict[str,Any]:
    """Supprime une ligne de vente."""
    ok=lignes_vente_db.delete_ligne_vente(ligne_vente_id)
    return success_response("Ligne de vente supprimee") if ok else error_response("Suppression de la ligne de vente impossible")

# ============================================================
# 4. AFFICHAGE ET KPIS
# ============================================================


def add_ventes_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute des colonnes formatees pour Streamlit."""
    if df.empty:
        return df
    result=df.copy()
    for col in ["total_vente","montant_ligne","pu_vente","cout_unitaire","cout_total","marge"]:
        if col in result.columns:
            result[f"{col}_affiche"]=result[col].apply(format_money)
    return result

def filter_ventes_dataframe(df:pd.DataFrame,keyword:Any="")->pd.DataFrame:
    """Filtre un DataFrame vente cote interface."""
    keyword=normalize_text(keyword)
    if df.empty or not keyword:
        return df
    mask=df.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
    return df[mask]

def get_ventes_kpis()->dict[str,Any]:
    """Retourne les KPIs ventes."""
    return ventes_db.get_ventes_kpis()

def get_lignes_vente_kpis()->dict[str,Any]:
    """Retourne les KPIs des lignes de vente."""
    stats=lignes_vente_db.get_lignes_vente_statistics()
    return {
        "total_lignes":int(stats.get("total_lignes",0)),
        "total_quantite":float(stats.get("total_quantite",0)),
        "chiffre_affaires":float(stats.get("chiffre_affaires",0)),
        "cout_total":float(stats.get("cout_total",0)),
        "marge_brute":float(stats.get("marge_brute",0)),
        "prix_moyen":float(stats.get("prix_moyen",0))
    }

def calculate_preview_total(lignes:list[dict[str,Any]])->float:
    """Calcule un total vente avant enregistrement."""
    return calcul_total_vente(lignes)

__all__ = [
    "prepare_vente_data",
    "prepare_ligne_vente_data",
    "validate_vente_form",
    "validate_ligne_vente_form",
    "list_ventes",
    "get_vente",
    "get_last_vente",
    "search_ventes",
    "list_ventes_by_vendeur",
    "list_ventes_by_date",
    "create_vente",
    "update_vente",
    "delete_vente",
    "list_lignes_vente",
    "list_lignes_by_vente",
    "get_ligne_vente",
    "get_last_sale_price_before_sale",
    "get_last_purchase_cost_before_sale",
    "search_lignes_vente",
    "create_ligne_vente",
    "update_ligne_vente",
    "delete_ligne_vente",
    "add_ventes_display_columns",
    "filter_ventes_dataframe",
    "get_ventes_kpis",
    "get_lignes_vente_kpis",
    "calculate_preview_total",
]
