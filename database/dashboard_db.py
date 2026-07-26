# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : dashboard_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

from __future__ import annotations
import logging
from typing import Any
import pandas as pd
from database.database_utils import fetch_one, read_sql_dataframe

logger=logging.getLogger("database")

# ============================================================
# KPIS GLOBAUX
# ============================================================


# ============================================================
# 1. FONCTIONS DU MODULE
# ============================================================

def get_global_kpis()->dict[str,Any]:
    """Retourne les indicateurs principaux du dashboard."""
    sql="""
    SELECT
    (SELECT COALESCE(SUM(total_vente),0) FROM fact_ventes) AS chiffre_affaires,
    (SELECT COALESCE(SUM(total_facture),0) FROM fact_achats) AS total_achats,
    (SELECT COALESCE(SUM(montant),0) FROM fact_depenses) AS total_depenses,
    (SELECT COALESCE(SUM(valeur_totale),0) FROM dim_pertes) AS total_pertes,
    (SELECT COALESCE(SUM(montant_ligne-COALESCE(cout_total,0)),0) FROM dim_lignes_vente) AS benefice_brut,
    (SELECT COUNT(*) FROM fact_ventes) AS nombre_ventes,
    (SELECT COUNT(*) FROM fact_achats) AS nombre_achats,
    (SELECT COUNT(*) FROM dim_produits WHERE actif=TRUE) AS produits_actifs,
    (SELECT COUNT(*) FROM dim_categories) AS categories,
    (SELECT COUNT(*) FROM dim_produits WHERE actif=TRUE AND COALESCE(stock_actuel,0)<=stock_min) AS alertes_stock,
    (SELECT COUNT(*) FROM dim_produits WHERE actif=TRUE AND COALESCE(stock_actuel,0)<=0) AS ruptures_stock,
    (SELECT COALESCE(SUM(COALESCE(p.stock_actuel,0)*COALESCE(cout.pu_achat_piece,0)),0)
    FROM dim_produits p LEFT JOIN (
    SELECT produit_id,MAX(pu_achat_piece) AS pu_achat_piece FROM dim_lignes_achat GROUP BY produit_id
    ) cout ON cout.produit_id=p.produit_id) AS valeur_stock,
    ((SELECT COALESCE(SUM(CASE WHEN type_mouvement IN ('Apport','Depot_Banque','Correction') THEN montant ELSE 0 END),0) FROM fact_tresorerie) + (SELECT COALESCE(SUM(total_vente),0) FROM fact_ventes) - (SELECT COALESCE(SUM(CASE WHEN type_mouvement IN ('Retrait','Retrait_Banque') THEN montant ELSE 0 END),0) FROM fact_tresorerie) - (SELECT COALESCE(SUM(total_facture),0) FROM fact_achats) - (SELECT COALESCE(SUM(montant),0) FROM fact_depenses)) AS solde_tresorerie
    """
    data=dict(fetch_one(sql) or {})
    data["benefice_net"]=float(data.get("benefice_brut",0))-float(data.get("total_depenses",0))-float(data.get("total_pertes",0))
    return data

def get_kpis_periode(date_debut:str|None=None,date_fin:str|None=None)->dict[str,Any]:
    """Retourne les KPIs entre deux dates."""
    params={}
    filtre_vente=filtre_achat=filtre_depense=filtre_perte=""
    if date_debut:
        params["date_debut"]=date_debut
        filtre_vente+=" AND date_vente>=:date_debut"
        filtre_achat+=" AND date_achat>=:date_debut"
        filtre_depense+=" AND date_depense>=:date_debut"
        filtre_perte+=" AND date_perte>=:date_debut"
    if date_fin:
        params["date_fin"]=date_fin
        filtre_vente+=" AND date_vente<=:date_fin"
        filtre_achat+=" AND date_achat<=:date_fin"
        filtre_depense+=" AND date_depense<=:date_fin"
        filtre_perte+=" AND date_perte<=:date_fin"
    sql=f"""
    SELECT
    (SELECT COALESCE(SUM(total_vente),0) FROM fact_ventes WHERE 1=1 {filtre_vente}) AS chiffre_affaires,
    (SELECT COALESCE(SUM(total_facture),0) FROM fact_achats WHERE 1=1 {filtre_achat}) AS total_achats,
    (SELECT COALESCE(SUM(montant),0) FROM fact_depenses WHERE 1=1 {filtre_depense}) AS total_depenses,
    (SELECT COALESCE(SUM(valeur_totale),0) FROM dim_pertes WHERE 1=1 {filtre_perte}) AS total_pertes,
    (SELECT COUNT(*) FROM fact_ventes WHERE 1=1 {filtre_vente}) AS nombre_ventes,
    (SELECT COUNT(*) FROM fact_achats WHERE 1=1 {filtre_achat}) AS nombre_achats
    """
    data=dict(fetch_one(sql,params) or {})
    data["benefice_net"]=float(data.get("chiffre_affaires",0))-float(data.get("total_achats",0))-float(data.get("total_depenses",0))-float(data.get("total_pertes",0))
    return data

# ============================================================
# GRAPHIQUES DASHBOARD
# ============================================================

def get_ventes_mensuelles()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT DATE_TRUNC('month',date_vente)::date AS mois,COUNT(*) AS nombre_ventes,COALESCE(SUM(total_vente),0) AS chiffre_affaires
    FROM fact_ventes GROUP BY DATE_TRUNC('month',date_vente) ORDER BY mois
    """
    return read_sql_dataframe(sql)

def get_achats_mensuels()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT DATE_TRUNC('month',date_achat)::date AS mois,COUNT(*) AS nombre_achats,COALESCE(SUM(total_facture),0) AS total_achats
    FROM fact_achats GROUP BY DATE_TRUNC('month',date_achat) ORDER BY mois
    """
    return read_sql_dataframe(sql)

def get_depenses_mensuelles()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT DATE_TRUNC('month',date_depense)::date AS mois,categorie_depense,COALESCE(SUM(montant),0) AS total_depenses
    FROM fact_depenses GROUP BY DATE_TRUNC('month',date_depense),categorie_depense ORDER BY mois,categorie_depense
    """
    return read_sql_dataframe(sql)

def get_pertes_mensuelles()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT DATE_TRUNC('month',date_perte)::date AS mois,motif_perte,COALESCE(SUM(qte_perte),0) AS quantite_perdue,COALESCE(SUM(valeur_totale),0) AS valeur_perdue
    FROM dim_pertes GROUP BY DATE_TRUNC('month',date_perte),motif_perte ORDER BY mois,motif_perte
    """
    return read_sql_dataframe(sql)

def get_top_produits_vendus(limit:int=10)->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie,COALESCE(SUM(lv.qte_vente),0) AS quantite_vendue,COALESCE(SUM(lv.montant_ligne),0) AS chiffre_affaires
    FROM dim_lignes_vente lv
    JOIN dim_produits p ON p.produit_id=lv.produit_id
    LEFT JOIN dim_categories c ON c.categorie_id=p.categorie_id
    GROUP BY p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie
    ORDER BY chiffre_affaires DESC LIMIT :limit
    """
    return read_sql_dataframe(sql,{"limit":limit})

def get_top_produits_achetes(limit:int=10)->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie,COALESCE(SUM(la.quantite_achat),0) AS quantite_achetee,COALESCE(SUM(la.total_achat),0) AS total_achats
    FROM dim_lignes_achat la
    JOIN dim_produits p ON p.produit_id=la.produit_id
    LEFT JOIN dim_categories c ON c.categorie_id=p.categorie_id
    GROUP BY p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie
    ORDER BY total_achats DESC LIMIT :limit
    """
    return read_sql_dataframe(sql,{"limit":limit})

def get_alertes_stock()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie,p.stock_actuel,p.stock_min,p.unite,
    CASE WHEN COALESCE(p.stock_actuel,0)<=0 THEN 'RUPTURE' ELSE 'ALERTE' END AS statut_stock
    FROM dim_produits p LEFT JOIN dim_categories c ON c.categorie_id=p.categorie_id
    WHERE p.actif=TRUE AND COALESCE(p.stock_actuel,0)<=p.stock_min ORDER BY p.stock_actuel ASC,p.nom_produit
    """
    return read_sql_dataframe(sql)

def get_repartition_stock_par_categorie()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT c.nom_categorie,COUNT(p.produit_id) AS nombre_produits,COALESCE(SUM(p.stock_actuel),0) AS stock_total
    FROM dim_categories c LEFT JOIN dim_produits p ON p.categorie_id=c.categorie_id AND p.actif=TRUE
    GROUP BY c.nom_categorie ORDER BY stock_total DESC
    """
    return read_sql_dataframe(sql)

def get_flux_tresorerie()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT date_mouvement,type_mouvement,description,montant,utilisateur
    FROM fact_tresorerie ORDER BY date_mouvement DESC,mouvement_id DESC LIMIT 50
    """
    return read_sql_dataframe(sql)

def get_dashboard_data()->dict[str,Any]:
    """Retourne toutes les donnees utiles pour la page Dashboard."""
    return {
        "kpis":get_global_kpis(),
        "ventes_mensuelles":get_ventes_mensuelles(),
        "achats_mensuels":get_achats_mensuels(),
        "depenses_mensuelles":get_depenses_mensuelles(),
        "pertes_mensuelles":get_pertes_mensuelles(),
        "top_produits_vendus":get_top_produits_vendus(),
        "top_produits_achetes":get_top_produits_achetes(),
        "alertes_stock":get_alertes_stock(),
        "stock_par_categorie":get_repartition_stock_par_categorie(),
        "flux_tresorerie":get_flux_tresorerie()
    }

