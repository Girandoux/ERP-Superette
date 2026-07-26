# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : analytics_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

from __future__ import annotations
from typing import Any
import logging
import pandas as pd
from database.database_utils import read_sql_dataframe

logger=logging.getLogger("database")

# ============================================================
# TENDANCES
# ============================================================


# ============================================================
# 1. FONCTIONS DU MODULE
# ============================================================

def get_evolution_ventes(freq:str="month")->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql=f"""
    SELECT DATE_TRUNC('{freq}',date_vente)::date AS periode,COUNT(*) AS nombre_ventes,COALESCE(SUM(total_vente),0) AS chiffre_affaires,COALESCE(AVG(total_vente),0) AS panier_moyen
    FROM fact_ventes GROUP BY DATE_TRUNC('{freq}',date_vente) ORDER BY periode
    """
    return read_sql_dataframe(sql)

def get_evolution_achats(freq:str="month")->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql=f"""
    SELECT DATE_TRUNC('{freq}',date_achat)::date AS periode,COUNT(*) AS nombre_achats,COALESCE(SUM(total_facture),0) AS total_achats,COALESCE(AVG(total_facture),0) AS achat_moyen
    FROM fact_achats GROUP BY DATE_TRUNC('{freq}',date_achat) ORDER BY periode
    """
    return read_sql_dataframe(sql)

def get_evolution_depenses(freq:str="month")->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql=f"""
    SELECT DATE_TRUNC('{freq}',date_depense)::date AS periode,categorie_depense,COALESCE(SUM(montant),0) AS montant
    FROM fact_depenses GROUP BY DATE_TRUNC('{freq}',date_depense),categorie_depense ORDER BY periode,categorie_depense
    """
    return read_sql_dataframe(sql)

# ============================================================
# PERFORMANCE PRODUITS ET CATEGORIES
# ============================================================

def get_performance_produits(limit:int|None=None)->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie,p.stock_actuel,p.stock_min,
    COALESCE(v.quantite_vendue,0) AS quantite_vendue,COALESCE(v.chiffre_affaires,0) AS chiffre_affaires,COALESCE(v.cout_total,0) AS cout_total,COALESCE(v.marge,0) AS marge,
    COALESCE(a.quantite_achetee,0) AS quantite_achetee,COALESCE(a.total_achats,0) AS total_achats,
    COALESCE(pe.quantite_perdue,0) AS quantite_perdue,COALESCE(pe.valeur_perdue,0) AS valeur_perdue,
    CASE WHEN COALESCE(v.chiffre_affaires,0)>0 THEN ROUND((v.marge/v.chiffre_affaires)*100,2) ELSE 0 END AS taux_marge
    FROM dim_produits p
    LEFT JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT JOIN (SELECT produit_id,SUM(qte_vente) AS quantite_vendue,SUM(montant_ligne) AS chiffre_affaires,SUM(cout_total) AS cout_total,SUM(montant_ligne-cout_total) AS marge FROM dim_lignes_vente GROUP BY produit_id) v ON v.produit_id=p.produit_id
    LEFT JOIN (SELECT produit_id,SUM(quantite_achat) AS quantite_achetee,SUM(total_achat) AS total_achats FROM dim_lignes_achat GROUP BY produit_id) a ON a.produit_id=p.produit_id
    LEFT JOIN (SELECT produit_id,SUM(qte_perte) AS quantite_perdue,SUM(valeur_totale) AS valeur_perdue FROM dim_pertes GROUP BY produit_id) pe ON pe.produit_id=p.produit_id
    WHERE p.actif=TRUE ORDER BY chiffre_affaires DESC
    """
    if limit:
        sql+=" LIMIT :limit"
        return read_sql_dataframe(sql,{"limit":limit})
    return read_sql_dataframe(sql)

def get_performance_categories()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT c.categorie_id,c.code_categorie,c.nom_categorie,COUNT(DISTINCT p.produit_id) AS nombre_produits,
    COALESCE(SUM(v.quantite_vendue),0) AS quantite_vendue,COALESCE(SUM(v.chiffre_affaires),0) AS chiffre_affaires,COALESCE(SUM(v.marge),0) AS marge,
    COALESCE(SUM(p.stock_actuel),0) AS stock_total,
    CASE WHEN SUM(v.chiffre_affaires)>0 THEN ROUND((SUM(v.marge)/SUM(v.chiffre_affaires))*100,2) ELSE 0 END AS taux_marge
    FROM dim_categories c
    LEFT JOIN dim_produits p ON p.categorie_id=c.categorie_id AND p.actif=TRUE
    LEFT JOIN (SELECT produit_id,SUM(qte_vente) AS quantite_vendue,SUM(montant_ligne) AS chiffre_affaires,SUM(montant_ligne-cout_total) AS marge FROM dim_lignes_vente GROUP BY produit_id) v ON v.produit_id=p.produit_id
    GROUP BY c.categorie_id,c.code_categorie,c.nom_categorie ORDER BY chiffre_affaires DESC
    """
    return read_sql_dataframe(sql)

def get_rotation_stock()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT p.produit_id,p.code_produit,p.nom_produit,c.nom_categorie,p.stock_actuel,COALESCE(v.quantite_vendue,0) AS quantite_vendue,
    CASE WHEN COALESCE(p.stock_actuel,0)>0 THEN ROUND(v.quantite_vendue/NULLIF(p.stock_actuel,0),2) ELSE 0 END AS taux_rotation,
    CASE WHEN COALESCE(v.quantite_vendue,0)=0 THEN 'DORMANT' WHEN COALESCE(p.stock_actuel,0)<=p.stock_min THEN 'A_REAPPROVISIONNER' ELSE 'ACTIF' END AS statut_rotation
    FROM dim_produits p
    LEFT JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT JOIN (SELECT produit_id,SUM(qte_vente) AS quantite_vendue FROM dim_lignes_vente GROUP BY produit_id) v ON v.produit_id=p.produit_id
    WHERE p.actif=TRUE ORDER BY taux_rotation DESC,p.nom_produit
    """
    return read_sql_dataframe(sql)

# ============================================================
# ANALYSE FINANCIERE
# ============================================================

def get_analyse_marge(freq:str="month")->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql=f"""
    SELECT DATE_TRUNC('{freq}',v.date_vente)::date AS periode,COALESCE(SUM(lv.montant_ligne),0) AS chiffre_affaires,COALESCE(SUM(lv.cout_total),0) AS cout_total,COALESCE(SUM(lv.montant_ligne-lv.cout_total),0) AS marge,
    CASE WHEN SUM(lv.montant_ligne)>0 THEN ROUND((SUM(lv.montant_ligne-lv.cout_total)/SUM(lv.montant_ligne))*100,2) ELSE 0 END AS taux_marge
    FROM fact_ventes v JOIN dim_lignes_vente lv ON lv.vente_id=v.vente_id
    GROUP BY DATE_TRUNC('{freq}',v.date_vente) ORDER BY periode
    """
    return read_sql_dataframe(sql)

def get_analyse_resultat(freq:str="month")->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql=f"""
    WITH ventes AS (SELECT DATE_TRUNC('{freq}',date_vente)::date AS periode,SUM(total_vente) AS ca FROM fact_ventes GROUP BY DATE_TRUNC('{freq}',date_vente)),
    achats AS (SELECT DATE_TRUNC('{freq}',date_achat)::date AS periode,SUM(total_facture) AS achats FROM fact_achats GROUP BY DATE_TRUNC('{freq}',date_achat)),
    depenses AS (SELECT DATE_TRUNC('{freq}',date_depense)::date AS periode,SUM(montant) AS depenses FROM fact_depenses GROUP BY DATE_TRUNC('{freq}',date_depense)),
    pertes AS (SELECT DATE_TRUNC('{freq}',date_perte)::date AS periode,SUM(valeur_totale) AS pertes FROM dim_pertes GROUP BY DATE_TRUNC('{freq}',date_perte)),
    periodes AS (SELECT periode FROM ventes UNION SELECT periode FROM achats UNION SELECT periode FROM depenses UNION SELECT periode FROM pertes)
    SELECT p.periode,COALESCE(v.ca,0) AS chiffre_affaires,COALESCE(a.achats,0) AS achats,COALESCE(d.depenses,0) AS depenses,COALESCE(pe.pertes,0) AS pertes,COALESCE(v.ca,0)-COALESCE(a.achats,0)-COALESCE(d.depenses,0)-COALESCE(pe.pertes,0) AS resultat_net
    FROM periodes p LEFT JOIN ventes v ON v.periode=p.periode LEFT JOIN achats a ON a.periode=p.periode LEFT JOIN depenses d ON d.periode=p.periode LEFT JOIN pertes pe ON pe.periode=p.periode ORDER BY p.periode
    """
    return read_sql_dataframe(sql)

def get_analyse_tresorerie()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT date_mouvement,type_mouvement,montant,description,utilisateur,
    SUM(CASE WHEN type_mouvement IN ('ENTREE','APPORT','VENTE','DEPOT') THEN montant WHEN type_mouvement IN ('SORTIE','RETRAIT','DEPENSE','ACHAT') THEN -montant ELSE montant END) OVER(ORDER BY date_mouvement,mouvement_id) AS solde_cumule
    FROM fact_tresorerie ORDER BY date_mouvement,mouvement_id
    """
    return read_sql_dataframe(sql)

def get_analyse_pertes()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT pe.motif_perte,c.nom_categorie,p.nom_produit,COUNT(*) AS nombre_pertes,COALESCE(SUM(pe.qte_perte),0) AS quantite_perdue,COALESCE(SUM(pe.valeur_totale),0) AS valeur_perdue
    FROM dim_pertes pe
    LEFT JOIN dim_produits p ON p.produit_id=pe.produit_id
    LEFT JOIN dim_categories c ON c.categorie_id=p.categorie_id
    GROUP BY pe.motif_perte,c.nom_categorie,p.nom_produit ORDER BY valeur_perdue DESC
    """
    return read_sql_dataframe(sql)

def get_analyse_ecarts_inventaire()->pd.DataFrame:
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    sql="""
    SELECT p.code_produit,p.nom_produit,c.nom_categorie,COUNT(i.inventaire_id) AS nombre_controles,COALESCE(SUM(i.ecart),0) AS ecart_total,COALESCE(SUM(i.valeur_ecart),0) AS valeur_ecart_total,MAX(i.date_inventaire) AS dernier_inventaire
    FROM fact_inventaire i
    LEFT JOIN dim_produits p ON p.produit_id=i.produit_id
    LEFT JOIN dim_categories c ON c.categorie_id=p.categorie_id
    GROUP BY p.code_produit,p.nom_produit,c.nom_categorie ORDER BY ABS(COALESCE(SUM(i.valeur_ecart),0)) DESC
    """
    return read_sql_dataframe(sql)

# ============================================================
# POWER BI
# ============================================================

def get_powerbi_tables()->dict[str,pd.DataFrame]:
    """Retourne les tables principales pretes pour Power BI."""
    return {
        "dim_date":read_sql_dataframe("SELECT * FROM dim_date ORDER BY date_id"),
        "dim_categories":read_sql_dataframe("SELECT * FROM dim_categories ORDER BY categorie_id"),
        "dim_produits":read_sql_dataframe("SELECT * FROM dim_produits ORDER BY produit_id"),
        "dim_acheteurs":read_sql_dataframe("SELECT * FROM dim_acheteurs ORDER BY acheteur_id"),
        "dim_vendeurs":read_sql_dataframe("SELECT * FROM dim_vendeurs ORDER BY vendeur_id"),
        "fact_achats":read_sql_dataframe("SELECT * FROM fact_achats ORDER BY achat_id"),
        "dim_lignes_achat":read_sql_dataframe("SELECT * FROM dim_lignes_achat ORDER BY ligne_achat_id"),
        "fact_ventes":read_sql_dataframe("SELECT * FROM fact_ventes ORDER BY vente_id"),
        "dim_lignes_vente":read_sql_dataframe("SELECT * FROM dim_lignes_vente ORDER BY ligne_vente_id"),
        "fact_depenses":read_sql_dataframe("SELECT * FROM fact_depenses ORDER BY depense_id"),
        "dim_pertes":read_sql_dataframe("SELECT * FROM dim_pertes ORDER BY perte_id"),
        "fact_tresorerie":read_sql_dataframe("SELECT * FROM fact_tresorerie ORDER BY mouvement_id"),
        "fact_inventaire":read_sql_dataframe("SELECT * FROM fact_inventaire ORDER BY inventaire_id")
    }

def get_analytics_data()->dict[str,Any]:
    """Retourne les jeux de donnees analytiques pour la page Analyse."""
    return {
        "evolution_ventes":get_evolution_ventes(),
        "evolution_achats":get_evolution_achats(),
        "evolution_depenses":get_evolution_depenses(),
        "performance_produits":get_performance_produits(),
        "performance_categories":get_performance_categories(),
        "rotation_stock":get_rotation_stock(),
        "analyse_marge":get_analyse_marge(),
        "analyse_resultat":get_analyse_resultat(),
        "analyse_tresorerie":get_analyse_tresorerie(),
        "analyse_pertes":get_analyse_pertes(),
        "analyse_ecarts_inventaire":get_analyse_ecarts_inventaire()
    }

