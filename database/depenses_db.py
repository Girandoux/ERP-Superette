# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : depenses_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar
from database.dates_db import date_exists,ensure_month_dates

logger = logging.getLogger("database")
TABLE_NAME = "fact_depenses"
DATE_TABLE = "dim_date"
ID_COLUMN = "depense_id"


# ============================================================
# 1. FONCTIONS DU MODULE
# ============================================================

def _txt(value):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return " ".join(str(value).strip().split()) if value is not None else ""

def _num(value):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    try:
        return float(value)
    except Exception:
        return 0.0

def depense_exists(depense_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return record_exists(f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": depense_id})

def validate_depense_data(date_depense, categorie_depense, montant, motif):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    if not date_depense:
        return False, "La date est obligatoire."
    if not ensure_month_dates(date_depense):
        return False, "Le mois de la depense n'a pas pu etre cree dans dim_date."
    if not date_exists(date_depense):
        return False, "La date de depense n'existe pas dans dim_date."
    if not _txt(categorie_depense):
        return False, "La categorie depense est obligatoire."
    if len(_txt(categorie_depense)) > 50:
        return False, "La categorie ne doit pas depasser 50 caracteres."
    if _num(montant) < 0:
        return False, "Le montant ne peut pas etre negatif."
    if not _txt(motif):
        return False, "Le motif est obligatoire."
    return True, "OK"

def get_all_depenses():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return read_sql_dataframe(f"SELECT * FROM {TABLE_NAME} ORDER BY date_depense DESC,depense_id DESC")

def get_depense_by_id(depense_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return fetch_one(f"SELECT * FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": depense_id})

def search_depenses(keyword=None, categorie_depense=None, utilisateur=None):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"SELECT * FROM {TABLE_NAME} WHERE 1=1"
    params = {}
    if keyword:
        query += " AND (categorie_depense ILIKE :keyword OR motif ILIKE :keyword OR utilisateur ILIKE :keyword)"
        params["keyword"] = f"%{keyword}%"
    if categorie_depense:
        query += " AND categorie_depense = :categorie"
        params["categorie"] = categorie_depense
    if utilisateur:
        query += " AND utilisateur = :utilisateur"
        params["utilisateur"] = utilisateur
    query += " ORDER BY date_depense DESC,depense_id DESC"
    return read_sql_dataframe(query, params)

def get_depenses_by_date(start_date, end_date):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return read_sql_dataframe(f"SELECT * FROM {TABLE_NAME} WHERE date_depense BETWEEN :start AND :end ORDER BY date_depense DESC", {"start": start_date, "end": end_date})

def insert_depense(date_depense, categorie_depense, montant, motif, utilisateur="SYSTEM"):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    valid, message = validate_depense_data(date_depense, categorie_depense, montant, motif)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    INSERT INTO {TABLE_NAME} (date_depense,date_id,categorie_depense,montant,motif,utilisateur)
    VALUES (:date_depense,:date_id,:categorie,:montant,:motif,:utilisateur)
    """
    return execute_query(query, {"date_depense": date_depense, "date_id": date_depense, "categorie": _txt(categorie_depense), "montant": _num(montant), "motif": _txt(motif), "utilisateur": _txt(utilisateur) or "SYSTEM"})

def update_depense(depense_id, date_depense, categorie_depense, montant, motif, utilisateur="SYSTEM"):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    if not depense_exists(depense_id):
        return False
    valid, message = validate_depense_data(date_depense, categorie_depense, montant, motif)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    UPDATE {TABLE_NAME}
    SET date_depense = :date_depense,date_id = :date_id,categorie_depense = :categorie,montant = :montant,motif = :motif,utilisateur = :utilisateur
    WHERE {ID_COLUMN} = :id
    """
    return execute_query(query, {"id": depense_id, "date_depense": date_depense, "date_id": date_depense, "categorie": _txt(categorie_depense), "montant": _num(montant), "motif": _txt(motif), "utilisateur": _txt(utilisateur) or "SYSTEM"})

def delete_depense(depense_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    if not depense_exists(depense_id):
        return False
    return execute_query(f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": depense_id})

def count_depenses():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return int(get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME}") or 0)

def get_depenses_statistics():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"SELECT COUNT(*) AS total_depenses,COALESCE(SUM(montant),0) AS montant_total,COALESCE(AVG(montant),0) AS montant_moyen,COALESCE(MAX(montant),0) AS montant_max FROM {TABLE_NAME}"
    return fetch_one(query) or {}

def get_monthly_depenses():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT d.annee,d.mois,d.nom_mois,COUNT(dp.depense_id) AS total_depenses,COALESCE(SUM(dp.montant),0) AS montant_total
    FROM {TABLE_NAME} dp JOIN {DATE_TABLE} d ON d.date_id = dp.date_id
    GROUP BY d.annee,d.mois,d.nom_mois ORDER BY d.annee,d.mois
    """
    return read_sql_dataframe(query)

def get_depenses_by_category():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return read_sql_dataframe(f"SELECT categorie_depense,COUNT(*) AS total_depenses,COALESCE(SUM(montant),0) AS montant_total FROM {TABLE_NAME} GROUP BY categorie_depense ORDER BY montant_total DESC")

def get_depenses_kpis():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    stats = get_depenses_statistics()
    return {"total_depenses": int(stats.get("total_depenses", 0)), "montant_total": float(stats.get("montant_total", 0)), "montant_moyen": float(stats.get("montant_moyen", 0)), "montant_max": float(stats.get("montant_max", 0))}

__all__ = ["get_all_depenses","get_depense_by_id","search_depenses","get_depenses_by_date","insert_depense","update_depense","delete_depense","count_depenses","get_depenses_statistics","get_monthly_depenses","get_depenses_by_category","get_depenses_kpis"]

