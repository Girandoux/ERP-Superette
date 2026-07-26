# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/inventaire.py
# ROLE : Services metier pour l'inventaire
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from typing import Any
import logging
import pandas as pd
from database import inventaire_db
from utils.calculs import calcul_ecart_stock,calcul_valeur_ecart
from utils.helpers import clean_text,error_response,format_money,format_quantity,get_date_id,normalize_text,success_response,to_float,to_int
from utils.validation import validate_inventaire,validate_date_range

logger=logging.getLogger("utils")

# ============================================================
# 1. PREPARATION ET VALIDATION DES DONNEES
# ============================================================

def prepare_inventaire_data(date_inventaire:Any,produit_id:Any,stock_physique:Any,commentaire:Any=None,utilisateur:Any="SYSTEM",stock_theorique:Any=0,cout_unitaire:Any=0)->dict[str,Any]:
    """Prepare les donnees d'un inventaire."""
    date_value=get_date_id(date_inventaire)
    stock_phy=to_int(stock_physique)
    stock_theo=to_int(stock_theorique)
    ecart=calcul_ecart_stock(stock_theo,stock_phy)
    return {
        "date_inventaire":date_value,
        "date_id":date_value,
        "produit_id":to_int(produit_id),
        "stock_theorique":stock_theo,
        "stock_physique":stock_phy,
        "ecart":ecart,
        "valeur_ecart":calcul_valeur_ecart(ecart,cout_unitaire),
        "commentaire":clean_text(commentaire) if commentaire else None,
        "utilisateur":clean_text(utilisateur) or "SYSTEM"
    }

def validate_inventaire_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire inventaire."""
    valid,errors=validate_inventaire(data)
    if not valid:
        return error_response("Inventaire invalide",errors)
    return success_response("Inventaire valide",data)

# ============================================================
# 2. OPERATIONS CRUD ET CLOTURE
# ============================================================

def list_inventaires()->pd.DataFrame:
    """Retourne tous les inventaires."""
    return inventaire_db.get_all_inventaires()

def get_inventaire(inventaire_id:int)->dict[str,Any]|None:
    """Retourne un inventaire par ID."""
    return inventaire_db.get_inventaire_by_id(inventaire_id)

def search_inventaires(keyword:Any=None,produit_id:int|None=None)->pd.DataFrame:
    """Recherche les inventaires."""
    return inventaire_db.search_inventaires(keyword=clean_text(keyword) if keyword else None,produit_id=produit_id)

def list_inventaires_by_date(date_debut:Any,date_fin:Any)->pd.DataFrame:
    """Retourne les inventaires sur une periode."""
    ok,message=validate_date_range(date_debut,date_fin)
    if not ok:
        logger.warning(message)
        return pd.DataFrame()
    return inventaire_db.get_inventaires_by_date(get_date_id(date_debut),get_date_id(date_fin))

def create_inventaire(date_inventaire:Any,produit_id:Any,stock_physique:Any,commentaire:Any=None,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Cree un controle inventaire."""
    data=prepare_inventaire_data(date_inventaire,produit_id,stock_physique,commentaire,utilisateur)
    check=validate_inventaire_form(data)
    if not check["success"]:
        return check
    ok=inventaire_db.insert_inventaire(data["date_inventaire"],data["produit_id"],data["stock_physique"],data["commentaire"],data["utilisateur"])
    return success_response("Inventaire cree",data) if ok else error_response("Creation de l'inventaire impossible")

def update_inventaire(inventaire_id:int,date_inventaire:Any,produit_id:Any,stock_physique:Any,commentaire:Any=None,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Modifie un controle inventaire."""
    data=prepare_inventaire_data(date_inventaire,produit_id,stock_physique,commentaire,utilisateur)
    check=validate_inventaire_form(data)
    if not check["success"]:
        return check
    ok=inventaire_db.update_inventaire(inventaire_id,data["date_inventaire"],data["produit_id"],data["stock_physique"],data["commentaire"],data["utilisateur"])
    return success_response("Inventaire modifie",data) if ok else error_response("Modification de l'inventaire impossible")

def delete_inventaire(inventaire_id:int)->dict[str,Any]:
    """Supprime un inventaire."""
    ok=inventaire_db.delete_inventaire(inventaire_id)
    return success_response("Inventaire supprime") if ok else error_response("Suppression de l'inventaire impossible")

def cloturer_inventaire(inventaire_id:int,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Cloture un inventaire et actualise le stock."""
    result=inventaire_db.cloturer_inventaire(inventaire_id,clean_text(utilisateur) or "SYSTEM")
    return success_response(result["message"],result.get("data")) if result.get("success") else error_response(result["message"],result.get("data"))
def cloturer_inventaires_by_date(date_inventaire:Any,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Cloture tous les inventaires ouverts d'une date."""
    result=inventaire_db.cloturer_inventaires_by_date(get_date_id(date_inventaire),clean_text(utilisateur) or "SYSTEM")
    return success_response(result["message"],result.get("data")) if result.get("success") else error_response(result["message"],result.get("data"))

def corriger_inventaire_cloture(inventaire_id:int,nouveau_stock_physique:Any,commentaire:Any=None,utilisateur:Any="SYSTEM")->dict[str,Any]:
    """Cree une correction tracee pour un inventaire cloture."""
    result=inventaire_db.corriger_inventaire_cloture(inventaire_id,to_int(nouveau_stock_physique),commentaire,clean_text(utilisateur) or "SYSTEM")
    return success_response(result["message"],result.get("data")) if result.get("success") else error_response(result["message"],result.get("data"))


# ============================================================
# 3. CONTROLE ET SYNCHRONISATION DU STOCK
# ============================================================

# Le controle compare le stock enregistre avec les mouvements reels
# afin d'identifier les surplus, les manquants et les incoherences.

def list_controle_stock(date_debut:Any,date_fin:Any)->pd.DataFrame:
    """Retourne le controle de coherence du stock sur une periode."""
    ok,message=validate_date_range(date_debut,date_fin)
    if not ok:
        logger.warning(message)
        return pd.DataFrame()
    return inventaire_db.get_controle_stock(get_date_id(date_debut),get_date_id(date_fin))

def synchroniser_stock_controle(date_debut:Any,date_fin:Any)->dict[str,Any]:
    """Synchronise le stock actuel avec le stock theorique attendu du controle."""
    ok,message=validate_date_range(date_debut,date_fin)
    if not ok:
        return error_response(message)
    total=inventaire_db.synchroniser_stock_depuis_controle(get_date_id(date_debut),get_date_id(date_fin))
    return success_response(f"Stock synchronise pour {total} produit(s).",{"total":total})

def get_statut_controle_stock(ecart:Any)->str:
    """Retourne le statut du controle stock."""
    value=to_float(ecart)
    if value==0:
        return "CONFORME"
    if value>0:
        return "SURPLUS"
    return "MANQUANT"

def add_controle_stock_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute les colonnes lisibles du controle stock."""
    if df.empty:
        return df
    result=df.copy()
    numeric_cols=["stock_dernier_inventaire","quantite_achetee","quantite_vendue","quantite_perdue","quantite_perdue_signalee","quantite_perdue_inventaire","stock_theorique_brut","vente_excedentaire","stock_theorique_attendu","stock_actuel","ecart_controle"]
    for col in numeric_cols:
        if col in result.columns:
            result[f"{col}_affiche"]=result[col].apply(format_quantity)
    if "ecart_controle" in result.columns:
        result["statut_controle"]=result["ecart_controle"].apply(get_statut_controle_stock)
    return result

def filter_controle_stock_dataframe(df:pd.DataFrame,keyword:Any="",categorie:Any="Toutes",statut:Any="Tous")->pd.DataFrame:
    """Filtre le controle stock cote interface."""
    if df.empty:
        return df
    result=add_controle_stock_display_columns(df)
    if categorie and categorie!="Toutes" and "nom_categorie" in result.columns:
        result=result[result["nom_categorie"].fillna("")==categorie]
    if statut and statut!="Tous" and "statut_controle" in result.columns:
        result=result[result["statut_controle"].fillna("")==statut]
    keyword=normalize_text(keyword)
    if keyword:
        mask=result.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
        result=result[mask]
    return result

# ============================================================
# 4. ECARTS, ANALYSE ET INDICATEURS
# ============================================================

def list_ecarts_inventaire(include_closed:bool=False)->pd.DataFrame:
    """Retourne les controles avec ecart."""
    return inventaire_db.get_inventaire_ecarts(include_closed=include_closed)

def get_inventaire_history_for_product(produit_id:int,exclude_id:int|None=None,limit:int=10)->pd.DataFrame:
    """Retourne l'historique inventaire d'un produit."""
    return inventaire_db.get_inventaire_history_for_product(produit_id,exclude_id,limit)

def compare_inventaire_with_previous(inventaire_id:int)->dict[str,Any]|None:
    """Compare un inventaire avec le precedent du meme produit."""
    return inventaire_db.compare_inventaire_with_previous(inventaire_id)

def get_inventaire_kpis()->dict[str,Any]:
    """Retourne les KPIs inventaire."""
    return inventaire_db.get_inventaire_kpis()

def add_inventaire_display_columns(df:pd.DataFrame)->pd.DataFrame:
    """Ajoute des colonnes formatees pour Streamlit."""
    if df.empty:
        return df
    result=df.copy()
    for col in ["stock_theorique","stock_physique","ecart"]:
        if col in result.columns:
            result[f"{col}_affiche"]=result[col].apply(format_quantity)
    if "valeur_ecart" in result.columns:
        result["valeur_ecart_affiche"]=result["valeur_ecart"].apply(format_money)
    if "ecart" in result.columns:
        result["statut_ecart"]=result["ecart"].apply(get_statut_ecart)
    if "cloture" in result.columns:
        result["statut_cloture"]=result["cloture"].apply(lambda value: "CLOTURE" if bool(value) else "OUVERT")
    return result

def get_statut_ecart(ecart:Any)->str:
    """Retourne le statut d'un ecart inventaire."""
    value=to_float(ecart)
    if value==0:
        return "CONFORME"
    if value>0:
        return "SURPLUS"
    return "MANQUANT"

def filter_inventaire_dataframe(df:pd.DataFrame,keyword:Any="",statut_ecart:str|None=None)->pd.DataFrame:
    """Filtre un DataFrame inventaire cote interface."""
    if df.empty:
        return df
    result=add_inventaire_display_columns(df)
    if statut_ecart and "statut_ecart" in result.columns:
        result=result[result["statut_ecart"].str.upper()==statut_ecart.upper()]
    keyword=normalize_text(keyword)
    if keyword:
        mask=result.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
        result=result[mask]
    return result

def get_inventaire_resume()->dict[str,Any]:
    """Retourne un resume inventaire."""
    kpis=get_inventaire_kpis()
    return {
        "total_controles":int(kpis.get("total_controles",0)),
        "clotures":int(kpis.get("clotures",0)),
        "conformes":int(kpis.get("conformes",0)),
        "surplus":int(kpis.get("surplus",0)),
        "manquants":int(kpis.get("manquants",0)),
        "total_ecarts":float(kpis.get("total_ecarts",0)),
        "valeur_ecarts":float(kpis.get("valeur_ecarts",0)),
        "valeur_ecarts_affiche":format_money(kpis.get("valeur_ecarts",0))
    }

__all__ = [
    "prepare_inventaire_data",
    "validate_inventaire_form",
    "list_inventaires",
    "get_inventaire",
    "search_inventaires",
    "list_inventaires_by_date",
    "create_inventaire",
    "update_inventaire",
    "delete_inventaire",
    "cloturer_inventaire",
    "cloturer_inventaires_by_date",
    "corriger_inventaire_cloture",
    "list_controle_stock",
    "synchroniser_stock_controle",
    "get_statut_controle_stock",
    "add_controle_stock_display_columns",
    "filter_controle_stock_dataframe",
    "list_ecarts_inventaire",
    "get_inventaire_history_for_product",
    "compare_inventaire_with_previous",
    "get_inventaire_kpis",
    "add_inventaire_display_columns",
    "get_statut_ecart",
    "filter_inventaire_dataframe",
    "get_inventaire_resume",
]
