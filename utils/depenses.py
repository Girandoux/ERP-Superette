# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/depenses.py
# ROLE : Services metier pour les depenses
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from typing import Any
import logging
import pandas as pd
from database import depenses_db
from utils.helpers import clean_text,error_response,format_money,get_date_id,normalize_text,success_response,to_float
from utils.validation import validate_depense,validate_date_range

logger=logging.getLogger("utils")

# ============================================================
# 1. CONSTANTES METIER
# ============================================================

CATEGORIES_DEPENSES=["Loyer","Salaire","Transport","Electricite","Eau","Internet","Entretien","Impots","Fournitures","Autre"]

# ============================================================
# 2. PREPARATION ET VALIDATION DES DONNEES
# ============================================================

# Normalise les valeurs saisies avant leur validation et leur enregistrement.
def prepare_depense_data(date_depense:Any,categorie_depense:Any,montant:Any,motif:Any,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Prepare les donnees d'une depense."""
    date_value=get_date_id(date_depense)
    return {
        "date_depense":date_value,
        "date_id":date_value,
        "categorie_depense":clean_text(categorie_depense),
        "montant":to_float(montant),
        "motif":clean_text(motif),
        "utilisateur":clean_text(utilisateur) or "SYSTEM"
    }

def validate_depense_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire depense."""
    valid,errors=validate_depense(data)
    if not valid:
        return error_response("Depense invalide",errors)
    return success_response("Depense valide",data)

# ============================================================
# 3. OPERATIONS CRUD
# ============================================================

def list_depenses()->pd.DataFrame:
    """Retourne toutes les depenses."""
    return depenses_db.get_all_depenses()

def get_depense(depense_id:int)->dict[str,Any]|None:
    """Retourne une depense par ID."""
    return depenses_db.get_depense_by_id(depense_id)

def search_depenses(keyword:Any=None,categorie_depense:Any=None,utilisateur:Any=None)->pd.DataFrame:
    """Recherche les depenses."""
    return depenses_db.search_depenses(keyword=clean_text(keyword) if keyword else None,categorie_depense=clean_text(categorie_depense) if categorie_depense else None,utilisateur=clean_text(utilisateur) if utilisateur else None)

def list_depenses_by_date(date_debut:Any,date_fin:Any)->pd.DataFrame:
    """Retourne les depenses sur une periode."""
    ok,message=validate_date_range(date_debut,date_fin)
    if not ok:
        logger.warning(message)
        return pd.DataFrame()
    return depenses_db.get_depenses_by_date(get_date_id(date_debut),get_date_id(date_fin))

def create_depense(date_depense:Any,categorie_depense:Any,montant:Any,motif:Any,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Cree une depense."""
    data=prepare_depense_data(date_depense,categorie_depense,montant,motif,utilisateur)
    check=validate_depense_form(data)
    if not check["success"]:
        return check
    ok=depenses_db.insert_depense(data["date_depense"],data["categorie_depense"],data["montant"],data["motif"],data["utilisateur"])
    return success_response("Depense creee",data) if ok else error_response("Creation de la depense impossible")

def update_depense(depense_id:int,date_depense:Any,categorie_depense:Any,montant:Any,motif:Any,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Modifie une depense."""
    data=prepare_depense_data(date_depense,categorie_depense,montant,motif,utilisateur)
    check=validate_depense_form(data)
    if not check["success"]:
        return check
    ok=depenses_db.update_depense(depense_id,data["date_depense"],data["categorie_depense"],data["montant"],data["motif"],data["utilisateur"])
    return success_response("Depense modifiee",data) if ok else error_response("Modification de la depense impossible")

def delete_depense(depense_id:int)->dict[str,Any]:
    """Supprime une depense."""
    ok=depenses_db.delete_depense(depense_id)
    return success_response("Depense supprimee") if ok else error_response("Suppression de la depense impossible")

# ============================================================
# 4. AFFICHAGE, ANALYSE ET INDICATEURS
# ============================================================

def get_depenses_kpis()->dict[str,Any]:
    """Retourne les KPIs depenses."""
    return depenses_db.get_depenses_kpis()

def get_depenses_by_category()->pd.DataFrame:
    """Retourne les depenses groupees par categorie."""
    return depenses_db.get_depenses_by_category()

def get_monthly_depenses()->pd.DataFrame:
    """Retourne les depenses mensuelles."""
    return depenses_db.get_monthly_depenses()

# Les montants bruts sont conserves et des colonnes formatees sont ajoutees
# uniquement pour l'affichage dans Streamlit.
def add_depenses_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute des colonnes formatees pour Streamlit."""
    if df.empty:
        return df
    result=df.copy()
    if "montant" in result.columns:
        result["montant_affiche"]=result["montant"].apply(format_money)
    if "montant_total" in result.columns:
        result["montant_total_affiche"]=result["montant_total"].apply(format_money)
    return result

def filter_depenses_dataframe(df:pd.DataFrame,keyword:Any="",categorie_depense:Any=None)->pd.DataFrame:
    """Filtre un DataFrame depenses cote interface."""
    if df.empty:
        return df
    result=df.copy()
    if categorie_depense and "categorie_depense" in result.columns:
        result=result[result["categorie_depense"].astype(str)==clean_text(categorie_depense)]
    keyword=normalize_text(keyword)
    if keyword:
        mask=result.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
        result=result[mask]
    return result

def get_categories_depenses_options()->list[str]:
    """Retourne les categories de depenses conseillees."""
    return CATEGORIES_DEPENSES.copy()

__all__ = [
    "prepare_depense_data",
    "validate_depense_form",
    "list_depenses",
    "get_depense",
    "search_depenses",
    "list_depenses_by_date",
    "create_depense",
    "update_depense",
    "delete_depense",
    "get_depenses_kpis",
    "get_depenses_by_category",
    "get_monthly_depenses",
    "add_depenses_display_columns",
    "filter_depenses_dataframe",
    "get_categories_depenses_options",
]
