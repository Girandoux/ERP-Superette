# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/tresorerie.py
# ROLE : Services metier pour la tresorerie
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from typing import Any
import logging
import pandas as pd
from database import tresorerie_db
from utils.helpers import clean_text,error_response,format_money,get_date_id,normalize_text,success_response,to_float
from utils.validation import validate_tresorerie,validate_date_range

logger=logging.getLogger("utils")

# ============================================================
# 1. CONSTANTES METIER
# ============================================================

TYPES_MOUVEMENTS=["Apport","Retrait","Depot_Banque","Retrait_Banque","Correction"]
TYPES_ENTREE={"Apport","Depot_Banque","Correction"}
TYPES_SORTIE={"Retrait","Retrait_Banque"}

# ============================================================
# 2. PREPARATION ET VALIDATION DES DONNEES
# ============================================================

def prepare_mouvement_data(date_mouvement:Any,type_mouvement:Any,montant:Any,description:Any=None,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Prepare les donnees d'un mouvement de tresorerie."""
    date_value=get_date_id(date_mouvement)
    return {
        "date_mouvement":date_value,
        "date_id":date_value,
        "type_mouvement":clean_text(type_mouvement),
        "montant":to_float(montant),
        "description":clean_text(description) if description else None,
        "utilisateur":clean_text(utilisateur) or "SYSTEM"
    }

def validate_mouvement_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire tresorerie."""
    valid,errors=validate_tresorerie(data)
    if not valid:
        return error_response("Mouvement invalide",errors)
    if data.get("type_mouvement") not in TYPES_MOUVEMENTS:
        return error_response("Type de mouvement invalide",TYPES_MOUVEMENTS)
    return success_response("Mouvement valide",data)

# ============================================================
# 3. OPERATIONS CRUD
# ============================================================

def list_mouvements()->pd.DataFrame:
    """Retourne tous les mouvements."""
    return tresorerie_db.get_all_mouvements()

def get_mouvement(mouvement_id:int)->dict[str,Any]|None:
    """Retourne un mouvement par ID."""
    return tresorerie_db.get_mouvement_by_id(mouvement_id)

def search_mouvements(keyword:Any=None,type_mouvement:Any=None,utilisateur:Any=None)->pd.DataFrame:
    """Recherche les mouvements."""
    return tresorerie_db.search_mouvements(keyword=clean_text(keyword) if keyword else None,type_mouvement=clean_text(type_mouvement) if type_mouvement else None,utilisateur=clean_text(utilisateur) if utilisateur else None)

def list_mouvements_by_date(date_debut:Any,date_fin:Any)->pd.DataFrame:
    """Retourne les mouvements sur une periode."""
    ok,message=validate_date_range(date_debut,date_fin)
    if not ok:
        logger.warning(message)
        return pd.DataFrame()
    return tresorerie_db.get_mouvements_by_date(get_date_id(date_debut),get_date_id(date_fin))

def create_mouvement(date_mouvement:Any,type_mouvement:Any,montant:Any,description:Any=None,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Cree un mouvement de tresorerie."""
    data=prepare_mouvement_data(date_mouvement,type_mouvement,montant,description,utilisateur)
    check=validate_mouvement_form(data)
    if not check["success"]:
        return check
    ok=tresorerie_db.insert_mouvement(data["date_mouvement"],data["type_mouvement"],data["montant"],data["description"],data["utilisateur"])
    return success_response("Mouvement cree",data) if ok else error_response("Creation du mouvement impossible")

def update_mouvement(mouvement_id:int,date_mouvement:Any,type_mouvement:Any,montant:Any,description:Any=None,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Modifie un mouvement de tresorerie."""
    data=prepare_mouvement_data(date_mouvement,type_mouvement,montant,description,utilisateur)
    check=validate_mouvement_form(data)
    if not check["success"]:
        return check
    ok=tresorerie_db.update_mouvement(mouvement_id,data["date_mouvement"],data["type_mouvement"],data["montant"],data["description"],data["utilisateur"])
    return success_response("Mouvement modifie",data) if ok else error_response("Modification du mouvement impossible")

def delete_mouvement(mouvement_id:int)->dict[str,Any]:
    """Supprime un mouvement."""
    ok=tresorerie_db.delete_mouvement(mouvement_id)
    return success_response("Mouvement supprime") if ok else error_response("Suppression du mouvement impossible")

# ============================================================
# 4. AFFICHAGE, ANALYSE ET INDICATEURS
# ============================================================

def get_solde_tresorerie()->float:
    """Retourne le solde de tresorerie."""
    return tresorerie_db.get_solde_tresorerie()

def get_tresorerie_kpis()->dict[str,Any]:
    """Retourne les KPIs tresorerie."""
    kpis=tresorerie_db.get_tresorerie_kpis()
    kpis["solde_affiche"] = format_money(kpis.get("solde", 0))
    kpis["entrees_reelles_affiche"] = format_money(kpis.get("entrees_reelles", 0))
    kpis["sorties_reelles_affiche"] = format_money(kpis.get("sorties_reelles", 0))
    kpis["solde_reel_caisse_affiche"] = format_money(kpis.get("solde_reel_caisse", 0))
    return kpis

def get_mouvements_by_type()->pd.DataFrame:
    """Retourne les mouvements groupes par type."""
    return tresorerie_db.get_mouvements_by_type()

def get_monthly_tresorerie()->pd.DataFrame:
    """Retourne les mouvements mensuels."""
    return tresorerie_db.get_monthly_tresorerie()

# Le signe permet de distinguer les entrees et les sorties de caisse.
def get_signe_mouvement(type_mouvement:Any)->int:
    """Retourne le signe financier d'un type de mouvement."""
    type_value=clean_text(type_mouvement)
    if type_value in TYPES_SORTIE:
        return -1
    return 1 if type_value in TYPES_ENTREE else 0

def add_tresorerie_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute des colonnes formatees pour Streamlit."""
    if df.empty:
        return df
    result=df.copy()
    if "montant" in result.columns:
        result["montant_affiche"]=result["montant"].apply(format_money)
        if "type_mouvement" in result.columns:
            result["sens"]=result["type_mouvement"].apply(lambda v:"Sortie" if get_signe_mouvement(v)<0 else "Entree")
            result["montant_signe"]=result.apply(lambda r:to_float(r["montant"])*get_signe_mouvement(r["type_mouvement"]),axis=1)
    if "montant_total" in result.columns:
        result["montant_total_affiche"]=result["montant_total"].apply(format_money)
    return result

def filter_tresorerie_dataframe(df:pd.DataFrame,keyword:Any="",type_mouvement:Any=None)->pd.DataFrame:
    """Filtre un DataFrame tresorerie cote interface."""
    if df.empty:
        return df
    result=df.copy()
    if type_mouvement and "type_mouvement" in result.columns:
        result=result[result["type_mouvement"].astype(str)==clean_text(type_mouvement)]
    keyword=normalize_text(keyword)
    if keyword:
        mask=result.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
        result=result[mask]
    return result

def get_types_mouvements_options()->list[str]:
    """Retourne les types autorises."""
    return TYPES_MOUVEMENTS.copy()

__all__ = [
    "prepare_mouvement_data",
    "validate_mouvement_form",
    "list_mouvements",
    "get_mouvement",
    "search_mouvements",
    "list_mouvements_by_date",
    "create_mouvement",
    "update_mouvement",
    "delete_mouvement",
    "get_solde_tresorerie",
    "get_tresorerie_kpis",
    "get_mouvements_by_type",
    "get_monthly_tresorerie",
    "get_signe_mouvement",
    "add_tresorerie_display_columns",
    "filter_tresorerie_dataframe",
    "get_types_mouvements_options",
]
