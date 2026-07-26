# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : lignes_achat_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
from datetime import date
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar
from database.achats_db import achat_exists, recalculate_achat_total
from database.produits_db import product_exists

# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("database")
TABLE_NAME = "dim_lignes_achat"
ACHATS_TABLE = "fact_achats"
PRODUITS_TABLE = "dim_produits"
ID_COLUMN = "ligne_achat_id"

# ============================================================
# 2. VALIDATION
# ============================================================

def _to_int(value, default=0):
    """Convertit une valeur en entier."""
    try:
        return int(value)
    except Exception:
        return default

def _to_float(value, default=0):
    """Convertit une valeur en nombre."""
    try:
        return float(value)
    except Exception:
        return default

def validate_ligne_achat_data(achat_id, produit_id, qte_cartons, qte_par_carton, pu_achat_carton, date_fabrication=None, date_peremption=None):
    """Valide une ligne d'achat."""
    qte_cartons = _to_float(qte_cartons)
    qte_par_carton = _to_int(qte_par_carton)
    pu_achat_carton = _to_float(pu_achat_carton)
    if not achat_id or not achat_exists(achat_id):
        return False, "L'achat selectionne n'existe pas."
    if not produit_id or not product_exists(produit_id):
        return False, "Le produit selectionne n'existe pas."
    if qte_cartons <= 0:
        return False, "La quantite de cartons doit etre superieure a 0."
    if qte_par_carton <= 0:
        return False, "La quantite par carton doit etre superieure a 0."
    if pu_achat_carton < 0:
        return False, "Le prix d'achat carton ne peut pas etre negatif."
    if date_fabrication and date_peremption and date_peremption < date_fabrication:
        return False, "La date de peremption doit etre superieure ou egale a la date de fabrication."
    return True, "OK"

def ligne_achat_exists(ligne_achat_id):
    """Verifie si une ligne d'achat existe."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return record_exists(query, {"id": ligne_achat_id})

def product_already_in_achat(achat_id, produit_id, exclude_id=None):
    """Verifie si un produit est deja present dans un achat."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE achat_id = :achat_id AND produit_id = :produit_id"
    params = {"achat_id": achat_id, "produit_id": produit_id}
    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id
    return record_exists(query, params)

# ============================================================
# 3. LECTURE
# ============================================================

def get_all_lignes_achat():
    """Retourne toutes les lignes d'achat avec produit et achat."""
    query = f"""
    SELECT la.*,p.code_produit,p.nom_produit,a.date_achat,a.numero_facture
    FROM {TABLE_NAME} la
    LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = la.produit_id
    LEFT JOIN {ACHATS_TABLE} a ON a.achat_id = la.achat_id
    ORDER BY la.achat_id DESC,la.ligne_achat_id
    """
    return read_sql_dataframe(query)

def get_ligne_achat_by_id(ligne_achat_id):
    """Retourne une ligne d'achat par ID."""
    query = f"""
    SELECT la.*,p.code_produit,p.nom_produit,a.date_achat,a.numero_facture
    FROM {TABLE_NAME} la
    LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = la.produit_id
    LEFT JOIN {ACHATS_TABLE} a ON a.achat_id = la.achat_id
    WHERE la.{ID_COLUMN} = :id
    """
    return fetch_one(query, {"id": ligne_achat_id})

def get_lignes_by_achat(achat_id):
    """Retourne les lignes d'un achat."""
    query = f"""
    SELECT la.*,p.code_produit,p.nom_produit
    FROM {TABLE_NAME} la
    LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = la.produit_id
    WHERE la.achat_id = :id
    ORDER BY la.ligne_achat_id
    """
    return read_sql_dataframe(query, {"id": achat_id})


def get_lignes_achat_incoherentes():
    """Retourne les lignes dont les valeurs calculees ne respectent pas les formules metier."""
    query = f"""
    SELECT la.ligne_achat_id,la.achat_id,p.code_produit,p.nom_produit,la.qte_cartons,la.qte_par_carton,
    la.pu_achat_carton,la.pu_achat_piece,ROUND(CASE WHEN COALESCE(la.qte_par_carton,0)>0 THEN la.pu_achat_carton/la.qte_par_carton ELSE 0 END,2) AS pu_achat_piece_calcule,
    la.total_achat,ROUND(la.qte_cartons*la.pu_achat_carton,2) AS total_achat_calcule
    FROM {TABLE_NAME} la
    JOIN {PRODUITS_TABLE} p ON p.produit_id = la.produit_id
    WHERE ABS(COALESCE(la.pu_achat_piece,0)-ROUND(CASE WHEN COALESCE(la.qte_par_carton,0)>0 THEN la.pu_achat_carton/la.qte_par_carton ELSE 0 END,2))>0.01
    OR ABS(COALESCE(la.total_achat,0)-ROUND(COALESCE(la.qte_cartons,0)*COALESCE(la.pu_achat_carton,0),2))>0.01
    ORDER BY la.ligne_achat_id
    """
    return read_sql_dataframe(query)
def get_lignes_by_product(produit_id):
    """Retourne les lignes d'achat d'un produit."""
    query = f"""
    SELECT la.*,a.date_achat,a.numero_facture
    FROM {TABLE_NAME} la
    LEFT JOIN {ACHATS_TABLE} a ON a.achat_id = la.achat_id
    WHERE la.produit_id = :id
    ORDER BY a.date_achat DESC,la.ligne_achat_id DESC
    """
    return read_sql_dataframe(query, {"id": produit_id})

def search_lignes_achat(achat_id=None, produit_id=None, keyword=None, start_date=None, end_date=None):
    """Recherche avancee des lignes d'achat."""
    query = f"""
    SELECT la.*,p.code_produit,p.nom_produit,a.date_achat,a.numero_facture
    FROM {TABLE_NAME} la
    LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = la.produit_id
    LEFT JOIN {ACHATS_TABLE} a ON a.achat_id = la.achat_id
    WHERE 1=1
    """
    params = {}
    if achat_id is not None:
        query += " AND la.achat_id = :achat_id"
        params["achat_id"] = achat_id
    if produit_id is not None:
        query += " AND la.produit_id = :produit_id"
        params["produit_id"] = produit_id
    if keyword:
        query += " AND (p.code_produit ILIKE :keyword OR p.nom_produit ILIKE :keyword OR a.numero_facture ILIKE :keyword)"
        params["keyword"] = f"%{keyword}%"
    if start_date is not None:
        query += " AND a.date_achat >= :start_date"
        params["start_date"] = start_date
    if end_date is not None:
        query += " AND a.date_achat <= :end_date"
        params["end_date"] = end_date
    query += " ORDER BY la.achat_id DESC,la.ligne_achat_id"
    return read_sql_dataframe(query, params)

# ============================================================
# 4. INSERTION ET MODIFICATION
# ============================================================

def insert_ligne_achat(achat_id, produit_id, qte_cartons, qte_par_carton, pu_achat_carton, date_fabrication=None, date_peremption=None):
    """Insere une ligne d'achat. Les triggers calculent quantites, prix piece, total et stock."""
    qte_cartons = _to_float(qte_cartons)
    qte_par_carton = _to_int(qte_par_carton)
    pu_achat_carton = _to_float(pu_achat_carton)
    valid, message = validate_ligne_achat_data(achat_id, produit_id, qte_cartons, qte_par_carton, pu_achat_carton, date_fabrication, date_peremption)
    if not valid:
        logger.warning(message)
        return False
    if product_already_in_achat(achat_id, produit_id):
        logger.warning("Ce produit existe deja dans cet achat.")
        return False
    quantite_achat = calculate_quantite_achat(qte_cartons, qte_par_carton)
    pu_achat_piece = calculate_pu_achat_piece(pu_achat_carton, qte_par_carton)
    total_achat = calculate_ligne_achat_total(qte_cartons, pu_achat_carton)
    query = f"""
    INSERT INTO {TABLE_NAME} (achat_id,produit_id,qte_cartons,qte_par_carton,quantite_achat,pu_achat_carton,pu_achat_piece,total_achat,date_fabrication,date_peremption)
    VALUES (:achat_id,:produit_id,:qte_cartons,:qte_par_carton,:quantite_achat,:pu_achat_carton,:pu_achat_piece,:total_achat,:date_fabrication,:date_peremption)
    """
    params = {"achat_id": achat_id, "produit_id": produit_id, "qte_cartons": qte_cartons, "qte_par_carton": qte_par_carton, "quantite_achat": quantite_achat, "pu_achat_carton": pu_achat_carton, "pu_achat_piece": pu_achat_piece, "total_achat": total_achat, "date_fabrication": date_fabrication, "date_peremption": date_peremption}
    return execute_query(query, params)

def create_ligne_achat(achat_id, produit_id, qte_cartons, qte_par_carton, pu_achat_carton, date_fabrication=None, date_peremption=None):
    """Wrapper utilise par Streamlit."""
    return insert_ligne_achat(achat_id, produit_id, qte_cartons, qte_par_carton, pu_achat_carton, date_fabrication, date_peremption)

def update_ligne_achat(ligne_achat_id, achat_id, produit_id, qte_cartons, qte_par_carton, pu_achat_carton, date_fabrication=None, date_peremption=None):
    """Modifie une ligne d'achat. Les triggers ajustent stock et total."""
    if not ligne_achat_exists(ligne_achat_id):
        logger.warning("Ligne d'achat inexistante.")
        return False
    qte_cartons = _to_float(qte_cartons)
    qte_par_carton = _to_int(qte_par_carton)
    pu_achat_carton = _to_float(pu_achat_carton)
    valid, message = validate_ligne_achat_data(achat_id, produit_id, qte_cartons, qte_par_carton, pu_achat_carton, date_fabrication, date_peremption)
    if not valid:
        logger.warning(message)
        return False
    if product_already_in_achat(achat_id, produit_id, exclude_id=ligne_achat_id):
        logger.warning("Ce produit existe deja dans cet achat.")
        return False
    quantite_achat = calculate_quantite_achat(qte_cartons, qte_par_carton)
    pu_achat_piece = calculate_pu_achat_piece(pu_achat_carton, qte_par_carton)
    total_achat = calculate_ligne_achat_total(qte_cartons, pu_achat_carton)
    query = f"""
    UPDATE {TABLE_NAME}
    SET achat_id = :achat_id,produit_id = :produit_id,qte_cartons = :qte_cartons,qte_par_carton = :qte_par_carton,quantite_achat = :quantite_achat,
    pu_achat_carton = :pu_achat_carton,pu_achat_piece = :pu_achat_piece,total_achat = :total_achat,date_fabrication = :date_fabrication,date_peremption = :date_peremption
    WHERE {ID_COLUMN} = :id
    """
    params = {"id": ligne_achat_id, "achat_id": achat_id, "produit_id": produit_id, "qte_cartons": qte_cartons, "qte_par_carton": qte_par_carton, "quantite_achat": quantite_achat, "pu_achat_carton": pu_achat_carton, "pu_achat_piece": pu_achat_piece, "total_achat": total_achat, "date_fabrication": date_fabrication, "date_peremption": date_peremption}
    return execute_query(query, params)

# ============================================================
# 5. SUPPRESSION ET CALCULS
# ============================================================

def delete_ligne_achat(ligne_achat_id):
    """Supprime une ligne d'achat. Les triggers ajustent stock et total."""
    if not ligne_achat_exists(ligne_achat_id):
        logger.warning("Ligne d'achat inexistante.")
        return False
    query = f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": ligne_achat_id})

def calculate_ligne_achat_total(qte_cartons, pu_achat_carton):
    """Calcule le total d'une ligne d'achat."""
    return round(max(_to_float(qte_cartons), 0) * max(_to_float(pu_achat_carton), 0), 2)

def calculate_quantite_achat(qte_cartons, qte_par_carton):
    """Calcule la quantite totale achetee."""
    return round(max(_to_float(qte_cartons), 0) * max(_to_int(qte_par_carton), 0))

def calculate_pu_achat_piece(pu_achat_carton, qte_par_carton):
    """Calcule le prix unitaire piece."""
    qte_par_carton = _to_int(qte_par_carton)
    if qte_par_carton <= 0:
        return 0
    return round(_to_float(pu_achat_carton) / qte_par_carton, 2)

def calculate_achat_total(achat_id):
    """Calcule le total des lignes d'un achat."""
    value = get_scalar(f"SELECT COALESCE(SUM(total_achat),0) FROM {TABLE_NAME} WHERE achat_id = :id", {"id": achat_id})
    return float(value or 0)

def calculate_achat_quantity(achat_id):
    """Calcule la quantite totale des lignes d'un achat."""
    value = get_scalar(f"SELECT COALESCE(SUM(quantite_achat),0) FROM {TABLE_NAME} WHERE achat_id = :id", {"id": achat_id})
    return int(value or 0)

# ============================================================
# 6. STATISTIQUES ET KPI
# ============================================================

def count_lignes_achat():
    """Compte les lignes d'achat."""
    value = get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    return int(value or 0)

def get_lignes_achat_statistics():
    """Retourne les statistiques des lignes d'achat."""
    query = f"""
    SELECT COUNT(*) AS total_lignes,COALESCE(SUM(qte_cartons),0) AS total_cartons,COALESCE(SUM(quantite_achat),0) AS total_quantite,
    COALESCE(SUM(total_achat),0) AS montant_total,COALESCE(AVG(pu_achat_piece),0) AS cout_moyen_piece
    FROM {TABLE_NAME}
    """
    return fetch_one(query) or {}

def get_product_achat_statistics(produit_id):
    """Retourne les statistiques d'achat d'un produit."""
    query = f"""
    SELECT produit_id,COUNT(*) AS total_achats,COALESCE(SUM(quantite_achat),0) AS quantite_achetee,
    COALESCE(SUM(total_achat),0) AS montant_total,COALESCE(AVG(pu_achat_piece),0) AS cout_moyen_piece,
    MAX(date_peremption) AS derniere_peremption
    FROM {TABLE_NAME}
    WHERE produit_id = :id
    GROUP BY produit_id
    """
    return fetch_one(query, {"id": produit_id}) or {}

def get_top_produits_achetes(limit=10):
    """Retourne les produits les plus achetes."""
    query = f"""
    SELECT p.produit_id,p.code_produit,p.nom_produit,COALESCE(SUM(la.quantite_achat),0) AS quantite_achetee,
    COALESCE(SUM(la.total_achat),0) AS montant_total
    FROM {TABLE_NAME} la
    JOIN {PRODUITS_TABLE} p ON p.produit_id = la.produit_id
    GROUP BY p.produit_id,p.code_produit,p.nom_produit
    ORDER BY quantite_achetee DESC
    LIMIT :limit
    """
    return read_sql_dataframe(query, {"limit": int(limit)})

def get_expiring_products(days=30):
    """Retourne les produits proches de la peremption."""
    query = f"""
    SELECT la.*,p.code_produit,p.nom_produit
    FROM {TABLE_NAME} la
    JOIN {PRODUITS_TABLE} p ON p.produit_id = la.produit_id
    WHERE la.date_peremption IS NOT NULL AND la.date_peremption <= CURRENT_DATE + (:days || ' days')::interval
    ORDER BY la.date_peremption
    """
    return read_sql_dataframe(query, {"days": int(days)})

def get_lignes_achat_kpis():
    """Retourne les KPIs des lignes d'achat."""
    stats = get_lignes_achat_statistics()
    return {
        "total_lignes": int(stats.get("total_lignes", 0)),
        "total_cartons": int(stats.get("total_cartons", 0)),
        "total_quantite": int(stats.get("total_quantite", 0)),
        "montant_total": float(stats.get("montant_total", 0)),
        "cout_moyen_piece": float(stats.get("cout_moyen_piece", 0))
    }

__all__ = [
    "get_all_lignes_achat","get_ligne_achat_by_id","get_lignes_by_achat","get_lignes_achat_incoherentes","get_lignes_by_product","search_lignes_achat",
    "ligne_achat_exists","insert_ligne_achat","create_ligne_achat","update_ligne_achat","delete_ligne_achat",
    "calculate_ligne_achat_total","calculate_quantite_achat","calculate_pu_achat_piece","calculate_achat_total","calculate_achat_quantity",
    "count_lignes_achat","get_lignes_achat_statistics","get_product_achat_statistics","get_top_produits_achetes","get_expiring_products","get_lignes_achat_kpis"
]

