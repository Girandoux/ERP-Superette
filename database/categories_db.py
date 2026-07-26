# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : categories_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import re
import unicodedata
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists

# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("database")
TABLE_NAME = "dim_categories"
PRODUCT_TABLE = "dim_produits"
ID_COLUMN = "categorie_id"
CODE_COLUMN = "code_categorie"
NAME_COLUMN = "nom_categorie"

# ============================================================
# 2. VALIDATION
# ============================================================

def _normalize_text(value):
    """Nettoie un texte."""
    return " ".join(str(value).strip().split()) if value is not None else ""

def _normalize_code(code):
    """Nettoie le code categorie."""
    return _normalize_text(code).upper()


def _slug_words(value):
    """Transforme un libelle en mots ASCII majuscules."""
    text = unicodedata.normalize("NFKD", _normalize_text(value)).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"[A-Z0-9]+", text.upper())
    ignored = {"DE", "DES", "DU", "LA", "LE", "LES", "ET", "D", "L"}
    return [word for word in words if word not in ignored]

def suggest_category_code(nom_categorie):
    """Propose un code categorie a partir du nom et evite les doublons."""
    words = _slug_words(nom_categorie)
    if not words:
        base = "CAT"
    elif len(words) == 1:
        base = words[0][:3]
    elif len(words) == 2:
        base = (words[0][:2] + words[1][:1])[:3]
    else:
        base = "".join(word[:1] for word in words[:3])[:3]
    base = (base or "CAT").upper()
    code = base
    counter = 2
    while category_code_exists(code):
        suffix = str(counter)
        code = f"{base[:10-len(suffix)]}{suffix}"
        counter += 1
    return code
def validate_category_data(code_categorie, nom_categorie, description=None):
    """Valide les donnees d'une categorie."""
    code_categorie = _normalize_code(code_categorie)
    nom_categorie = _normalize_text(nom_categorie)
    description = _normalize_text(description) if description else None
    if not code_categorie:
        return False, "Le code categorie est obligatoire."
    if len(code_categorie) > 10:
        return False, "Le code categorie ne doit pas depasser 10 caracteres."
    if not nom_categorie:
        return False, "Le nom categorie est obligatoire."
    if len(nom_categorie) > 100:
        return False, "Le nom categorie ne doit pas depasser 100 caracteres."
    if description and len(description) > 255:
        return False, "La description ne doit pas depasser 255 caracteres."
    return True, "OK"

def category_code_exists(code_categorie, exclude_id=None):
    """Verifie si un code categorie existe deja."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER({CODE_COLUMN}) = LOWER(:code)"
    params = {"code": _normalize_code(code_categorie)}
    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id
    return record_exists(query, params)

def category_name_exists(nom_categorie, exclude_id=None):
    """Verifie si un nom categorie existe deja."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER({NAME_COLUMN}) = LOWER(:name)"
    params = {"name": _normalize_text(nom_categorie)}
    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id
    return record_exists(query, params)

def can_save_category(code_categorie, nom_categorie, description=None, exclude_id=None):
    """Verifie si une categorie peut etre inseree ou modifiee."""
    valid, message = validate_category_data(code_categorie, nom_categorie, description)
    if not valid:
        return False, message
    if category_code_exists(code_categorie, exclude_id):
        return False, "Ce code categorie existe deja."
    if category_name_exists(nom_categorie, exclude_id):
        return False, "Ce nom categorie existe deja."
    return True, "OK"

# ============================================================
# 3. LECTURE
# ============================================================

def get_all_categories():
    """Retourne toutes les categories."""
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY {NAME_COLUMN}"
    return read_sql_dataframe(query)

def get_category_by_id(categorie_id):
    """Retourne une categorie par ID."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return fetch_one(query, {"id": categorie_id})

def get_category_by_code(code_categorie):
    """Retourne une categorie par code."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE LOWER({CODE_COLUMN}) = LOWER(:code)"
    return fetch_one(query, {"code": _normalize_code(code_categorie)})

def get_category_by_name(nom_categorie):
    """Retourne une categorie par nom."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE LOWER({NAME_COLUMN}) = LOWER(:name)"
    return fetch_one(query, {"name": _normalize_text(nom_categorie)})

def search_categories(keyword):
    """Recherche une categorie par code, nom ou description."""
    keyword = _normalize_text(keyword)
    if not keyword:
        return pd.DataFrame()
    query = f"""
    SELECT * FROM {TABLE_NAME}
    WHERE {CODE_COLUMN} ILIKE :keyword OR {NAME_COLUMN} ILIKE :keyword OR description ILIKE :keyword
    ORDER BY {NAME_COLUMN}
    """
    return read_sql_dataframe(query, {"keyword": f"%{keyword}%"})

def count_categories():
    """Compte le nombre total de categories."""
    result = fetch_one(f"SELECT COUNT(*) AS total FROM {TABLE_NAME}")
    return int(result["total"]) if result else 0

# ============================================================
# 4. INSERTION ET MODIFICATION
# ============================================================

def insert_category(code_categorie, nom_categorie, description=None):
    """Insere une nouvelle categorie."""
    code_categorie = _normalize_code(code_categorie)
    nom_categorie = _normalize_text(nom_categorie)
    description = _normalize_text(description) if description else None
    valid, message = can_save_category(code_categorie, nom_categorie, description)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    INSERT INTO {TABLE_NAME} ({CODE_COLUMN},{NAME_COLUMN},description)
    VALUES (:code,:name,:description)
    """
    return execute_query(query, {"code": code_categorie, "name": nom_categorie, "description": description})

def create_category(code_categorie, nom_categorie, description=None):
    """Wrapper utilise par Streamlit."""
    return insert_category(code_categorie, nom_categorie, description)

def update_category(categorie_id, code_categorie, nom_categorie, description=None):
    """Modifie une categorie."""
    if not get_category_by_id(categorie_id):
        logger.warning("Categorie inexistante.")
        return False
    code_categorie = _normalize_code(code_categorie)
    nom_categorie = _normalize_text(nom_categorie)
    description = _normalize_text(description) if description else None
    valid, message = can_save_category(code_categorie, nom_categorie, description, exclude_id=categorie_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    UPDATE {TABLE_NAME}
    SET {CODE_COLUMN} = :code,{NAME_COLUMN} = :name,description = :description
    WHERE {ID_COLUMN} = :id
    """
    return execute_query(query, {"id": categorie_id, "code": code_categorie, "name": nom_categorie, "description": description})

# ============================================================
# 5. SUPPRESSION
# ============================================================

def count_products_by_category(categorie_id):
    """Compte les produits utilisant une categorie."""
    query = f"SELECT COUNT(*) AS total FROM {PRODUCT_TABLE} WHERE {ID_COLUMN} = :id"
    result = fetch_one(query, {"id": categorie_id})
    return int(result["total"]) if result else 0

def can_delete_category(categorie_id):
    """Verifie si une categorie peut etre supprimee."""
    if not get_category_by_id(categorie_id):
        return False, "Categorie inexistante."
    total_products = count_products_by_category(categorie_id)
    if total_products > 0:
        return False, f"Suppression impossible : {total_products} produit(s) utilisent cette categorie."
    return True, "OK"

def delete_category(categorie_id):
    """Supprime une categorie si aucun produit ne l'utilise."""
    valid, message = can_delete_category(categorie_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": categorie_id})

# ============================================================
# 6. STATISTIQUES ET KPI
# ============================================================

def get_categories_with_products():
    """Retourne les categories avec le nombre de produits."""
    query = f"""
    SELECT c.{ID_COLUMN},c.{CODE_COLUMN},c.{NAME_COLUMN},c.description,c.date_creation,COUNT(p.produit_id) AS total_produits
    FROM {TABLE_NAME} c
    LEFT JOIN {PRODUCT_TABLE} p ON p.{ID_COLUMN} = c.{ID_COLUMN}
    GROUP BY c.{ID_COLUMN},c.{CODE_COLUMN},c.{NAME_COLUMN},c.description,c.date_creation
    ORDER BY c.{NAME_COLUMN}
    """
    return read_sql_dataframe(query)

def get_unused_categories():
    """Retourne les categories sans produit."""
    query = f"""
    SELECT c.*
    FROM {TABLE_NAME} c
    LEFT JOIN {PRODUCT_TABLE} p ON p.{ID_COLUMN} = c.{ID_COLUMN}
    WHERE p.produit_id IS NULL
    ORDER BY c.{NAME_COLUMN}
    """
    return read_sql_dataframe(query)

def get_category_statistics():
    """Retourne les statistiques des categories."""
    df = get_categories_with_products()
    if df.empty:
        return {"total_categories": 0, "used_categories": 0, "unused_categories": 0}
    total = len(df)
    used = int((df["total_produits"] > 0).sum())
    unused = total - used
    return {"total_categories": total, "used_categories": used, "unused_categories": unused}

def get_category_kpis():
    """Retourne les KPIs categories."""
    stats = get_category_statistics()
    total = stats["total_categories"]
    used = stats["used_categories"]
    usage_rate = round((used / total * 100), 2) if total else 0
    return {
        "total_categories": total,
        "used_categories": used,
        "unused_categories": stats["unused_categories"],
        "usage_rate": usage_rate
    }

# ============================================================
# 7. EXPORT PUBLIC
# ============================================================

__all__ = [
    "get_all_categories",
    "get_category_by_id",
    "get_category_by_code",
    "get_category_by_name",
    "suggest_category_code",
    "search_categories",
    "count_categories",
    "insert_category",
    "create_category",
    "update_category",
    "delete_category",
    "can_delete_category",
    "count_products_by_category",
    "get_categories_with_products",
    "get_unused_categories",
    "get_category_statistics",
    "get_category_kpis"
]

