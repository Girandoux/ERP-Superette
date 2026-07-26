# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : acheteurs_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar

# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("database")
TABLE_NAME = "dim_acheteurs"
ACHATS_TABLE = "fact_achats"
ID_COLUMN = "acheteur_id"
NAME_COLUMN = "nom_acheteur"

# ============================================================
# 2. VALIDATION
# ============================================================

def _normalize_name(value):
    """Nettoie le nom acheteur."""
    return " ".join(str(value).strip().split()) if value is not None else ""

def validate_acheteur_name(nom_acheteur):
    """Valide le nom acheteur."""
    nom_acheteur = _normalize_name(nom_acheteur)
    if not nom_acheteur:
        return False, "Le nom acheteur est obligatoire."
    if len(nom_acheteur) > 100:
        return False, "Le nom acheteur ne doit pas depasser 100 caracteres."
    return True, "OK"

def acheteur_name_exists(nom_acheteur, exclude_id=None):
    """Verifie si un acheteur existe deja."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER({NAME_COLUMN}) = LOWER(:name)"
    params = {"name": _normalize_name(nom_acheteur)}
    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id
    return record_exists(query, params)

def can_save_acheteur(nom_acheteur, exclude_id=None):
    """Verifie si un acheteur peut etre enregistre."""
    valid, message = validate_acheteur_name(nom_acheteur)
    if not valid:
        return False, message
    if acheteur_name_exists(nom_acheteur, exclude_id):
        return False, "Cet acheteur existe deja."
    return True, "OK"

# ============================================================
# 3. LECTURE
# ============================================================

def get_all_acheteurs():
    """Retourne tous les acheteurs."""
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY {NAME_COLUMN}"
    return read_sql_dataframe(query)

def get_acheteur_by_id(acheteur_id):
    """Retourne un acheteur par ID."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return fetch_one(query, {"id": acheteur_id})

def get_acheteur_by_name(nom_acheteur):
    """Retourne un acheteur par nom."""
    query = f"SELECT * FROM {TABLE_NAME} WHERE LOWER({NAME_COLUMN}) = LOWER(:name)"
    return fetch_one(query, {"name": _normalize_name(nom_acheteur)})

def acheteur_exists(acheteur_id):
    """Verifie si un acheteur existe."""
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return record_exists(query, {"id": acheteur_id})

def search_acheteurs(keyword):
    """Recherche un acheteur par nom."""
    keyword = _normalize_name(keyword)
    if not keyword:
        return pd.DataFrame()
    query = f"SELECT * FROM {TABLE_NAME} WHERE {NAME_COLUMN} ILIKE :keyword ORDER BY {NAME_COLUMN}"
    return read_sql_dataframe(query, {"keyword": f"%{keyword}%"})

def count_acheteurs():
    """Compte les acheteurs."""
    value = get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    return int(value or 0)

# ============================================================
# 4. INSERTION ET MODIFICATION
# ============================================================

def insert_acheteur(nom_acheteur):
    """Insere un acheteur."""
    nom_acheteur = _normalize_name(nom_acheteur)
    valid, message = can_save_acheteur(nom_acheteur)
    if not valid:
        logger.warning(message)
        return False
    query = f"INSERT INTO {TABLE_NAME} ({NAME_COLUMN}) VALUES (:name)"
    return execute_query(query, {"name": nom_acheteur})

def create_acheteur(nom_acheteur):
    """Wrapper utilise par Streamlit."""
    return insert_acheteur(nom_acheteur)

def update_acheteur(acheteur_id, nom_acheteur):
    """Modifie un acheteur."""
    if not acheteur_exists(acheteur_id):
        logger.warning("Acheteur inexistant.")
        return False
    nom_acheteur = _normalize_name(nom_acheteur)
    valid, message = can_save_acheteur(nom_acheteur, exclude_id=acheteur_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"UPDATE {TABLE_NAME} SET {NAME_COLUMN} = :name WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": acheteur_id, "name": nom_acheteur})

# ============================================================
# 5. SUPPRESSION PROTEGEE
# ============================================================

def count_achats_by_acheteur(acheteur_id):
    """Compte les achats lies a un acheteur."""
    query = f"SELECT COUNT(*) AS total FROM {ACHATS_TABLE} WHERE {ID_COLUMN} = :id"
    result = fetch_one(query, {"id": acheteur_id})
    return int(result["total"]) if result else 0

def can_delete_acheteur(acheteur_id):
    """Verifie si un acheteur peut etre supprime."""
    if not acheteur_exists(acheteur_id):
        return False, "Acheteur inexistant."
    total = count_achats_by_acheteur(acheteur_id)
    if total > 0:
        return False, f"Suppression impossible : {total} achat(s) utilisent cet acheteur."
    return True, "OK"

def delete_acheteur(acheteur_id):
    """Supprime un acheteur si aucun achat ne l'utilise."""
    valid, message = can_delete_acheteur(acheteur_id)
    if not valid:
        logger.warning(message)
        return False
    query = f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"
    return execute_query(query, {"id": acheteur_id})

# ============================================================
# 6. STATISTIQUES
# ============================================================

def get_acheteurs_with_achats():
    """Retourne les acheteurs avec leur nombre et montant d'achats."""
    query = f"""
    SELECT a.{ID_COLUMN},a.{NAME_COLUMN},COUNT(f.achat_id) AS total_achats,COALESCE(SUM(f.total_facture),0) AS montant_total
    FROM {TABLE_NAME} a
    LEFT JOIN {ACHATS_TABLE} f ON f.{ID_COLUMN} = a.{ID_COLUMN}
    GROUP BY a.{ID_COLUMN},a.{NAME_COLUMN}
    ORDER BY a.{NAME_COLUMN}
    """
    return read_sql_dataframe(query)

def get_acheteur_kpis():
    """Retourne les KPIs acheteurs."""
    df = get_acheteurs_with_achats()
    if df.empty:
        return {"total_acheteurs": 0, "acheteurs_utilises": 0, "acheteurs_non_utilises": 0, "montant_total_achats": 0}
    used = int((df["total_achats"] > 0).sum())
    return {
        "total_acheteurs": len(df),
        "acheteurs_utilises": used,
        "acheteurs_non_utilises": len(df) - used,
        "montant_total_achats": float(df["montant_total"].sum())
    }

__all__ = [
    "get_all_acheteurs",
    "get_acheteur_by_id",
    "get_acheteur_by_name",
    "acheteur_exists",
    "search_acheteurs",
    "count_acheteurs",
    "insert_acheteur",
    "create_acheteur",
    "update_acheteur",
    "delete_acheteur",
    "can_delete_acheteur",
    "count_achats_by_acheteur",
    "get_acheteurs_with_achats",
    "get_acheteur_kpis"
]

