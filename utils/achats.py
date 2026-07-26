# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/achats.py
# ROLE : Services metier pour les achats et lignes d'achat
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

from typing import Any
import logging
import pandas as pd
from database import achats_db,lignes_achat_db
from utils.calculs import calcul_ligne_achat,calcul_total_facture
from utils.helpers import clean_text,error_response,format_money,get_date_id,normalize_text,parse_date,success_response,to_float,to_int
from utils.validation import validate_achat,validate_ligne_achat,validate_date_range

logger=logging.getLogger("utils")

# ============================================================
# 1. PREPARATION DES DONNEES
# ============================================================


def prepare_achat_data(date_achat:Any,numero_facture:Any,acheteur_id:Any,frais_enlevement:Any=0,type_achat:Any="Achat fournisseur")->dict[str,Any]:
    """Prepare les donnees d'un achat."""
    date_value=get_date_id(date_achat)
    return {"date_achat":date_value,"date_id":date_value,"numero_facture":clean_text(numero_facture).upper(),"acheteur_id":to_int(acheteur_id),"frais_enlevement":to_float(frais_enlevement),"type_achat":clean_text(type_achat) or "Achat fournisseur"}

def prepare_ligne_achat_data(achat_id:Any,produit_id:Any,qte_cartons:Any,qte_par_carton:Any,pu_achat_carton:Any,date_fabrication:Any=None,date_peremption:Any=None)->dict[str,Any]:
    """Prepare les donnees d'une ligne d'achat."""
    calculs=calcul_ligne_achat(qte_cartons,qte_par_carton,pu_achat_carton)
    return {
        "achat_id":to_int(achat_id),"produit_id":to_int(produit_id),"qte_cartons":to_float(qte_cartons),"qte_par_carton":to_int(qte_par_carton),
        "quantite_achat":calculs["quantite_achat"],"pu_achat_carton":to_float(pu_achat_carton),"pu_achat_piece":calculs["pu_achat_piece"],"total_achat":calculs["total_achat"],
        "date_fabrication":parse_date(date_fabrication),"date_peremption":parse_date(date_peremption)
    }

def validate_achat_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire achat."""
    valid,errors=validate_achat(data)
    if not valid:
        return error_response("Achat invalide",errors)
    return success_response("Achat valide",data)

def validate_ligne_achat_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire ligne d'achat."""
    valid,errors=validate_ligne_achat(data)
    if not valid:
        return error_response("Ligne d'achat invalide",errors)
    return success_response("Ligne d'achat valide",data)

# ============================================================
# 2. ACHATS
# ============================================================


def list_achats()->pd.DataFrame:
    """Retourne tous les achats."""
    return achats_db.get_all_achats()

def get_achat(achat_id:int)->dict[str,Any]|None:
    """Retourne un achat par ID."""
    return achats_db.get_achat_by_id(achat_id)

def get_next_numero_facture()->str:
    """Retourne le prochain numero de facture propose."""
    return achats_db.get_next_numero_facture()

def get_last_achat()->dict[str,Any]|None:
    """Retourne le dernier achat."""
    return achats_db.get_last_achat()

def search_achats(keyword:Any)->pd.DataFrame:
    """Recherche une facture d'achat."""
    keyword=clean_text(keyword)
    return achats_db.search_achats(keyword) if keyword else pd.DataFrame()

def list_achats_by_acheteur(acheteur_id:int)->pd.DataFrame:
    """Retourne les achats d'un acheteur."""
    return achats_db.get_achats_by_acheteur(acheteur_id)

def list_achats_by_date(date_debut:Any,date_fin:Any)->pd.DataFrame:
    """Retourne les achats sur une periode."""
    ok,message=validate_date_range(date_debut,date_fin)
    if not ok:
        logger.warning(message)
        return pd.DataFrame()
    return achats_db.get_achats_by_date(get_date_id(date_debut),get_date_id(date_fin))

def create_achat(date_achat:Any,numero_facture:Any,acheteur_id:Any,frais_enlevement:Any=0,type_achat:Any="Achat fournisseur")->dict[str,Any]:
    """Cree une facture d'achat."""
    data=prepare_achat_data(date_achat,numero_facture,acheteur_id,frais_enlevement,type_achat)
    check=validate_achat_form(data)
    if not check["success"]:
        return check
    valid,message=achats_db.can_save_achat(data["date_achat"],data["numero_facture"],data["acheteur_id"],data["frais_enlevement"],data["type_achat"])
    if not valid:
        return error_response(message,data)
    ok=achats_db.create_achat(data["date_achat"],data["numero_facture"],data["acheteur_id"],data["frais_enlevement"],data["type_achat"])
    return success_response("Achat cree",data) if ok else error_response("Creation de l'achat impossible")

def update_achat(achat_id:int,date_achat:Any,numero_facture:Any,acheteur_id:Any,frais_enlevement:Any=0,type_achat:Any="Achat fournisseur")->dict[str,Any]:
    """Modifie une facture d'achat."""
    data=prepare_achat_data(date_achat,numero_facture,acheteur_id,frais_enlevement,type_achat)
    check=validate_achat_form(data)
    if not check["success"]:
        return check
    valid,message=achats_db.can_save_achat(data["date_achat"],data["numero_facture"],data["acheteur_id"],data["frais_enlevement"],data["type_achat"],exclude_id=achat_id)
    if not valid:
        return error_response(message,data)
    ok=achats_db.update_achat(achat_id,data["date_achat"],data["numero_facture"],data["acheteur_id"],data["frais_enlevement"],data["type_achat"])
    return success_response("Achat modifie",data) if ok else error_response("Modification de l'achat impossible")

def delete_achat(achat_id:int)->dict[str,Any]:
    """Supprime une facture d'achat."""
    valid,message=achats_db.can_delete_achat(achat_id)
    if not valid:
        return error_response(message)
    ok=achats_db.delete_achat(achat_id)
    return success_response("Achat supprime") if ok else error_response("Suppression de l'achat impossible")

# ============================================================
# 3. LIGNES D'ACHAT
# ============================================================


def list_lignes_achat()->pd.DataFrame:
    """Retourne toutes les lignes d'achat."""
    return lignes_achat_db.get_all_lignes_achat()

def list_lignes_by_achat(achat_id:int)->pd.DataFrame:
    """Retourne les lignes d'un achat."""
    return lignes_achat_db.get_lignes_by_achat(achat_id)

def list_lignes_achat_incoherentes()->pd.DataFrame:
    """Retourne les lignes d'achat qui ne respectent pas les formules metier."""
    return lignes_achat_db.get_lignes_achat_incoherentes()

def get_ligne_achat(ligne_achat_id:int)->dict[str,Any]|None:
    """Retourne une ligne d'achat."""
    return lignes_achat_db.get_ligne_achat_by_id(ligne_achat_id)

def search_lignes_achat(achat_id:int|None=None,produit_id:int|None=None,keyword:Any=None,start_date:Any=None,end_date:Any=None)->pd.DataFrame:
    """Recherche les lignes d'achat."""
    return lignes_achat_db.search_lignes_achat(achat_id=achat_id,produit_id=produit_id,keyword=clean_text(keyword) if keyword else None,start_date=get_date_id(start_date) if start_date else None,end_date=get_date_id(end_date) if end_date else None)

def create_ligne_achat(achat_id:Any,produit_id:Any,qte_cartons:Any,qte_par_carton:Any,pu_achat_carton:Any,date_fabrication:Any=None,date_peremption:Any=None)->dict[str,Any]:
    """Cree une ligne d'achat."""
    data=prepare_ligne_achat_data(achat_id,produit_id,qte_cartons,qte_par_carton,pu_achat_carton,date_fabrication,date_peremption)
    check=validate_ligne_achat_form(data)
    if not check["success"]:
        return check
    ok=lignes_achat_db.create_ligne_achat(data["achat_id"],data["produit_id"],data["qte_cartons"],data["qte_par_carton"],data["pu_achat_carton"],data["date_fabrication"],data["date_peremption"])
    return success_response("Ligne d'achat creee",data) if ok else error_response("Creation de la ligne d'achat impossible")

def update_ligne_achat(ligne_achat_id:int,achat_id:Any,produit_id:Any,qte_cartons:Any,qte_par_carton:Any,pu_achat_carton:Any,date_fabrication:Any=None,date_peremption:Any=None)->dict[str,Any]:
    """Modifie une ligne d'achat."""
    data=prepare_ligne_achat_data(achat_id,produit_id,qte_cartons,qte_par_carton,pu_achat_carton,date_fabrication,date_peremption)
    check=validate_ligne_achat_form(data)
    if not check["success"]:
        return check
    ok=lignes_achat_db.update_ligne_achat(ligne_achat_id,data["achat_id"],data["produit_id"],data["qte_cartons"],data["qte_par_carton"],data["pu_achat_carton"],data["date_fabrication"],data["date_peremption"])
    return success_response("Ligne d'achat modifiee",data) if ok else error_response("Modification de la ligne d'achat impossible")

def delete_ligne_achat(ligne_achat_id:int)->dict[str,Any]:
    """Supprime une ligne d'achat."""
    ok=lignes_achat_db.delete_ligne_achat(ligne_achat_id)
    return success_response("Ligne d'achat supprimee") if ok else error_response("Suppression de la ligne d'achat impossible")

# ============================================================
# 4. AFFICHAGE ET KPIS
# ============================================================


def add_achats_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute des colonnes formatees pour Streamlit."""
    if df.empty:
        return df
    result=df.copy()
    for col in ["frais_enlevement","total_facture","total_achat","pu_achat_carton","pu_achat_piece"]:
        if col in result.columns:
            result[f"{col}_affiche"]=result[col].apply(format_money)
    return result

def filter_achats_dataframe(df:pd.DataFrame,keyword:Any="")->pd.DataFrame:
    """Filtre un DataFrame achat cote interface."""
    keyword=normalize_text(keyword)
    if df.empty or not keyword:
        return df
    mask=df.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
    return df[mask]

def get_achats_kpis()->dict[str,Any]:
    """Retourne les KPIs achats."""
    stats=achats_db.get_achats_statistics()
    return {"total_achats":int(stats.get("total_achats",0)),"montant_total":float(stats.get("montant_total",0)),"montant_moyen":float(stats.get("montant_moyen",0)),"montant_max":float(stats.get("montant_max",0)),"montant_min":float(stats.get("montant_min",0)),"premier_achat":stats.get("premier_achat"),"dernier_achat":stats.get("dernier_achat")}

def calculate_preview_total(lignes:list[dict[str,Any]],frais_enlevement:Any=0)->float:
    """Calcule un total achat avant enregistrement."""
    return calcul_total_facture(lignes,frais_enlevement)

__all__ = [
    "prepare_achat_data",
    "prepare_ligne_achat_data",
    "validate_achat_form",
    "validate_ligne_achat_form",
    "list_achats",
    "get_achat",
    "get_next_numero_facture",
    "get_last_achat",
    "search_achats",
    "list_achats_by_acheteur",
    "list_achats_by_date",
    "create_achat",
    "update_achat",
    "delete_achat",
    "list_lignes_achat",
    "list_lignes_by_achat",
    "list_lignes_achat_incoherentes",
    "get_ligne_achat",
    "search_lignes_achat",
    "create_ligne_achat",
    "update_ligne_achat",
    "delete_ligne_achat",
    "add_achats_display_columns",
    "filter_achats_dataframe",
    "get_achats_kpis",
    "calculate_preview_total",
]
