# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : tresorerie_db.py
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
TABLE_NAME = "fact_tresorerie"
DATE_TABLE = "dim_date"
ID_COLUMN = "mouvement_id"
TYPES = {"Apport","Retrait","Depot_Banque","Retrait_Banque","Correction"}


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

def mouvement_exists(mouvement_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return record_exists(f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": mouvement_id})

def validate_mouvement_data(date_mouvement, type_mouvement, montant):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    type_mouvement = _txt(type_mouvement)
    if not date_mouvement:
        return False, "Date mouvement invalide."
    if not ensure_month_dates(date_mouvement):
        return False, "Le mois du mouvement n'a pas pu etre cree dans dim_date."
    if not date_exists(date_mouvement):
        return False, "La date du mouvement n'existe pas dans dim_date."
    if type_mouvement not in TYPES:
        return False, f"Type invalide. Valeurs autorisees : {sorted(TYPES)}"
    if _num(montant) <= 0:
        return False, "Le montant doit etre superieur a 0."
    return True, "OK"

def get_all_mouvements():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return read_sql_dataframe(f"SELECT * FROM {TABLE_NAME} ORDER BY date_mouvement DESC,mouvement_id DESC")

def get_mouvement_by_id(mouvement_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return fetch_one(f"SELECT * FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": mouvement_id})

def search_mouvements(keyword=None, type_mouvement=None, utilisateur=None):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"SELECT * FROM {TABLE_NAME} WHERE 1=1"
    params = {}
    if keyword:
        query += " AND (description ILIKE :keyword OR utilisateur ILIKE :keyword OR type_mouvement ILIKE :keyword)"
        params["keyword"] = f"%{keyword}%"
    if type_mouvement:
        query += " AND type_mouvement = :type"
        params["type"] = type_mouvement
    if utilisateur:
        query += " AND utilisateur = :utilisateur"
        params["utilisateur"] = utilisateur
    query += " ORDER BY date_mouvement DESC,mouvement_id DESC"
    return read_sql_dataframe(query, params)

def get_mouvements_by_date(start_date, end_date):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return read_sql_dataframe(f"SELECT * FROM {TABLE_NAME} WHERE date_mouvement BETWEEN :start AND :end ORDER BY date_mouvement DESC", {"start": start_date, "end": end_date})

def insert_mouvement(date_mouvement, type_mouvement, montant, description=None, utilisateur="SYSTEM"):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    valid, message = validate_mouvement_data(date_mouvement, type_mouvement, montant)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    INSERT INTO {TABLE_NAME} (date_mouvement,date_id,type_mouvement,montant,description,utilisateur)
    VALUES (:date_mouvement,:date_id,:type_mouvement,:montant,:description,:utilisateur)
    """
    return execute_query(query, {"date_mouvement": date_mouvement, "date_id": date_mouvement, "type_mouvement": _txt(type_mouvement), "montant": _num(montant), "description": _txt(description) or None, "utilisateur": _txt(utilisateur) or "SYSTEM"})

def update_mouvement(mouvement_id, date_mouvement, type_mouvement, montant, description=None, utilisateur="SYSTEM"):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    if not mouvement_exists(mouvement_id):
        return False
    valid, message = validate_mouvement_data(date_mouvement, type_mouvement, montant)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    UPDATE {TABLE_NAME}
    SET date_mouvement = :date_mouvement,date_id = :date_id,type_mouvement = :type_mouvement,montant = :montant,description = :description,utilisateur = :utilisateur
    WHERE {ID_COLUMN} = :id
    """
    return execute_query(query, {"id": mouvement_id, "date_mouvement": date_mouvement, "date_id": date_mouvement, "type_mouvement": _txt(type_mouvement), "montant": _num(montant), "description": _txt(description) or None, "utilisateur": _txt(utilisateur) or "SYSTEM"})

def delete_mouvement(mouvement_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    if not mouvement_exists(mouvement_id):
        return False
    return execute_query(f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": mouvement_id})

def get_solde_tresorerie():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT COALESCE(SUM(CASE
        WHEN type_mouvement IN ('Apport','Depot_Banque','Correction') THEN montant
        WHEN type_mouvement IN ('Retrait','Retrait_Banque') THEN -montant
        ELSE 0 END),0) AS solde
    FROM {TABLE_NAME}
    """
    result = fetch_one(query)
    return float(result["solde"]) if result else 0.0

def get_solde_reel_caisse():
    """Calcule la caisse reelle : apports + ventes - retraits - achats - depenses."""
    query = """
    SELECT
    (SELECT COALESCE(SUM(CASE WHEN type_mouvement IN ('Apport','Depot_Banque','Correction') THEN montant ELSE 0 END),0) FROM fact_tresorerie) AS apports,
    (SELECT COALESCE(SUM(CASE WHEN type_mouvement IN ('Retrait','Retrait_Banque') THEN montant ELSE 0 END),0) FROM fact_tresorerie) AS retraits,
    (SELECT COALESCE(SUM(total_vente),0) FROM fact_ventes) AS ventes,
    (SELECT COALESCE(SUM(total_facture),0) FROM fact_achats) AS achats,
    (SELECT COALESCE(SUM(montant),0) FROM fact_depenses) AS depenses
    """
    data = fetch_one(query) or {}
    apports = float(data.get("apports", 0) or 0)
    retraits = float(data.get("retraits", 0) or 0)
    ventes = float(data.get("ventes", 0) or 0)
    achats = float(data.get("achats", 0) or 0)
    depenses = float(data.get("depenses", 0) or 0)
    entrees_reelles = apports + ventes
    sorties_reelles = retraits + achats + depenses
    solde_reel = entrees_reelles - sorties_reelles
    return {"apports": apports, "retraits": retraits, "ventes": ventes, "achats": achats, "depenses": depenses, "entrees_reelles": entrees_reelles, "sorties_reelles": sorties_reelles, "solde_reel_caisse": solde_reel}

def get_tresorerie_statistics():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT COUNT(*) AS total_mouvements,
    COALESCE(SUM(CASE WHEN type_mouvement IN ('Apport','Depot_Banque','Correction') THEN montant ELSE 0 END),0) AS entrees,
    COALESCE(SUM(CASE WHEN type_mouvement IN ('Retrait','Retrait_Banque') THEN montant ELSE 0 END),0) AS sorties
    FROM {TABLE_NAME}
    """
    return fetch_one(query) or {}

def get_mouvements_by_type():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return read_sql_dataframe(f"SELECT type_mouvement,COUNT(*) AS total_mouvements,COALESCE(SUM(montant),0) AS montant_total FROM {TABLE_NAME} GROUP BY type_mouvement ORDER BY montant_total DESC")

def get_monthly_tresorerie():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT d.annee,d.mois,d.nom_mois,
    COALESCE(SUM(CASE WHEN t.type_mouvement IN ('Apport','Depot_Banque','Correction') THEN t.montant ELSE 0 END),0) AS entrees,
    COALESCE(SUM(CASE WHEN t.type_mouvement IN ('Retrait','Retrait_Banque') THEN t.montant ELSE 0 END),0) AS sorties
    FROM {TABLE_NAME} t JOIN {DATE_TABLE} d ON d.date_id = t.date_id
    GROUP BY d.annee,d.mois,d.nom_mois ORDER BY d.annee,d.mois
    """
    return read_sql_dataframe(query)

def get_tresorerie_kpis():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    stats = get_tresorerie_statistics()
    reel = get_solde_reel_caisse()
    return {
        "total_mouvements": int(stats.get("total_mouvements", 0)),
        "entrees": float(stats.get("entrees", 0)),
        "sorties": float(stats.get("sorties", 0)),
        "solde": get_solde_tresorerie(),
        "apports": reel["apports"],
        "retraits": reel["retraits"],
        "ventes": reel["ventes"],
        "achats": reel["achats"],
        "depenses": reel["depenses"],
        "entrees_reelles": reel["entrees_reelles"],
        "sorties_reelles": reel["sorties_reelles"],
        "solde_reel_caisse": reel["solde_reel_caisse"]
    }

__all__ = ["get_all_mouvements","get_mouvement_by_id","search_mouvements","get_mouvements_by_date","insert_mouvement","update_mouvement","delete_mouvement","get_solde_tresorerie","get_solde_reel_caisse","get_tresorerie_statistics","get_mouvements_by_type","get_monthly_tresorerie","get_tresorerie_kpis"]

