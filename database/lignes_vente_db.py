# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : lignes_vente_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar
from database.ventes_db import vente_exists
from database.produits_db import product_exists

# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("database")
TABLE_NAME = "dim_lignes_vente"
VENTES_TABLE = "fact_ventes"
PRODUITS_TABLE = "dim_produits"
ID_COLUMN = "ligne_vente_id"
TYPE_VENTE_VALUES = {"Normale","Declassee - produit abime","Promotion","Don"}

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

def normalize_type_vente(type_vente):
    """Normalise le type de vente."""
    value = str(type_vente or "Normale").strip()
    return value if value in TYPE_VENTE_VALUES else "Normale"


def get_product_stock(produit_id):
    """Retourne le stock actuel d'un produit."""
    value = get_scalar(f"SELECT COALESCE(stock_actuel,0) FROM {PRODUITS_TABLE} WHERE produit_id = :id", {"id": produit_id})
    return int(value or 0)


def get_vente_date(vente_id):
    """Retourne la date d'une vente."""
    row=fetch_one(f"SELECT date_vente FROM {VENTES_TABLE} WHERE vente_id=:vente_id", {"vente_id": vente_id})
    return row.get("date_vente") if row else None

def get_last_purchase_cost_before_sale(produit_id, vente_id=None, date_vente=None):
    """Retourne le dernier cout d'achat du produit avant la date de vente."""
    if date_vente is None and vente_id:
        date_vente=get_vente_date(vente_id)
    if not produit_id or not date_vente:
        return 0.0
    row=fetch_one("""
        SELECT la.pu_achat_piece
        FROM dim_lignes_achat la
        JOIN fact_achats a ON a.achat_id=la.achat_id
        WHERE la.produit_id=:produit_id AND a.date_achat<=:date_vente AND la.pu_achat_piece IS NOT NULL
        ORDER BY a.date_achat DESC,la.ligne_achat_id DESC
        LIMIT 1
    """, {"produit_id": produit_id, "date_vente": date_vente})
    return _to_float(row.get("pu_achat_piece")) if row else 0.0

def get_last_sale_price_before_sale(produit_id, vente_id=None, date_vente=None, exclude_ligne_id=None):
    """Retourne le dernier prix de vente du produit avant la date de vente."""
    if date_vente is None and vente_id:
        date_vente=get_vente_date(vente_id)
    if not produit_id or not date_vente:
        return 0.0
    query="""
        SELECT lv.pu_vente
        FROM dim_lignes_vente lv
        JOIN fact_ventes v ON v.vente_id=lv.vente_id
        WHERE lv.produit_id=:produit_id AND v.date_vente<=:date_vente AND lv.pu_vente IS NOT NULL
    """
    params={"produit_id": produit_id, "date_vente": date_vente}
    if exclude_ligne_id:
        query += " AND lv.ligne_vente_id<>:exclude_ligne_id"
        params["exclude_ligne_id"]=exclude_ligne_id
    query += " ORDER BY v.date_vente DESC,lv.ligne_vente_id DESC LIMIT 1"
    row=fetch_one(query,params)
    return _to_float(row.get("pu_vente")) if row else 0.0
def validate_ligne_vente_data(vente_id, produit_id, qte_vente, pu_vente, cout_unitaire=None, old_qte=0, old_produit_id=None, type_vente="Normale"):
    """Valide une ligne de vente."""
    qte_vente = _to_int(qte_vente)
    pu_vente = _to_float(pu_vente)
    cout_unitaire = None if cout_unitaire is None else _to_float(cout_unitaire)
    type_vente = normalize_type_vente(type_vente)
    if type_vente not in TYPE_VENTE_VALUES:
        return False, "Type de vente invalide."
    if not vente_id or not vente_exists(vente_id):
        return False, "La vente selectionnee n'existe pas."
    if not produit_id or not product_exists(produit_id):
        return False, "Le produit selectionne n'existe pas."
    if qte_vente <= 0:
        return False, "La quantite vendue doit etre superieure a 0."
    if pu_vente < 0:
        return False, "Le prix de vente ne peut pas etre negatif."
    if cout_unitaire is not None and cout_unitaire < 0:
        return False, "Le cout unitaire ne peut pas etre negatif."
    stock = get_product_stock(produit_id)
    available_stock = stock + old_qte if old_produit_id == produit_id else stock
    if available_stock < qte_vente:
        return False, f"Stock insuffisant. Stock disponible : {available_stock}."
    return True, "OK"

def ligne_vente_exists(ligne_vente_id):
    """Verifie si une ligne de vente existe."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return record_exists(query, {"id": ligne_vente_id})

def product_already_in_vente(vente_id, produit_id, exclude_id=None, type_vente="Normale"):
    """Verifie si un produit/type de vente est deja present dans une vente."""
    type_vente = normalize_type_vente(type_vente)
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE vente_id = :vente_id AND produit_id = :produit_id AND COALESCE(type_vente,'Normale') = :type_vente"
    params = {"vente_id": vente_id, "produit_id": produit_id, "type_vente": type_vente}
    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id
    return record_exists(query, params)

# ============================================================
# 3. LECTURE
# ============================================================

def get_all_lignes_vente():
    """Retourne toutes les lignes de vente avec produit et vente."""
    query = f"""
    SELECT lv.*,p.code_produit,p.nom_produit,v.date_vente,v.vendeur_id
    FROM {TABLE_NAME} lv
    LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = lv.produit_id
    LEFT JOIN {VENTES_TABLE} v ON v.vente_id = lv.vente_id
    ORDER BY lv.vente_id DESC,lv.ligne_vente_id
    """
    return read_sql_dataframe(query)

def get_ligne_vente_by_id(ligne_vente_id):
    """Retourne une ligne de vente par ID."""
    query = f"""
    SELECT lv.*,p.code_produit,p.nom_produit,v.date_vente
    FROM {TABLE_NAME} lv
    LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = lv.produit_id
    LEFT JOIN {VENTES_TABLE} v ON v.vente_id = lv.vente_id
    WHERE lv.{ID_COLUMN} = :id
    """
    return fetch_one(query, {"id": ligne_vente_id})

def get_lignes_by_vente(vente_id):
    """Retourne les lignes d'une vente."""
    query = f"""
    SELECT lv.*,p.code_produit,p.nom_produit
    FROM {TABLE_NAME} lv
    LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = lv.produit_id
    WHERE lv.vente_id = :id
    ORDER BY lv.ligne_vente_id
    """
    return read_sql_dataframe(query, {"id": vente_id})

def get_lignes_by_product(produit_id):
    """Retourne les lignes de vente d'un produit."""
    query = f"""
    SELECT lv.*,v.date_vente
    FROM {TABLE_NAME} lv
    LEFT JOIN {VENTES_TABLE} v ON v.vente_id = lv.vente_id
    WHERE lv.produit_id = :id
    ORDER BY v.date_vente DESC,lv.ligne_vente_id DESC
    """
    return read_sql_dataframe(query, {"id": produit_id})

def search_lignes_vente(vente_id=None, produit_id=None, keyword=None, start_date=None, end_date=None):
    """Recherche avancee des lignes de vente."""
    query = f"""
    SELECT lv.*,p.code_produit,p.nom_produit,v.date_vente
    FROM {TABLE_NAME} lv
    LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = lv.produit_id
    LEFT JOIN {VENTES_TABLE} v ON v.vente_id = lv.vente_id
    WHERE 1=1
    """
    params = {}
    if vente_id is not None:
        query += " AND lv.vente_id = :vente_id"
        params["vente_id"] = vente_id
    if produit_id is not None:
        query += " AND lv.produit_id = :produit_id"
        params["produit_id"] = produit_id
    if keyword:
        query += " AND (p.code_produit ILIKE :keyword OR p.nom_produit ILIKE :keyword)"
        params["keyword"] = f"%{keyword}%"
    if start_date is not None:
        query += " AND v.date_vente >= :start_date"
        params["start_date"] = start_date
    if end_date is not None:
        query += " AND v.date_vente <= :end_date"
        params["end_date"] = end_date
    query += " ORDER BY lv.vente_id DESC,lv.ligne_vente_id"
    return read_sql_dataframe(query, params)

# ============================================================
# 4. INSERTION ET MODIFICATION
# ============================================================

def insert_ligne_vente(vente_id, produit_id, qte_vente, pu_vente, cout_unitaire=None, type_vente="Normale"):
    """Insere une ligne de vente. Les triggers calculent montants et stock."""
    qte_vente = _to_int(qte_vente)
    pu_vente = _to_float(pu_vente)
    type_vente = normalize_type_vente(type_vente)
    if cout_unitaire in (None, ""):
        cout_unitaire = get_last_purchase_cost_before_sale(produit_id, vente_id=vente_id)
    valid, message = validate_ligne_vente_data(vente_id, produit_id, qte_vente, pu_vente, cout_unitaire, type_vente=type_vente)
    if not valid:
        logger.warning(message)
        return False
    if product_already_in_vente(vente_id, produit_id, type_vente=type_vente):
        logger.warning("Ce produit existe deja dans cette vente.")
        return False
    if cout_unitaire is None:
        query = f"INSERT INTO {TABLE_NAME} (vente_id,produit_id,qte_vente,pu_vente,type_vente) VALUES (:vente_id,:produit_id,:qte_vente,:pu_vente,:type_vente)"
        params = {"vente_id": vente_id, "produit_id": produit_id, "qte_vente": qte_vente, "pu_vente": pu_vente, "type_vente": type_vente}
    else:
        query = f"INSERT INTO {TABLE_NAME} (vente_id,produit_id,qte_vente,pu_vente,cout_unitaire,type_vente) VALUES (:vente_id,:produit_id,:qte_vente,:pu_vente,:cout_unitaire,:type_vente)"
        params = {"vente_id": vente_id, "produit_id": produit_id, "qte_vente": qte_vente, "pu_vente": pu_vente, "cout_unitaire": _to_float(cout_unitaire), "type_vente": type_vente}
    return execute_query(query, params)

def create_ligne_vente(vente_id, produit_id, qte_vente, pu_vente, cout_unitaire=None, type_vente="Normale"):
    """Wrapper utilise par Streamlit."""
    return insert_ligne_vente(vente_id, produit_id, qte_vente, pu_vente, cout_unitaire, type_vente)

def update_ligne_vente(ligne_vente_id, vente_id, produit_id, qte_vente, pu_vente, cout_unitaire=None, type_vente="Normale"):
    """Modifie une ligne de vente. Les triggers ajustent stock et total."""
    old_line = get_ligne_vente_by_id(ligne_vente_id)
    if not old_line:
        logger.warning("Ligne de vente inexistante.")
        return False
    qte_vente = _to_int(qte_vente)
    pu_vente = _to_float(pu_vente)
    type_vente = normalize_type_vente(type_vente)
    if cout_unitaire in (None, ""):
        cout_unitaire = get_last_purchase_cost_before_sale(produit_id, vente_id=vente_id)
    valid, message = validate_ligne_vente_data(vente_id, produit_id, qte_vente, pu_vente, cout_unitaire, old_qte=int(old_line["qte_vente"]), old_produit_id=old_line["produit_id"], type_vente=type_vente)
    if not valid:
        logger.warning(message)
        return False
    if product_already_in_vente(vente_id, produit_id, exclude_id=ligne_vente_id, type_vente=type_vente):
        logger.warning("Ce produit existe deja dans cette vente.")
        return False
    if cout_unitaire is None:
        query = f"""
        UPDATE {TABLE_NAME}
        SET vente_id = :vente_id,produit_id = :produit_id,qte_vente = :qte_vente,pu_vente = :pu_vente,cout_unitaire = NULL,type_vente = :type_vente
        WHERE {ID_COLUMN} = :id
        """
        params = {"id": ligne_vente_id, "vente_id": vente_id, "produit_id": produit_id, "qte_vente": qte_vente, "pu_vente": pu_vente, "type_vente": type_vente}
    else:
        query = f"""
        UPDATE {TABLE_NAME}
        SET vente_id = :vente_id,produit_id = :produit_id,qte_vente = :qte_vente,pu_vente = :pu_vente,cout_unitaire = :cout_unitaire,type_vente = :type_vente
        WHERE {ID_COLUMN} = :id
        """
        params = {"id": ligne_vente_id, "vente_id": vente_id, "produit_id": produit_id, "qte_vente": qte_vente, "pu_vente": pu_vente, "cout_unitaire": _to_float(cout_unitaire), "type_vente": type_vente}
    return execute_query(query, params)

# ============================================================
# 5. SUPPRESSION ET CALCULS
# ============================================================

def delete_ligne_vente(ligne_vente_id):
    """Supprime une ligne de vente. Les triggers ajustent stock et total."""
    if not ligne_vente_exists(ligne_vente_id):
        logger.warning("Ligne de vente inexistante.")
        return False
    query = f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": ligne_vente_id})

def calculate_ligne_vente_total(qte_vente, pu_vente):
    """Calcule le total d'une ligne de vente."""
    return round(max(_to_int(qte_vente), 0) * max(_to_float(pu_vente), 0), 2)

def calculate_vente_total(vente_id):
    """Calcule le total des lignes d'une vente."""
    value = get_scalar(f"SELECT COALESCE(SUM(montant_ligne),0) FROM {TABLE_NAME} WHERE vente_id = :id", {"id": vente_id})
    return float(value or 0)

def calculate_vente_quantity(vente_id):
    """Calcule la quantite totale vendue."""
    value = get_scalar(f"SELECT COALESCE(SUM(qte_vente),0) FROM {TABLE_NAME} WHERE vente_id = :id", {"id": vente_id})
    return int(value or 0)

def calculate_vente_profit(vente_id):
    """Calcule la marge d'une vente."""
    value = get_scalar(f"SELECT COALESCE(SUM(montant_ligne - COALESCE(cout_total,0)),0) FROM {TABLE_NAME} WHERE vente_id = :id", {"id": vente_id})
    return float(value or 0)

# ============================================================
# 6. STATISTIQUES ET KPI
# ============================================================

def count_lignes_vente():
    """Compte les lignes de vente."""
    value = get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    return int(value or 0)

def get_lignes_vente_statistics():
    """Retourne les statistiques des lignes de vente."""
    query = f"""
    SELECT COUNT(*) AS total_lignes,COALESCE(SUM(qte_vente),0) AS total_quantite,
    COALESCE(SUM(montant_ligne),0) AS chiffre_affaires,COALESCE(SUM(cout_total),0) AS cout_total,
    COALESCE(SUM(montant_ligne - COALESCE(cout_total,0)),0) AS marge_brute,COALESCE(AVG(pu_vente),0) AS prix_moyen
    FROM {TABLE_NAME}
    """
    return fetch_one(query) or {}

def get_product_vente_statistics(produit_id):
    """Retourne les statistiques de vente d'un produit."""
    query = f"""
    SELECT produit_id,COUNT(*) AS total_ventes,COALESCE(SUM(qte_vente),0) AS quantite_vendue,
    COALESCE(SUM(montant_ligne),0) AS chiffre_affaires,COALESCE(SUM(cout_total),0) AS cout_total,
    COALESCE(SUM(montant_ligne - COALESCE(cout_total,0)),0) AS marge_brute
    FROM {TABLE_NAME}
    WHERE produit_id = :id
    GROUP BY produit_id
    """
    return fetch_one(query, {"id": produit_id}) or {}

def get_top_produits_vendus(limit=10):
    """Retourne les produits les plus vendus."""
    query = f"""
    SELECT p.produit_id,p.code_produit,p.nom_produit,COALESCE(SUM(lv.qte_vente),0) AS quantite_vendue,
    COALESCE(SUM(lv.montant_ligne),0) AS chiffre_affaires,COALESCE(SUM(lv.montant_ligne - COALESCE(lv.cout_total,0)),0) AS marge_brute
    FROM {TABLE_NAME} lv
    JOIN {PRODUITS_TABLE} p ON p.produit_id = lv.produit_id
    GROUP BY p.produit_id,p.code_produit,p.nom_produit
    ORDER BY quantite_vendue DESC
    LIMIT :limit
    """
    return read_sql_dataframe(query, {"limit": int(limit)})

def get_lignes_vente_kpis():
    """Retourne les KPIs des lignes de vente."""
    stats = get_lignes_vente_statistics()
    return {
        "total_lignes": int(stats.get("total_lignes", 0)),
        "total_quantite": int(stats.get("total_quantite", 0)),
        "chiffre_affaires": float(stats.get("chiffre_affaires", 0)),
        "cout_total": float(stats.get("cout_total", 0)),
        "marge_brute": float(stats.get("marge_brute", 0)),
        "prix_moyen": float(stats.get("prix_moyen", 0))
    }

__all__ = [
    "get_all_lignes_vente","get_ligne_vente_by_id","get_last_purchase_cost_before_sale","get_last_sale_price_before_sale","get_lignes_by_vente","get_lignes_by_product","search_lignes_vente",
    "ligne_vente_exists","insert_ligne_vente","create_ligne_vente","update_ligne_vente","delete_ligne_vente",
    "calculate_ligne_vente_total","calculate_vente_total","calculate_vente_quantity","calculate_vente_profit",
    "count_lignes_vente","get_lignes_vente_statistics","get_product_vente_statistics","get_top_produits_vendus","get_lignes_vente_kpis"
]

