# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : achats_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import re
from datetime import date
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar
from database.dates_db import date_exists,ensure_month_dates

# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("database")
TABLE_NAME = "fact_achats"
LINES_TABLE = "dim_lignes_achat"
ACHETEURS_TABLE = "dim_acheteurs"
DATE_TABLE = "dim_date"
ID_COLUMN = "achat_id"

# ============================================================
# 2. VALIDATION
# ============================================================

def _normalize_text(value):
    """Nettoie un texte."""
    return " ".join(str(value).strip().split()) if value is not None else ""

def _to_float(value, default=0):
    """Convertit une valeur en nombre."""
    try:
        return float(value)
    except Exception:
        return default

def validate_achat_data(date_achat, numero_facture, acheteur_id, frais_enlevement=0, type_achat="Achat fournisseur"):
    """Valide les donnees d'un achat."""
    numero_facture = _normalize_text(numero_facture)
    type_achat = _normalize_text(type_achat) or "Achat fournisseur"
    frais_enlevement = _to_float(frais_enlevement)
    if not date_achat:
        return False, "La date d'achat est obligatoire."
    if not numero_facture:
        return False, "Le numero de facture est obligatoire."
    if len(numero_facture) > 50:
        return False, "Le numero de facture ne doit pas depasser 50 caracteres."
    if len(type_achat) > 50:
        return False, "Le type d'achat ne doit pas depasser 50 caracteres."
    if not acheteur_id:
        return False, "L'acheteur est obligatoire."
    if frais_enlevement < 0:
        return False, "Les frais d'enlevement ne peuvent pas etre negatifs."
    return True, "OK"

def acheteur_exists(acheteur_id):
    """Verifie si un acheteur existe."""
    query = f"SELECT 1 FROM {ACHETEURS_TABLE} WHERE acheteur_id = :id"
    return record_exists(query, {"id": acheteur_id})


def achat_exists(achat_id):
    """Verifie si un achat existe."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return record_exists(query, {"id": achat_id})

def numero_facture_exists(numero_facture, exclude_id=None):
    """Verifie si un numero de facture existe deja."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER(numero_facture) = LOWER(:numero)"
    params = {"numero": _normalize_text(numero_facture)}
    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id
    return record_exists(query, params)

def can_save_achat(date_achat, numero_facture, acheteur_id, frais_enlevement=0, type_achat="Achat fournisseur", exclude_id=None):
    """Verifie si un achat peut etre insere ou modifie."""
    valid, message = validate_achat_data(date_achat, numero_facture, acheteur_id, frais_enlevement, type_achat)
    if not valid:
        return False, message
    if not ensure_month_dates(date_achat):
        return False, "Le mois de la date d'achat n'a pas pu etre cree dans dim_date."
    if not date_exists(date_achat):
        return False, "La date d'achat n'existe pas dans dim_date."
    if not acheteur_exists(acheteur_id):
        return False, "L'acheteur selectionne n'existe pas."
    if numero_facture_exists(numero_facture, exclude_id):
        return False, "Ce numero de facture existe deja."
    return True, "OK"

# ============================================================
# 3. LECTURE
# ============================================================

def get_all_achats():
    """Retourne tous les achats avec acheteur."""
    query = f"""
    SELECT a.achat_id,a.date_achat,a.date_id,a.numero_facture,a.acheteur_id,ac.nom_acheteur,a.frais_enlevement,a.total_facture,a.type_achat
    FROM {TABLE_NAME} a
    LEFT JOIN {ACHETEURS_TABLE} ac ON ac.acheteur_id = a.acheteur_id
    ORDER BY a.date_achat DESC,a.achat_id DESC
    """
    return read_sql_dataframe(query)

def get_achat_by_id(achat_id):
    """Retourne un achat par ID."""
    query = f"""
    SELECT a.*,ac.nom_acheteur
    FROM {TABLE_NAME} a
    LEFT JOIN {ACHETEURS_TABLE} ac ON ac.acheteur_id = a.acheteur_id
    WHERE a.{ID_COLUMN} = :id
    """
    return fetch_one(query, {"id": achat_id})

def get_achat_by_numero_facture(numero_facture):
    """Retourne un achat par numero de facture."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE LOWER(numero_facture) = LOWER(:numero)"
    return fetch_one(query, {"numero": _normalize_text(numero_facture)})

def search_achats(keyword):
    """Recherche un achat par facture ou acheteur."""
    keyword = _normalize_text(keyword)
    if not keyword:
        return pd.DataFrame()
    query = f"""
    SELECT a.*,ac.nom_acheteur
    FROM {TABLE_NAME} a
    LEFT JOIN {ACHETEURS_TABLE} ac ON ac.acheteur_id = a.acheteur_id
    WHERE a.numero_facture ILIKE :keyword OR ac.nom_acheteur ILIKE :keyword OR a.type_achat ILIKE :keyword
    ORDER BY a.date_achat DESC,a.achat_id DESC
    """
    return read_sql_dataframe(query, {"keyword": f"%{keyword}%"})

def get_achats_by_acheteur(acheteur_id):
    """Retourne les achats d'un acheteur."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE acheteur_id = :id ORDER BY date_achat DESC,achat_id DESC"
    return read_sql_dataframe(query, {"id": acheteur_id})

def get_achats_by_date(start_date, end_date):
    """Retourne les achats sur une periode."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE date_achat BETWEEN :start_date AND :end_date ORDER BY date_achat DESC,achat_id DESC"
    return read_sql_dataframe(query, {"start_date": start_date, "end_date": end_date})


def get_next_numero_facture(prefix="FAC", width=4):
    """Genere le prochain numero de facture selon le dernier numero existant."""
    rows = read_sql_dataframe(f"SELECT numero_facture FROM {TABLE_NAME} WHERE numero_facture IS NOT NULL ORDER BY {ID_COLUMN}")
    max_number = 0
    selected_prefix = prefix
    selected_width = width
    if not rows.empty:
        for value in rows["numero_facture"].dropna().astype(str):
            match = re.search(r"^(.*?)(\d+)$", value.strip())
            if not match:
                continue
            current_prefix = match.group(1).rstrip("-") or prefix
            current_number_text = match.group(2)
            current_number = int(current_number_text)
            if current_number >= max_number:
                max_number = current_number
                selected_prefix = current_prefix
                selected_width = len(current_number_text)
    return f"{selected_prefix}-{max_number + 1:0{selected_width}d}"
def get_last_achat():
    """Retourne le dernier achat."""
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY date_achat DESC,achat_id DESC LIMIT 1"
    return fetch_one(query)

# ============================================================
# 4. INSERTION ET MODIFICATION
# ============================================================

def insert_achat(date_achat, numero_facture, acheteur_id, frais_enlevement=0, total_facture=0, type_achat="Achat fournisseur"):
    """Insere un achat."""
    numero_facture = _normalize_text(numero_facture)
    type_achat = _normalize_text(type_achat) or "Achat fournisseur"
    frais_enlevement = _to_float(frais_enlevement)
    total_facture = _to_float(total_facture)
    valid, message = can_save_achat(date_achat, numero_facture, acheteur_id, frais_enlevement, type_achat)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    INSERT INTO {TABLE_NAME} (date_achat,date_id,numero_facture,acheteur_id,frais_enlevement,total_facture,type_achat)
    VALUES (:date_achat,:date_id,:numero_facture,:acheteur_id,:frais_enlevement,:total_facture,:type_achat)
    """
    params = {"date_achat": date_achat, "date_id": date_achat, "numero_facture": numero_facture, "acheteur_id": acheteur_id, "frais_enlevement": frais_enlevement, "total_facture": total_facture, "type_achat": type_achat}
    return execute_query(query, params)

def create_achat(date_achat, numero_facture, acheteur_id, frais_enlevement=0, type_achat="Achat fournisseur"):
    """Wrapper utilise par Streamlit."""
    return insert_achat(date_achat, numero_facture, acheteur_id, frais_enlevement, total_facture=frais_enlevement, type_achat=type_achat)

def update_achat(achat_id, date_achat, numero_facture, acheteur_id, frais_enlevement=0, type_achat="Achat fournisseur"):
    """Modifie un achat."""
    if not achat_exists(achat_id):
        logger.warning("Achat inexistant.")
        return False
    numero_facture = _normalize_text(numero_facture)
    type_achat = _normalize_text(type_achat) or "Achat fournisseur"
    frais_enlevement = _to_float(frais_enlevement)
    valid, message = can_save_achat(date_achat, numero_facture, acheteur_id, frais_enlevement, type_achat, exclude_id=achat_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    UPDATE {TABLE_NAME}
    SET date_achat = :date_achat,date_id = :date_id,numero_facture = :numero_facture,acheteur_id = :acheteur_id,frais_enlevement = :frais_enlevement,type_achat = :type_achat
    WHERE {ID_COLUMN} = :id
    """
    success = execute_query(query, {"id": achat_id, "date_achat": date_achat, "date_id": date_achat, "numero_facture": numero_facture, "acheteur_id": acheteur_id, "frais_enlevement": frais_enlevement, "type_achat": type_achat})
    if success:
        recalculate_achat_total(achat_id)
    return success

# ============================================================
# 5. SUPPRESSION ET CALCULS
# ============================================================

def count_lignes_by_achat(achat_id):
    """Compte les lignes d'un achat."""
    value = get_scalar(f"SELECT COUNT(*) FROM {LINES_TABLE} WHERE achat_id = :id", {"id": achat_id})
    return int(value or 0)

def can_delete_achat(achat_id):
    """Verifie si un achat peut etre supprime."""
    if not achat_exists(achat_id):
        return False, "Achat inexistant."
    return True, "OK"

def delete_achat(achat_id):
    """Supprime un achat et ses lignes. Les triggers ajustent le stock."""
    valid, message = can_delete_achat(achat_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": achat_id})

def calculate_achat_total(achat_id):
    """Calcule le total facture d'un achat."""
    query = f"""
    SELECT COALESCE((SELECT SUM(total_achat) FROM {LINES_TABLE} WHERE achat_id = :id),0) + COALESCE((SELECT frais_enlevement FROM {TABLE_NAME} WHERE achat_id = :id),0) AS total
    """
    result = fetch_one(query, {"id": achat_id})
    return float(result["total"]) if result else 0.0

def calculate_achat_quantity(achat_id):
    """Calcule la quantite totale achetee."""
    value = get_scalar(f"SELECT COALESCE(SUM(quantite_achat),0) FROM {LINES_TABLE} WHERE achat_id = :id", {"id": achat_id})
    return int(value or 0)

def recalculate_achat_total(achat_id):
    """Recalcule et met a jour total_facture."""
    total = calculate_achat_total(achat_id)
    query = f"UPDATE {TABLE_NAME} SET total_facture = :total WHERE {ID_COLUMN} = :id"
    execute_query(query, {"id": achat_id, "total": total})
    return total

# ============================================================
# 6. STATISTIQUES ET KPI
# ============================================================

def count_achats():
    """Compte les achats."""
    value = get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    return int(value or 0)

def get_achats_statistics():
    """Retourne les statistiques des achats."""
    query = f"""
    SELECT COUNT(*) AS total_achats,COALESCE(SUM(total_facture),0) AS montant_total,
    COALESCE(AVG(total_facture),0) AS montant_moyen,COALESCE(MAX(total_facture),0) AS montant_max,
    COALESCE(MIN(total_facture),0) AS montant_min,MIN(date_achat) AS premier_achat,MAX(date_achat) AS dernier_achat
    FROM {TABLE_NAME}
    """
    return fetch_one(query) or {}

def get_monthly_achats():
    """Retourne les achats par mois."""
    query = f"""
    SELECT d.annee,d.mois,d.nom_mois,COUNT(a.achat_id) AS total_achats,COALESCE(SUM(a.total_facture),0) AS montant_total
    FROM {TABLE_NAME} a
    JOIN {DATE_TABLE} d ON d.date_id = a.date_id
    GROUP BY d.annee,d.mois,d.nom_mois
    ORDER BY d.annee,d.mois
    """
    return read_sql_dataframe(query)

def get_acheteur_statistics():
    """Retourne les achats par acheteur."""
    query = f"""
    SELECT ac.acheteur_id,ac.nom_acheteur,COUNT(a.achat_id) AS total_achats,COALESCE(SUM(a.total_facture),0) AS montant_total
    FROM {ACHETEURS_TABLE} ac
    LEFT JOIN {TABLE_NAME} a ON a.acheteur_id = ac.acheteur_id
    GROUP BY ac.acheteur_id,ac.nom_acheteur
    ORDER BY montant_total DESC
    """
    return read_sql_dataframe(query)

def get_achats_kpis():
    """Retourne les KPIs achats."""
    stats = get_achats_statistics()
    return {
        "total_achats": int(stats.get("total_achats", 0)),
        "montant_total": float(stats.get("montant_total", 0)),
        "montant_moyen": float(stats.get("montant_moyen", 0)),
        "montant_max": float(stats.get("montant_max", 0)),
        "montant_min": float(stats.get("montant_min", 0)),
        "premier_achat": stats.get("premier_achat"),
        "dernier_achat": stats.get("dernier_achat")
    }

__all__ = [
    "get_all_achats","get_achat_by_id","get_achat_by_numero_facture","search_achats","get_achats_by_acheteur","get_achats_by_date","get_next_numero_facture","get_last_achat",
    "achat_exists","date_exists","insert_achat","create_achat","update_achat","delete_achat","count_lignes_by_achat","calculate_achat_total","calculate_achat_quantity",
    "recalculate_achat_total","count_achats","get_achats_statistics","get_monthly_achats","get_acheteur_statistics","get_achats_kpis"
]

