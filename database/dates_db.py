# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : dates_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

from __future__ import annotations
from calendar import monthrange
from datetime import date,timedelta
from database.database_utils import execute_query,record_exists

DATE_TABLE="dim_date"
MOIS_NOMS={1:"Janvier",2:"Fevrier",3:"Mars",4:"Avril",5:"Mai",6:"Juin",7:"Juillet",8:"Aout",9:"Septembre",10:"Octobre",11:"Novembre",12:"Decembre"}


# ============================================================
# 1. FONCTIONS DU MODULE
# ============================================================

def date_exists(date_id:date)->bool:
    """Verifie si une date existe dans dim_date."""
    return record_exists(f"SELECT 1 FROM {DATE_TABLE} WHERE date_id=:date_id",{"date_id":date_id})

def build_date_row(date_id:date)->dict:
    """Prepare les valeurs d'une ligne dim_date."""
    return {"date_id":date_id,"jour":date_id.day,"mois":date_id.month,"annee":date_id.year,"trimestre":f"T{((date_id.month-1)//3)+1}","nom_mois":MOIS_NOMS.get(date_id.month,"")}

def ensure_date_exists(date_id:date)->bool:
    """Cree ou harmonise une date dans dim_date."""
    query=f"""
    INSERT INTO {DATE_TABLE} (date_id,jour,mois,annee,trimestre,nom_mois)
    VALUES (:date_id,:jour,:mois,:annee,:trimestre,:nom_mois)
    ON CONFLICT (date_id) DO UPDATE SET
    jour=EXCLUDED.jour,mois=EXCLUDED.mois,annee=EXCLUDED.annee,trimestre=EXCLUDED.trimestre,nom_mois=EXCLUDED.nom_mois
    """
    return execute_query(query,build_date_row(date_id))

def ensure_month_dates(date_id:date)->bool:
    """Cree toutes les dates du mois de date_id dans dim_date."""
    if not date_id:
        return False
    first_day=date(date_id.year,date_id.month,1)
    last_day=date(date_id.year,date_id.month,monthrange(date_id.year,date_id.month)[1])
    current=first_day
    success=True
    while current<=last_day:
        success=ensure_date_exists(current) and success
        current+=timedelta(days=1)
    return success

