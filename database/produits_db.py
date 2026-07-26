# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : produits_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import re
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar

# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("database")
TABLE_NAME = "dim_produits"
CATEGORY_TABLE = "dim_categories"
LIGNES_ACHAT_TABLE = "dim_lignes_achat"
LIGNES_VENTE_TABLE = "dim_lignes_vente"
PERTES_TABLE = "dim_pertes"
INVENTAIRE_TABLE = "fact_inventaire"
ID_COLUMN = "produit_id"
CODE_COLUMN = "code_produit"
NAME_COLUMN = "nom_produit"

# ============================================================
# 2. VALIDATION
# ============================================================

def _normalize_text(value):
    """Nettoie un texte."""
    return " ".join(str(value).strip().split()) if value is not None else ""

def _normalize_code(code):
    """Nettoie le code produit."""
    return _normalize_text(code).upper()

def _to_int(value, default=0):
    """Convertit une valeur en entier."""
    try:
        return int(value)
    except Exception:
        return default

def validate_product_data(code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min, actif=True):
    """Valide les donnees d'un produit."""
    code_produit = _normalize_code(code_produit)
    nom_produit = _normalize_text(nom_produit)
    unite = _normalize_text(unite)
    qte_par_carton = _to_int(qte_par_carton)
    stock_min = _to_int(stock_min)
    if not code_produit:
        return False, "Le code produit est obligatoire."
    if len(code_produit) > 20:
        return False, "Le code produit ne doit pas depasser 20 caracteres."
    if not nom_produit:
        return False, "Le nom produit est obligatoire."
    if len(nom_produit) > 150:
        return False, "Le nom produit ne doit pas depasser 150 caracteres."
    if not categorie_id:
        return False, "La categorie est obligatoire."
    if not unite:
        return False, "L'unite est obligatoire."
    if len(unite) > 20:
        return False, "L'unite ne doit pas depasser 20 caracteres."
    if qte_par_carton <= 0:
        return False, "La quantite par carton doit etre superieure a 0."
    if stock_min < 0:
        return False, "Le stock minimum ne peut pas etre negatif."
    if not isinstance(actif, bool):
        return False, "Le champ actif doit etre True ou False."
    return True, "OK"

def category_exists(categorie_id):
    """Verifie si une categorie existe."""
    query = f"SELECT 1 FROM {CATEGORY_TABLE} WHERE categorie_id = :id"
    return record_exists(query, {"id": categorie_id})

def product_code_exists(code_produit, exclude_id=None):
    """Verifie si un code produit existe deja."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER({CODE_COLUMN}) = LOWER(:code)"
    params = {"code": _normalize_code(code_produit)}
    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id
    return record_exists(query, params)

def product_name_exists(nom_produit, exclude_id=None):
    """Verifie si un nom produit existe deja."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER({NAME_COLUMN}) = LOWER(:name)"
    params = {"name": _normalize_text(nom_produit)}
    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id
    return record_exists(query, params)

def can_save_product(code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min, actif=True, exclude_id=None):
    """Verifie si un produit peut etre insere ou modifie."""
    valid, message = validate_product_data(code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min, actif)
    if not valid:
        return False, message
    if not category_exists(categorie_id):
        return False, "La categorie selectionnee n'existe pas."
    if product_code_exists(code_produit, exclude_id):
        return False, "Ce code produit existe deja."
    if product_name_exists(nom_produit, exclude_id):
        return False, "Ce nom produit existe deja."
    return True, "OK"

# ============================================================
# 3. LECTURE
# ============================================================

def get_all_products(active_only=False):
    """Retourne tous les produits avec leur categorie."""
    where = "WHERE p.actif = TRUE" if active_only else ""
    query = f"""
    SELECT p.produit_id,p.code_produit,p.nom_produit,p.categorie_id,c.code_categorie,c.nom_categorie,p.unite,p.qte_par_carton,p.stock_min,
    COALESCE(p.stock_actuel,0) AS stock_actuel,p.actif,p.date_creation
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    {where}
    ORDER BY p.nom_produit
    """
    return read_sql_dataframe(query)

def get_products_dataframe(active_only=False):
    """Retourne les produits dans un DataFrame."""
    return get_all_products(active_only=active_only)

def get_product_by_id(produit_id):
    """Retourne un produit par ID."""
    query = f"""
    SELECT p.*,c.code_categorie,c.nom_categorie
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    WHERE p.{ID_COLUMN} = :id
    """
    return fetch_one(query, {"id": produit_id})

def get_product_by_code(code_produit):
    """Retourne un produit par code."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE LOWER({CODE_COLUMN}) = LOWER(:code)"
    return fetch_one(query, {"code": _normalize_code(code_produit)})

def get_product_by_name(nom_produit):
    """Retourne un produit par nom."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE LOWER({NAME_COLUMN}) = LOWER(:name)"
    return fetch_one(query, {"name": _normalize_text(nom_produit)})

def product_exists(produit_id):
    """Verifie si un produit existe."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return record_exists(query, {"id": produit_id})

def search_products(keyword, active_only=False):
    """Recherche un produit par code, nom, unite ou categorie."""
    keyword = _normalize_text(keyword)
    if not keyword:
        return pd.DataFrame()
    active_filter = "AND p.actif = TRUE" if active_only else ""
    query = f"""
    SELECT p.produit_id,p.code_produit,p.nom_produit,p.categorie_id,c.nom_categorie,p.unite,p.qte_par_carton,p.stock_min,
    COALESCE(p.stock_actuel,0) AS stock_actuel,p.actif,p.date_creation
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    WHERE (p.code_produit ILIKE :keyword OR p.nom_produit ILIKE :keyword OR p.unite ILIKE :keyword OR c.nom_categorie ILIKE :keyword) {active_filter}
    ORDER BY p.nom_produit
    """
    return read_sql_dataframe(query, {"keyword": f"%{keyword}%"})


def get_next_product_code(categorie_id=None, width=3):
    """Genere le premier code produit libre selon le code de categorie."""
    prefix = "PRD"
    if categorie_id:
        category = fetch_one(f"SELECT code_categorie FROM {CATEGORY_TABLE} WHERE categorie_id = :id", {"id": categorie_id})
        if category and category.get("code_categorie"):
            prefix = _normalize_code(category["code_categorie"])
    rows = read_sql_dataframe(f"SELECT {CODE_COLUMN} FROM {TABLE_NAME} WHERE {CODE_COLUMN} ILIKE :prefix", {"prefix": f"{prefix}%"})
    used_numbers = set()
    selected_width = width
    if not rows.empty:
        for value in rows[CODE_COLUMN].dropna().astype(str):
            match = re.search(rf"^{re.escape(prefix)}(\d+)$", value.strip().upper())
            if not match:
                continue
            number_text = match.group(1)
            used_numbers.add(int(number_text))
            selected_width = max(selected_width, len(number_text))
    next_number = 1
    while next_number in used_numbers:
        next_number += 1
    return f"{prefix}{next_number:0{selected_width}d}"

def get_products_by_category(categorie_id, active_only=False):
    """Retourne les produits d'une categorie."""
    active_filter = "AND actif = TRUE" if active_only else ""
    query = f"SELECT * FROM {TABLE_NAME} WHERE categorie_id = :id {active_filter} ORDER BY {NAME_COLUMN}"
    return read_sql_dataframe(query, {"id": categorie_id})

# ============================================================
# 4. INSERTION ET MODIFICATION
# ============================================================

def insert_product(code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min=0, actif=True):
    """Insere un nouveau produit."""
    code_produit = _normalize_code(code_produit)
    nom_produit = _normalize_text(nom_produit)
    unite = _normalize_text(unite)
    qte_par_carton = _to_int(qte_par_carton)
    stock_min = _to_int(stock_min)
    valid, message = can_save_product(code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min, actif)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    INSERT INTO {TABLE_NAME} ({CODE_COLUMN},{NAME_COLUMN},categorie_id,unite,qte_par_carton,stock_min,actif)
    VALUES (:code,:name,:categorie_id,:unite,:qte_par_carton,:stock_min,:actif)
    """
    params = {"code": code_produit, "name": nom_produit, "categorie_id": categorie_id, "unite": unite, "qte_par_carton": qte_par_carton, "stock_min": stock_min, "actif": actif}
    return execute_query(query, params)

def create_product(code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min=0, actif=True):
    """Wrapper utilise par Streamlit."""
    return insert_product(code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min, actif)

def update_product(produit_id, code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min=0, actif=True):
    """Modifie un produit."""
    if not product_exists(produit_id):
        logger.warning("Produit inexistant.")
        return False
    code_produit = _normalize_code(code_produit)
    nom_produit = _normalize_text(nom_produit)
    unite = _normalize_text(unite)
    qte_par_carton = _to_int(qte_par_carton)
    stock_min = _to_int(stock_min)
    valid, message = can_save_product(code_produit, nom_produit, categorie_id, unite, qte_par_carton, stock_min, actif, exclude_id=produit_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    UPDATE {TABLE_NAME}
    SET {CODE_COLUMN} = :code,{NAME_COLUMN} = :name,categorie_id = :categorie_id,unite = :unite,qte_par_carton = :qte_par_carton,stock_min = :stock_min,actif = :actif
    WHERE {ID_COLUMN} = :id
    """
    params = {"id": produit_id, "code": code_produit, "name": nom_produit, "categorie_id": categorie_id, "unite": unite, "qte_par_carton": qte_par_carton, "stock_min": stock_min, "actif": actif}
    return execute_query(query, params)

# ============================================================
# 5. STOCK ET ACTIVATION
# ============================================================

def update_stock(produit_id, nouveau_stock):
    """Met a jour le stock actuel manuellement."""
    nouveau_stock = _to_int(nouveau_stock)
    if nouveau_stock < 0:
        logger.warning("Le stock ne peut pas etre negatif.")
        return False
    if not product_exists(produit_id):
        logger.warning("Produit inexistant.")
        return False
    query = f"UPDATE {TABLE_NAME} SET stock_actuel = :stock WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": produit_id, "stock": nouveau_stock})

def update_stock_min(produit_id, stock_min):
    """Modifie uniquement le stock minimum."""
    stock_min = _to_int(stock_min)
    if stock_min < 0:
        return False
    query = f"UPDATE {TABLE_NAME} SET stock_min = :stock_min WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": produit_id, "stock_min": stock_min})

def deactivate_product(produit_id):
    """Desactive un produit."""
    query = f"UPDATE {TABLE_NAME} SET actif = FALSE WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": produit_id})

def activate_product(produit_id):
    """Reactive un produit."""
    query = f"UPDATE {TABLE_NAME} SET actif = TRUE WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": produit_id})

# ============================================================
# 6. SUPPRESSION
# ============================================================

def count_product_movements(produit_id):
    """Compte les utilisations liees a un produit."""
    query = f"""
    SELECT
    (SELECT COUNT(*) FROM {LIGNES_ACHAT_TABLE} WHERE produit_id = :id) AS achats,
    (SELECT COUNT(*) FROM {LIGNES_VENTE_TABLE} WHERE produit_id = :id) AS ventes,
    (SELECT COUNT(*) FROM {PERTES_TABLE} WHERE produit_id = :id) AS pertes,
    (SELECT COUNT(*) FROM {INVENTAIRE_TABLE} WHERE produit_id = :id) AS inventaires,
    (SELECT COALESCE(stock_actuel,0) FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id) AS stock_actuel
    """
    result = fetch_one(query, {"id": produit_id})
    return result or {"achats": 0, "ventes": 0, "pertes": 0, "inventaires": 0, "stock_actuel": 0}

def can_delete_product(produit_id):
    """Verifie si un produit peut etre supprime physiquement."""
    if not product_exists(produit_id):
        return False, "Produit inexistant."
    movements = count_product_movements(produit_id)
    reasons = []
    if int(movements.get("achats") or 0) > 0:
        reasons.append(f"{int(movements.get('achats') or 0)} ligne(s) d'achat")
    if int(movements.get("ventes") or 0) > 0:
        reasons.append(f"{int(movements.get('ventes') or 0)} ligne(s) de vente")
    if int(movements.get("pertes") or 0) > 0:
        reasons.append(f"{int(movements.get('pertes') or 0)} perte(s)")
    if int(movements.get("inventaires") or 0) > 0:
        reasons.append(f"{int(movements.get('inventaires') or 0)} inventaire(s)")
    if int(float(movements.get("stock_actuel") or 0)) != 0:
        reasons.append(f"stock actuel {int(float(movements.get('stock_actuel') or 0))}")
    if reasons:
        return False, "Suppression impossible : produit utilise dans " + ", ".join(reasons) + ". Desactive le produit a la place."
    return True, "OK"

def delete_product(produit_id):
    """Supprime un produit si aucun module ne l'utilise."""
    valid, message = can_delete_product(produit_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": produit_id})

# ============================================================
# 7. KPI ET STATISTIQUES
# ============================================================

def count_products(active_only=False):
    """Compte les produits."""
    where = "WHERE actif = TRUE" if active_only else ""
    value = get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME} {where}")
    return int(value or 0)

def get_low_stock_products():
    """Produits dont le stock est sous ou egal au minimum."""
    query = f"""
    SELECT p.*,c.nom_categorie
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    WHERE COALESCE(p.stock_actuel,0) <= p.stock_min AND p.actif = TRUE
    ORDER BY COALESCE(p.stock_actuel,0),p.nom_produit
    """
    return read_sql_dataframe(query)

def get_out_of_stock_products():
    """Produits en rupture."""
    query = f"""
    SELECT p.*,c.nom_categorie
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    WHERE COALESCE(p.stock_actuel,0) <= 0 AND p.actif = TRUE
    ORDER BY p.nom_produit
    """
    return read_sql_dataframe(query)

def get_stock_value():
    """Valeur du stock selon le dernier prix d'achat piece."""
    query = f"""
    SELECT COALESCE(SUM(COALESCE(p.stock_actuel,0) * COALESCE(cout.pu_achat_piece,0)),0) AS valeur_stock
    FROM {TABLE_NAME} p
    LEFT JOIN (
        SELECT DISTINCT ON (produit_id) produit_id,pu_achat_piece
        FROM {LIGNES_ACHAT_TABLE}
        ORDER BY produit_id,ligne_achat_id DESC
    ) cout ON cout.produit_id = p.produit_id
    """
    result = fetch_one(query)
    return float(result["valeur_stock"]) if result else 0.0

def get_top_stock_value_products(limit=10):
    """Top produits par valeur de stock."""
    query = f"""
    SELECT p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie,COALESCE(p.stock_actuel,0) AS stock_actuel,
    COALESCE(cout.pu_achat_piece,0) AS dernier_cout,COALESCE(p.stock_actuel,0) * COALESCE(cout.pu_achat_piece,0) AS valeur_stock
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    LEFT JOIN (
        SELECT DISTINCT ON (produit_id) produit_id,pu_achat_piece
        FROM {LIGNES_ACHAT_TABLE}
        ORDER BY produit_id,ligne_achat_id DESC
    ) cout ON cout.produit_id = p.produit_id
    ORDER BY valeur_stock DESC
    LIMIT :limit
    """
    return read_sql_dataframe(query, {"limit": int(limit)})

def count_products_by_category(categorie_id):
    """Compte les produits d'une categorie."""
    value = get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE categorie_id = :id", {"id": categorie_id})
    return int(value or 0)

def get_products_statistics():
    """Retourne les statistiques generales produits."""
    query = f"""
    SELECT COUNT(*) AS total_products,
    COUNT(*) FILTER (WHERE actif = TRUE) AS active_products,
    COUNT(*) FILTER (WHERE actif = FALSE) AS inactive_products,
    COUNT(*) FILTER (WHERE COALESCE(stock_actuel,0) <= stock_min AND actif = TRUE) AS low_stock_products,
    COUNT(*) FILTER (WHERE COALESCE(stock_actuel,0) <= 0 AND actif = TRUE) AS out_of_stock_products,
    COALESCE(SUM(stock_actuel),0) AS total_stock
    FROM {TABLE_NAME}
    """
    return fetch_one(query) or {}

def get_products_kpis():
    """Retourne les KPIs produits."""
    stats = get_products_statistics()
    return {
        "total_products": int(stats.get("total_products", 0)),
        "active_products": int(stats.get("active_products", 0)),
        "inactive_products": int(stats.get("inactive_products", 0)),
        "low_stock_products": int(stats.get("low_stock_products", 0)),
        "out_of_stock_products": int(stats.get("out_of_stock_products", 0)),
        "total_stock": int(stats.get("total_stock", 0)),
        "stock_value": get_stock_value()
    }

# ============================================================
# 8. EXPORT PUBLIC
# ============================================================

__all__ = [
    "get_all_products",
    "get_products_dataframe",
    "get_product_by_id",
    "get_product_by_code",
    "get_product_by_name",
    "product_exists",
    "search_products",
    "get_next_product_code",
    "get_products_by_category",
    "insert_product",
    "create_product",
    "update_product",
    "update_stock",
    "update_stock_min",
    "deactivate_product",
    "activate_product",
    "delete_product",
    "can_delete_product",
    "count_product_movements",
    "count_products",
    "get_low_stock_products",
    "get_out_of_stock_products",
    "get_stock_value",
    "get_top_stock_value_products",
    "count_products_by_category",
    "get_products_statistics",
    "get_products_kpis"
]

