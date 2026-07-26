# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : stock_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar

logger = logging.getLogger("database")
TABLE_NAME = "dim_produits"
CATEGORY_TABLE = "dim_categories"
LIGNES_ACHAT_TABLE = "dim_lignes_achat"


# ============================================================
# 1. FONCTIONS DU MODULE
# ============================================================

def _to_int(value, default=0):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    try:
        return int(value)
    except Exception:
        return default

def product_exists(produit_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return record_exists(f"SELECT 1 FROM {TABLE_NAME} WHERE produit_id = :id", {"id": produit_id})

def get_current_stock(produit_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    value = get_scalar(f"SELECT COALESCE(stock_actuel,0) FROM {TABLE_NAME} WHERE produit_id = :id", {"id": produit_id})
    return int(value or 0)

def get_stock_by_product(produit_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie,p.stock_min,COALESCE(p.stock_actuel,0) AS stock_actuel,p.actif
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    WHERE p.produit_id = :id
    """
    return fetch_one(query, {"id": produit_id})

def get_all_stock(active_only=True):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    where = "WHERE p.actif = TRUE" if active_only else ""
    query = f"""
    SELECT p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie,p.unite,p.stock_min,COALESCE(p.stock_actuel,0) AS stock_actuel,
    CASE WHEN COALESCE(p.stock_actuel,0) <= 0 THEN 'Rupture' WHEN COALESCE(p.stock_actuel,0) <= p.stock_min THEN 'Alerte' ELSE 'Normal' END AS statut_stock
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    {where}
    ORDER BY p.nom_produit
    """
    return read_sql_dataframe(query)

def get_low_stock_products():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT p.*,c.nom_categorie
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    WHERE COALESCE(p.stock_actuel,0) <= p.stock_min AND p.actif = TRUE
    ORDER BY COALESCE(p.stock_actuel,0),p.nom_produit
    """
    return read_sql_dataframe(query)

def get_out_of_stock_products():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT p.*,c.nom_categorie
    FROM {TABLE_NAME} p
    LEFT JOIN {CATEGORY_TABLE} c ON c.categorie_id = p.categorie_id
    WHERE COALESCE(p.stock_actuel,0) <= 0 AND p.actif = TRUE
    ORDER BY p.nom_produit
    """
    return read_sql_dataframe(query)

def set_stock(produit_id, nouveau_stock):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    nouveau_stock = _to_int(nouveau_stock)
    if nouveau_stock < 0 or not product_exists(produit_id):
        return False
    return execute_query(f"UPDATE {TABLE_NAME} SET stock_actuel = :stock WHERE produit_id = :id", {"id": produit_id, "stock": nouveau_stock})

def add_stock(produit_id, quantite):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    quantite = _to_int(quantite)
    if quantite <= 0 or not product_exists(produit_id):
        return False
    return execute_query(f"UPDATE {TABLE_NAME} SET stock_actuel = stock_actuel + :qte WHERE produit_id = :id", {"id": produit_id, "qte": quantite})

def remove_stock(produit_id, quantite):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    quantite = _to_int(quantite)
    if quantite <= 0 or not product_exists(produit_id):
        return False
    if get_current_stock(produit_id) < quantite:
        logger.warning("Stock insuffisant.")
        return False
    return execute_query(f"UPDATE {TABLE_NAME} SET stock_actuel = stock_actuel - :qte WHERE produit_id = :id", {"id": produit_id, "qte": quantite})

def get_stock_value():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
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

def get_stock_statistics():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT COUNT(*) AS total_produits,COUNT(*) FILTER (WHERE actif = TRUE) AS produits_actifs,
    COALESCE(SUM(stock_actuel),0) AS quantite_stock,
    COUNT(*) FILTER (WHERE COALESCE(stock_actuel,0) <= stock_min AND actif = TRUE) AS stock_faible,
    COUNT(*) FILTER (WHERE COALESCE(stock_actuel,0) <= 0 AND actif = TRUE) AS rupture
    FROM {TABLE_NAME}
    """
    return fetch_one(query) or {}

def get_stock_kpis():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    stats = get_stock_statistics()
    return {
        "total_produits": int(stats.get("total_produits", 0)),
        "produits_actifs": int(stats.get("produits_actifs", 0)),
        "quantite_stock": int(stats.get("quantite_stock", 0)),
        "stock_faible": int(stats.get("stock_faible", 0)),
        "rupture": int(stats.get("rupture", 0)),
        "valeur_stock": get_stock_value()
    }

__all__ = ["get_current_stock","get_stock_by_product","get_all_stock","get_low_stock_products","get_out_of_stock_products","set_stock","add_stock","remove_stock","get_stock_value","get_stock_statistics","get_stock_kpis"]

