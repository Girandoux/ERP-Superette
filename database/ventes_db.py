# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : ventes_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar
from database.dates_db import date_exists,ensure_month_dates

# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("database")
TABLE_NAME = "fact_ventes"
LINES_TABLE = "dim_lignes_vente"
VENDEURS_TABLE = "dim_vendeurs"
DATE_TABLE = "dim_date"
ID_COLUMN = "vente_id"

# ============================================================
# 2. VALIDATION
# ============================================================

def validate_vente_data(date_vente, vendeur_id):
    """Valide les donnees d'une vente."""
    if not date_vente:
        return False, "La date de vente est obligatoire."
    if not vendeur_id:
        return False, "Le vendeur est obligatoire."
    return True, "OK"

def vendeur_exists(vendeur_id):
    """Verifie si un vendeur existe."""
    query = f"SELECT 1 FROM {VENDEURS_TABLE} WHERE vendeur_id = :id"
    return record_exists(query, {"id": vendeur_id})


def vente_exists(vente_id):
    """Verifie si une vente existe."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return record_exists(query, {"id": vente_id})

def can_save_vente(date_vente, vendeur_id):
    """Verifie si une vente peut etre inseree ou modifiee."""
    valid, message = validate_vente_data(date_vente, vendeur_id)
    if not valid:
        return False, message
    if not ensure_month_dates(date_vente):
        return False, "Le mois de la date de vente n'a pas pu etre cree dans dim_date."
    if not date_exists(date_vente):
        return False, "La date de vente n'existe pas dans dim_date."
    if not vendeur_exists(vendeur_id):
        return False, "Le vendeur selectionne n'existe pas."
    return True, "OK"

# ============================================================
# 3. LECTURE
# ============================================================

def get_all_ventes():
    """Retourne toutes les ventes avec vendeur."""
    query = f"""
    SELECT v.vente_id,v.date_vente,v.date_id,v.vendeur_id,ve.nom_vendeur,v.total_vente
    FROM {TABLE_NAME} v
    LEFT JOIN {VENDEURS_TABLE} ve ON ve.vendeur_id = v.vendeur_id
    ORDER BY v.date_vente DESC,v.vente_id DESC
    """
    return read_sql_dataframe(query)

def get_vente_by_id(vente_id):
    """Retourne une vente par ID."""
    query = f"""
    SELECT v.*,ve.nom_vendeur
    FROM {TABLE_NAME} v
    LEFT JOIN {VENDEURS_TABLE} ve ON ve.vendeur_id = v.vendeur_id
    WHERE v.{ID_COLUMN} = :id
    """
    return fetch_one(query, {"id": vente_id})

def search_ventes(keyword):
    """Recherche une vente par ID ou vendeur."""
    keyword = str(keyword).strip()
    if not keyword:
        return pd.DataFrame()
    query = f"""
    SELECT v.*,ve.nom_vendeur
    FROM {TABLE_NAME} v
    LEFT JOIN {VENDEURS_TABLE} ve ON ve.vendeur_id = v.vendeur_id
    WHERE CAST(v.vente_id AS TEXT) ILIKE :keyword OR ve.nom_vendeur ILIKE :keyword
    ORDER BY v.date_vente DESC,v.vente_id DESC
    """
    return read_sql_dataframe(query, {"keyword": f"%{keyword}%"})

def get_ventes_by_vendeur(vendeur_id):
    """Retourne les ventes d'un vendeur."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE vendeur_id = :id ORDER BY date_vente DESC,vente_id DESC"
    return read_sql_dataframe(query, {"id": vendeur_id})

def get_ventes_by_date(start_date, end_date):
    """Retourne les ventes sur une periode."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE date_vente BETWEEN :start_date AND :end_date ORDER BY date_vente DESC,vente_id DESC"
    return read_sql_dataframe(query, {"start_date": start_date, "end_date": end_date})

def get_last_vente():
    """Retourne la derniere vente."""
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY date_vente DESC,vente_id DESC LIMIT 1"
    return fetch_one(query)

# ============================================================
# 4. INSERTION ET MODIFICATION
# ============================================================

def insert_vente(date_vente, vendeur_id, total_vente=0):
    """Insere une vente."""
    valid, message = can_save_vente(date_vente, vendeur_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    INSERT INTO {TABLE_NAME} (date_vente,date_id,vendeur_id,total_vente)
    VALUES (:date_vente,:date_id,:vendeur_id,:total_vente)
    """
    return execute_query(query, {"date_vente": date_vente, "date_id": date_vente, "vendeur_id": vendeur_id, "total_vente": total_vente})

def create_vente(date_vente, vendeur_id):
    """Wrapper utilise par Streamlit."""
    return insert_vente(date_vente, vendeur_id, total_vente=0)

def update_vente(vente_id, date_vente, vendeur_id):
    """Modifie une vente."""
    if not vente_exists(vente_id):
        logger.warning("Vente inexistante.")
        return False
    valid, message = can_save_vente(date_vente, vendeur_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    UPDATE {TABLE_NAME}
    SET date_vente = :date_vente,date_id = :date_id,vendeur_id = :vendeur_id
    WHERE {ID_COLUMN} = :id
    """
    success = execute_query(query, {"id": vente_id, "date_vente": date_vente, "date_id": date_vente, "vendeur_id": vendeur_id})
    if success:
        recalculate_vente_total(vente_id)
    return success

# ============================================================
# 5. SUPPRESSION ET CALCULS
# ============================================================

def count_lignes_by_vente(vente_id):
    """Compte les lignes d'une vente."""
    value = get_scalar(f"SELECT COUNT(*) FROM {LINES_TABLE} WHERE vente_id = :id", {"id": vente_id})
    return int(value or 0)

def can_delete_vente(vente_id):
    """Verifie si une vente peut etre supprimee."""
    if not vente_exists(vente_id):
        return False, "Vente inexistante."
    return True, "OK"

def delete_vente(vente_id):
    """Supprime une vente et ses lignes. Les triggers ajustent le stock."""
    valid, message = can_delete_vente(vente_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": vente_id})

def calculate_vente_total(vente_id):
    """Calcule le total d'une vente."""
    value = get_scalar(f"SELECT COALESCE(SUM(montant_ligne),0) FROM {LINES_TABLE} WHERE vente_id = :id", {"id": vente_id})
    return float(value or 0)

def calculate_vente_quantity(vente_id):
    """Calcule la quantite totale vendue."""
    value = get_scalar(f"SELECT COALESCE(SUM(qte_vente),0) FROM {LINES_TABLE} WHERE vente_id = :id", {"id": vente_id})
    return int(value or 0)

def recalculate_vente_total(vente_id):
    """Recalcule et met a jour total_vente."""
    total = calculate_vente_total(vente_id)
    query = f"UPDATE {TABLE_NAME} SET total_vente = :total WHERE {ID_COLUMN} = :id"
    execute_query(query, {"id": vente_id, "total": total})
    return total

# ============================================================
# 6. STATISTIQUES ET KPI
# ============================================================

def count_ventes():
    """Compte les ventes."""
    value = get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    return int(value or 0)

def get_ventes_statistics():
    """Retourne les statistiques des ventes."""
    query = f"""
    SELECT COUNT(*) AS total_ventes,COALESCE(SUM(total_vente),0) AS chiffre_affaires,
    COALESCE(AVG(total_vente),0) AS ticket_moyen,COALESCE(MAX(total_vente),0) AS vente_max,
    COALESCE(MIN(total_vente),0) AS vente_min,MIN(date_vente) AS premiere_vente,MAX(date_vente) AS derniere_vente
    FROM {TABLE_NAME}
    """
    return fetch_one(query) or {}

def get_monthly_ventes():
    """Retourne les ventes par mois."""
    query = f"""
    SELECT d.annee,d.mois,d.nom_mois,COUNT(v.vente_id) AS total_ventes,COALESCE(SUM(v.total_vente),0) AS chiffre_affaires
    FROM {TABLE_NAME} v
    JOIN {DATE_TABLE} d ON d.date_id = v.date_id
    GROUP BY d.annee,d.mois,d.nom_mois
    ORDER BY d.annee,d.mois
    """
    return read_sql_dataframe(query)

def get_vendeur_statistics():
    """Retourne les ventes par vendeur."""
    query = f"""
    SELECT ve.vendeur_id,ve.nom_vendeur,COUNT(v.vente_id) AS total_ventes,COALESCE(SUM(v.total_vente),0) AS chiffre_affaires,
    COALESCE(AVG(v.total_vente),0) AS ticket_moyen
    FROM {VENDEURS_TABLE} ve
    LEFT JOIN {TABLE_NAME} v ON v.vendeur_id = ve.vendeur_id
    GROUP BY ve.vendeur_id,ve.nom_vendeur
    ORDER BY chiffre_affaires DESC
    """
    return read_sql_dataframe(query)

def get_ventes_kpis():
    """Retourne les KPIs ventes."""
    stats = get_ventes_statistics()
    return {
        "total_ventes": int(stats.get("total_ventes", 0)),
        "chiffre_affaires": float(stats.get("chiffre_affaires", 0)),
        "ticket_moyen": float(stats.get("ticket_moyen", 0)),
        "vente_max": float(stats.get("vente_max", 0)),
        "vente_min": float(stats.get("vente_min", 0)),
        "premiere_vente": stats.get("premiere_vente"),
        "derniere_vente": stats.get("derniere_vente")
    }

__all__ = [
    "get_all_ventes","get_vente_by_id","search_ventes","get_ventes_by_vendeur","get_ventes_by_date","get_last_vente",
    "vente_exists","insert_vente","create_vente","update_vente","delete_vente","count_lignes_by_vente",
    "calculate_vente_total","calculate_vente_quantity","recalculate_vente_total","count_ventes",
    "get_ventes_statistics","get_monthly_ventes","get_vendeur_statistics","get_ventes_kpis"
]

