# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/categories.py
# ROLE : Services metier pour les categories
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

from typing import Any
import logging
import pandas as pd
from database import categories_db
from utils.helpers import clean_text,error_response,normalize_text,success_response
from utils.validation import validate_categorie

logger=logging.getLogger("utils")

# ============================================================
# 1. PREPARATION DES DONNEES
# ============================================================


def prepare_categorie_data(code_categorie:Any,nom_categorie:Any,description:Any=None)->dict[str,Any]:
    """Prepare les donnees d'une categorie avant enregistrement."""
    return {
        "code_categorie":clean_text(code_categorie).upper(),
        "nom_categorie":clean_text(nom_categorie),
        "description":clean_text(description) if description else None
    }

def validate_categorie_form(data:dict[str,Any])->dict[str,Any]:
    """Valide un formulaire categorie."""
    valid,errors=validate_categorie(data)
    if not valid:
        return error_response("Categorie invalide",errors)
    return success_response("Categorie valide",data)

# ============================================================
# 2. OPERATIONS CRUD
# ============================================================


def list_categories()->pd.DataFrame:
    """Retourne toutes les categories."""
    return categories_db.get_all_categories()

def list_categories_with_products()->pd.DataFrame:
    """Retourne les categories avec le nombre de produits."""
    return categories_db.get_categories_with_products()

def get_categorie(categorie_id:int)->dict[str,Any]|None:
    """Retourne une categorie par ID."""
    return categories_db.get_category_by_id(categorie_id)

def search_categories(keyword:Any)->pd.DataFrame:
    """Recherche une categorie."""
    keyword=clean_text(keyword)
    return categories_db.search_categories(keyword) if keyword else pd.DataFrame()

def suggest_code_categorie(nom_categorie:Any)->str:
    """Propose un code categorie depuis le nom saisi."""
    return categories_db.suggest_category_code(clean_text(nom_categorie))

def create_categorie(code_categorie:Any,nom_categorie:Any,description:Any=None)->dict[str,Any]:
    """Cree une categorie."""
    data=prepare_categorie_data(code_categorie,nom_categorie,description)
    check=validate_categorie_form(data)
    if not check["success"]:
        return check
    ok=categories_db.create_category(data["code_categorie"],data["nom_categorie"],data["description"])
    return success_response("Categorie creee",data) if ok else error_response("Creation de la categorie impossible")

def update_categorie(categorie_id:int,code_categorie:Any,nom_categorie:Any,description:Any=None)->dict[str,Any]:
    """Modifie une categorie."""
    data=prepare_categorie_data(code_categorie,nom_categorie,description)
    check=validate_categorie_form(data)
    if not check["success"]:
        return check
    ok=categories_db.update_category(categorie_id,data["code_categorie"],data["nom_categorie"],data["description"])
    return success_response("Categorie modifiee",data) if ok else error_response("Modification de la categorie impossible")

def delete_categorie(categorie_id:int)->dict[str,Any]:
    """Supprime une categorie si elle n'est pas utilisee."""
    valid,message=categories_db.can_delete_category(categorie_id)
    if not valid:
        return error_response(message)
    ok=categories_db.delete_category(categorie_id)
    return success_response("Categorie supprimee") if ok else error_response("Suppression de la categorie impossible")

# ============================================================
# 3. DONNEES POUR STREAMLIT
# ============================================================


def get_categories_options()->dict[str,int]:
    """Retourne les options selectbox {nom: id}."""
    df=list_categories()
    if df.empty:
        return {}
    return {f"{row['code_categorie']} - {row['nom_categorie']}":int(row["categorie_id"]) for _,row in df.iterrows()}

def get_categorie_name(categorie_id:int)->str:
    """Retourne le nom d'une categorie."""
    categorie=get_categorie(categorie_id)
    return str(categorie.get("nom_categorie","")) if categorie else ""

def filter_categories_dataframe(df:pd.DataFrame,keyword:Any="")->pd.DataFrame:
    """Filtre un DataFrame de categories cote interface."""
    keyword=normalize_text(keyword)
    if df.empty or not keyword:
        return df
    mask=df.apply(lambda row: keyword in normalize_text(" ".join(str(v) for v in row.values)),axis=1)
    return df[mask]

def get_categories_kpis()->dict[str,Any]:
    """Retourne les KPIs categories."""
    df=list_categories_with_products()
    if df.empty:
        return {"total_categories":0,"categories_utilisees":0,"categories_vides":0}
    product_col="total_produits" if "total_produits" in df.columns else None
    if not product_col:
        return {"total_categories":len(df),"categories_utilisees":0,"categories_vides":len(df)}
    used=int((df[product_col]>0).sum())
    return {"total_categories":len(df),"categories_utilisees":used,"categories_vides":len(df)-used}

def get_unused_categories()->pd.DataFrame:
    """Retourne les categories sans produit."""
    return categories_db.get_unused_categories()

__all__ = [
    "prepare_categorie_data",
    "validate_categorie_form",
    "list_categories",
    "list_categories_with_products",
    "get_categorie",
    "search_categories",
    "suggest_code_categorie",
    "create_categorie",
    "update_categorie",
    "delete_categorie",
    "get_categories_options",
    "get_categorie_name",
    "filter_categories_dataframe",
    "get_categories_kpis",
    "get_unused_categories",
]
