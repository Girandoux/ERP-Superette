# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : pertes_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import pandas as pd
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists, get_scalar
from database.dates_db import date_exists,ensure_month_dates
from database.produits_db import product_exists
from database.stock_db import get_current_stock

logger = logging.getLogger("database")
TABLE_NAME = "dim_pertes"
PRODUITS_TABLE = "dim_produits"
DATE_TABLE = "dim_date"
ID_COLUMN = "perte_id"
MOTIFS = {"Perime","Casse","Vole","Don","Inventaire","Consommation_Interne"}


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

def _int(value):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    try:
        return int(value)
    except Exception:
        return 0

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

def perte_exists(perte_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return record_exists(f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": perte_id})

def validate_perte_data(date_perte, produit_id, qte_perte, motif_perte, valeur_unitaire, old_qte=0, old_produit_id=None):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    qte_perte = _int(qte_perte)
    motif_perte = _txt(motif_perte)
    if not date_perte:
        return False, "Date perte invalide."
    if not ensure_month_dates(date_perte):
        return False, "Le mois de la perte n'a pas pu etre cree dans dim_date."
    if not date_exists(date_perte):
        return False, "La date de perte n'existe pas dans dim_date."
    if not produit_id or not product_exists(produit_id):
        return False, "Produit invalide."
    if qte_perte <= 0:
        return False, "La quantite perdue doit etre superieure a 0."
    if motif_perte not in MOTIFS:
        return False, f"Motif invalide. Valeurs autorisees : {sorted(MOTIFS)}"
    if _num(valeur_unitaire) < 0:
        return False, "La valeur unitaire ne peut pas etre negative."
    stock = get_current_stock(produit_id)
    available = stock + old_qte if old_produit_id == produit_id else stock
    if available < qte_perte:
        return False, f"Stock insuffisant. Disponible : {available}."
    return True, "OK"

def get_all_pertes():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"""
    SELECT pe.*,p.code_produit,p.nom_produit
    FROM {TABLE_NAME} pe LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = pe.produit_id
    ORDER BY pe.date_perte DESC,pe.perte_id DESC
    """
    return read_sql_dataframe(query)

def get_perte_by_id(perte_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return fetch_one(f"SELECT * FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": perte_id})

def search_pertes(keyword=None, produit_id=None, motif_perte=None):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    query = f"SELECT pe.*,p.code_produit,p.nom_produit FROM {TABLE_NAME} pe LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = pe.produit_id WHERE 1=1"
    params = {}
    if keyword:
        query += " AND (p.code_produit ILIKE :keyword OR p.nom_produit ILIKE :keyword OR pe.utilisateur ILIKE :keyword)"
        params["keyword"] = f"%{keyword}%"
    if produit_id:
        query += " AND pe.produit_id = :produit_id"
        params["produit_id"] = produit_id
    if motif_perte:
        query += " AND pe.motif_perte = :motif"
        params["motif"] = motif_perte
    query += " ORDER BY pe.date_perte DESC,pe.perte_id DESC"
    return read_sql_dataframe(query, params)

def get_pertes_by_date(start_date, end_date):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return read_sql_dataframe(f"SELECT * FROM {TABLE_NAME} WHERE date_perte BETWEEN :start AND :end ORDER BY date_perte DESC", {"start": start_date, "end": end_date})

def insert_perte(date_perte, produit_id, qte_perte, motif_perte, valeur_unitaire, utilisateur="SYSTEM"):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    valid, message = validate_perte_data(date_perte, produit_id, qte_perte, motif_perte, valeur_unitaire)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    INSERT INTO {TABLE_NAME} (date_perte,date_id,produit_id,qte_perte,motif_perte,valeur_unitaire,valeur_totale,utilisateur)
    VALUES (:date_perte,:date_id,:produit_id,:qte_perte,:motif,:valeur_unitaire,0,:utilisateur)
    """
    return execute_query(query, {"date_perte": date_perte, "date_id": date_perte, "produit_id": produit_id, "qte_perte": _int(qte_perte), "motif": _txt(motif_perte), "valeur_unitaire": _num(valeur_unitaire), "utilisateur": _txt(utilisateur) or "SYSTEM"})

def update_perte(perte_id, date_perte, produit_id, qte_perte, motif_perte, valeur_unitaire, utilisateur="SYSTEM"):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    old = get_perte_by_id(perte_id)
    if not old:
        return False
    valid, message = validate_perte_data(date_perte, produit_id, qte_perte, motif_perte, valeur_unitaire, old_qte=int(old["qte_perte"]), old_produit_id=old["produit_id"])
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    UPDATE {TABLE_NAME}
    SET date_perte = :date_perte,date_id = :date_id,produit_id = :produit_id,qte_perte = :qte_perte,motif_perte = :motif,valeur_unitaire = :valeur_unitaire,utilisateur = :utilisateur
    WHERE {ID_COLUMN} = :id
    """
    return execute_query(query, {"id": perte_id, "date_perte": date_perte, "date_id": date_perte, "produit_id": produit_id, "qte_perte": _int(qte_perte), "motif": _txt(motif_perte), "valeur_unitaire": _num(valeur_unitaire), "utilisateur": _txt(utilisateur) or "SYSTEM"})

def delete_perte(perte_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    if not perte_exists(perte_id):
        return False
    return execute_query(f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": perte_id})

def get_pertes_statistics():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return fetch_one(f"SELECT COUNT(*) AS total_pertes,COALESCE(SUM(qte_perte),0) AS quantite_perdue,COALESCE(SUM(valeur_totale),0) AS valeur_perdue FROM {TABLE_NAME}") or {}

def get_pertes_by_motif():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return read_sql_dataframe(f"SELECT motif_perte,COUNT(*) AS total_pertes,COALESCE(SUM(qte_perte),0) AS quantite_perdue,COALESCE(SUM(valeur_totale),0) AS valeur_perdue FROM {TABLE_NAME} GROUP BY motif_perte ORDER BY valeur_perdue DESC")

def get_pertes_kpis():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    stats = get_pertes_statistics()
    return {"total_pertes": int(stats.get("total_pertes", 0)), "quantite_perdue": int(stats.get("quantite_perdue", 0)), "valeur_perdue": float(stats.get("valeur_perdue", 0))}

__all__ = ["get_all_pertes","get_perte_by_id","search_pertes","get_pertes_by_date","insert_perte","update_perte","delete_perte","get_pertes_statistics","get_pertes_by_motif","get_pertes_kpis"]

