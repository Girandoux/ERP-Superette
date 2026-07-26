# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/pertes.py
# ROLE : Services metier pour les pertes
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from typing import Any
import logging
import pandas as pd
from database import pertes_db
from utils.calculs import calcul_valeur_perte
from utils.helpers import clean_text,error_response,format_money,format_quantity,get_date_id,normalize_text,success_response,to_float,to_int
from utils.validation import validate_perte,validate_date_range

logger=logging.getLogger("utils")

# ============================================================
# 1. CONSTANTES METIER
# ============================================================

MOTIFS_PERTES=["Perime","Casse","Vole","Don","Inventaire","Consommation_Interne"]

# ============================================================
# 2. PREPARATION ET VALIDATION DES DONNEES
# ============================================================

# Calcule la valeur totale de la perte avant validation et enregistrement.
def prepare_perte_data(date_perte:Any,produit_id:Any,qte_perte:Any,motif_perte:Any,valeur_unitaire:Any,utilisateur:Any="SYSTEM",stock_disponible:Any=None)->dict[str,Any]:
    """Prepare les donnees d'une perte."""
    date_value=get_date_id(date_perte)
    data={
        "date_perte":date_value,
        "date_id":date_value,
        "produit_id":to_int(produit_id),
        "qte_perte":to_int(qte_perte),
        "motif_perte":clean_text(motif_perte),
        "valeur_unitaire":to_float(valeur_unitaire),
        "valeur_totale":calcul_valeur_perte(qte_perte,valeur_unitaire),
        "utilisateur":clean_text(utilisateur) or "SYSTEM"
    }
    if stock_disponible is not None:
        data["stock_disponible"]=to_float(stock_disponible)
    return data

def validate_perte_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire perte."""
    valid,errors=validate_perte(data)
    if not valid:
        return error_response("Perte invalide",errors)
    if data.get("motif_perte") not in MOTIFS_PERTES:
        return error_response("Motif de perte invalide",MOTIFS_PERTES)
    return success_response("Perte valide",data)

# ============================================================
# 3. OPERATIONS CRUD
# ============================================================

def list_pertes()->pd.DataFrame:
    """Retourne toutes les pertes."""
    return pertes_db.get_all_pertes()

def get_perte(perte_id:int)->dict[str,Any]|None:
    """Retourne une perte par ID."""
    return pertes_db.get_perte_by_id(perte_id)

def search_pertes(keyword:Any=None,produit_id:int|None=None,motif_perte:Any=None)->pd.DataFrame:
    """Recherche les pertes."""
    return pertes_db.search_pertes(keyword=clean_text(keyword) if keyword else None,produit_id=produit_id,motif_perte=clean_text(motif_perte) if motif_perte else None)

def list_pertes_by_date(date_debut:Any,date_fin:Any)->pd.DataFrame:
    """Retourne les pertes sur une periode."""
    ok,message=validate_date_range(date_debut,date_fin)
    if not ok:
        logger.warning(message)
        return pd.DataFrame()
    return pertes_db.get_pertes_by_date(get_date_id(date_debut),get_date_id(date_fin))

def create_perte(date_perte:Any,produit_id:Any,qte_perte:Any,motif_perte:Any,valeur_unitaire:Any,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Cree une perte."""
    data=prepare_perte_data(date_perte,produit_id,qte_perte,motif_perte,valeur_unitaire,utilisateur)
    check=validate_perte_form(data)
    if not check["success"]:
        return check
    ok=pertes_db.insert_perte(data["date_perte"],data["produit_id"],data["qte_perte"],data["motif_perte"],data["valeur_unitaire"],data["utilisateur"])
    return success_response("Perte creee",data) if ok else error_response("Creation de la perte impossible")

def update_perte(perte_id:int,date_perte:Any,produit_id:Any,qte_perte:Any,motif_perte:Any,valeur_unitaire:Any,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Modifie une perte."""
    data=prepare_perte_data(date_perte,produit_id,qte_perte,motif_perte,valeur_unitaire,utilisateur)
    check=validate_perte_form(data)
    if not check["success"]:
        return check
    ok=pertes_db.update_perte(perte_id,data["date_perte"],data["produit_id"],data["qte_perte"],data["motif_perte"],data["valeur_unitaire"],data["utilisateur"])
    return success_response("Perte modifiee",data) if ok else error_response("Modification de la perte impossible")

def delete_perte(perte_id:int)->dict[str,Any]:
    """Supprime une perte."""
    ok=pertes_db.delete_perte(perte_id)
    return success_response("Perte supprimee") if ok else error_response("Suppression de la perte impossible")

# ============================================================
# 4. AFFICHAGE, ANALYSE ET INDICATEURS
# ============================================================

def get_pertes_kpis()->dict[str,Any]:
    """Retourne les KPIs pertes."""
    return pertes_db.get_pertes_kpis()

def get_pertes_by_motif()->pd.DataFrame:
    """Retourne les pertes groupees par motif."""
    return pertes_db.get_pertes_by_motif()

# Les colonnes originales restent intactes ; seules des colonnes d'affichage
# sont ajoutees pour l'interface Streamlit.
def add_pertes_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute des colonnes formatees pour Streamlit."""
    if df.empty:
        return df
    result=df.copy()
    for col in ["qte_perte","quantite_perdue"]:
        if col in result.columns:
            result[f"{col}_affiche"]=result[col].apply(format_quantity)
    for col in ["valeur_unitaire","valeur_totale","valeur_perdue"]:
        if col in result.columns:
            result[f"{col}_affiche"]=result[col].apply(format_money)
    return result

def filter_pertes_dataframe(df:pd.DataFrame,keyword:Any="",motif_perte:Any=None)->pd.DataFrame:
    """Filtre un DataFrame pertes cote interface."""
    if df.empty:
        return df
    result=df.copy()
    if motif_perte and "motif_perte" in result.columns:
        result=result[result["motif_perte"].astype(str)==clean_text(motif_perte)]
    keyword=normalize_text(keyword)
    if keyword:
        mask=result.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
        result=result[mask]
    return result

def get_motifs_pertes_options()->list[str]:
    """Retourne les motifs autorises."""
    return MOTIFS_PERTES.copy()

__all__ = [
    "prepare_perte_data",
    "validate_perte_form",
    "list_pertes",
    "get_perte",
    "search_pertes",
    "list_pertes_by_date",
    "create_perte",
    "update_perte",
    "delete_perte",
    "get_pertes_kpis",
    "get_pertes_by_motif",
    "add_pertes_display_columns",
    "filter_pertes_dataframe",
    "get_motifs_pertes_options",
]
