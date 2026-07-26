# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : database/rapports_db.py
# ROLE : Rapports SQL pour export et consultation
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from database.database_utils import read_sql_dataframe


# ============================================================
# 1. CONFIGURATION DU MODULE
# ============================================================

logger = logging.getLogger("database")


# ============================================================
# 2. OUTILS INTERNES
# ============================================================

def _date_filter(
    column: str,
    date_debut: str | None,
    date_fin: str | None,
) -> tuple[str, dict[str, Any]]:
    """Construit un filtre SQL optionnel sur une plage de dates.

    Entrée :
        column : nom de la colonne SQL utilisée pour le filtrage.
        date_debut : date minimale incluse ou ``None``.
        date_fin : date maximale incluse ou ``None``.

    Traitement :
        Construit les clauses SQL et le dictionnaire de paramètres associés.

    Validation :
        Seules les dates effectivement renseignées sont ajoutées au filtre.

    Retour :
        Tuple contenant la clause ``WHERE`` et les paramètres SQL.
    """
    params: dict[str, Any] = {}
    clauses: list[str] = []

    if date_debut:
        clauses.append(f"{column} >= :date_debut")
        params["date_debut"] = date_debut

    if date_fin:
        clauses.append(f"{column} <= :date_fin")
        params["date_fin"] = date_fin

    filter_clause = (
        " WHERE " + " AND ".join(clauses)
        if clauses
        else ""
    )

    return filter_clause, params


# ============================================================
# 3. RAPPORTS PRINCIPAUX
# ============================================================

def get_rapport_ventes(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> pd.DataFrame:
    """Retourne le rapport détaillé des ventes.

    Entrée :
        date_debut : date minimale facultative.
        date_fin : date maximale facultative.

    Traitement :
        Joint les ventes, vendeurs, lignes de vente, produits et catégories.

    Validation :
        Le filtrage par date est appliqué uniquement lorsque nécessaire.

    Retour :
        DataFrame contenant le détail des ventes.
    """
    filtre, params = _date_filter(
        "v.date_vente",
        date_debut,
        date_fin,
    )

    sql = f"""
        SELECT
            v.vente_id,
            v.date_vente,
            v.date_id,
            ve.nom_vendeur,
            p.code_produit,
            p.nom_produit,
            c.nom_categorie,
            lv.qte_vente,
            lv.pu_vente,
            lv.montant_ligne,
            lv.cout_unitaire,
            lv.cout_total,
            (
                lv.montant_ligne
                - COALESCE(lv.cout_total, 0)
            ) AS marge_ligne,
            v.total_vente
        FROM fact_ventes v
        LEFT JOIN dim_vendeurs ve
            ON ve.vendeur_id = v.vendeur_id
        LEFT JOIN dim_lignes_vente lv
            ON lv.vente_id = v.vente_id
        LEFT JOIN dim_produits p
            ON p.produit_id = lv.produit_id
        LEFT JOIN dim_categories c
            ON c.categorie_id = p.categorie_id
        {filtre}
        ORDER BY
            v.date_vente DESC,
            v.vente_id DESC,
            lv.ligne_vente_id
    """

    return read_sql_dataframe(sql, params)


def get_rapport_achats(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> pd.DataFrame:
    """Retourne le rapport détaillé des achats.

    Entrée :
        date_debut : date minimale facultative.
        date_fin : date maximale facultative.

    Traitement :
        Joint les achats, acheteurs, lignes d'achat, produits et catégories.

    Validation :
        Le filtrage par date est appliqué uniquement lorsque nécessaire.

    Retour :
        DataFrame contenant le détail des achats.
    """
    filtre, params = _date_filter(
        "a.date_achat",
        date_debut,
        date_fin,
    )

    sql = f"""
        SELECT
            a.achat_id,
            a.date_achat,
            a.date_id,
            a.numero_facture,
            ac.nom_acheteur,
            p.code_produit,
            p.nom_produit,
            c.nom_categorie,
            la.qte_cartons,
            la.qte_par_carton,
            la.quantite_achat,
            la.pu_achat_carton,
            la.pu_achat_piece,
            la.total_achat,
            la.date_fabrication,
            la.date_peremption,
            a.frais_enlevement,
            a.total_facture
        FROM fact_achats a
        LEFT JOIN dim_acheteurs ac
            ON ac.acheteur_id = a.acheteur_id
        LEFT JOIN dim_lignes_achat la
            ON la.achat_id = a.achat_id
        LEFT JOIN dim_produits p
            ON p.produit_id = la.produit_id
        LEFT JOIN dim_categories c
            ON c.categorie_id = p.categorie_id
        {filtre}
        ORDER BY
            a.date_achat DESC,
            a.achat_id DESC,
            la.ligne_achat_id
    """

    return read_sql_dataframe(sql, params)


def get_rapport_stock() -> pd.DataFrame:
    """Retourne l'état détaillé du stock.

    Entrée :
        Aucune.

    Traitement :
        Calcule la valeur du stock, récupère le dernier coût d'achat
        et détermine le statut de chaque produit.

    Validation :
        Les valeurs nulles de stock et de coût sont remplacées par zéro.

    Retour :
        DataFrame contenant l'état du stock.
    """
    sql = """
        SELECT
            p.produit_id,
            p.code_produit,
            p.nom_produit,
            c.nom_categorie,
            p.unite,
            p.qte_par_carton,
            p.stock_min,
            p.stock_actuel,
            COALESCE(cout.pu_achat_piece, 0) AS dernier_cout_achat,
            (
                COALESCE(p.stock_actuel, 0)
                * COALESCE(cout.pu_achat_piece, 0)
            ) AS valeur_stock,
            CASE
                WHEN COALESCE(p.stock_actuel, 0) <= 0
                    THEN 'RUPTURE'
                WHEN COALESCE(p.stock_actuel, 0) <= p.stock_min
                    THEN 'ALERTE'
                ELSE 'NORMAL'
            END AS statut_stock,
            p.actif,
            p.date_creation
        FROM dim_produits p
        LEFT JOIN dim_categories c
            ON c.categorie_id = p.categorie_id
        LEFT JOIN (
            SELECT
                produit_id,
                MAX(pu_achat_piece) AS pu_achat_piece
            FROM dim_lignes_achat
            GROUP BY produit_id
        ) cout
            ON cout.produit_id = p.produit_id
        ORDER BY
            c.nom_categorie,
            p.nom_produit
    """

    return read_sql_dataframe(sql)


def get_rapport_depenses(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> pd.DataFrame:
    """Retourne le rapport des dépenses.

    Entrée :
        date_debut : date minimale facultative.
        date_fin : date maximale facultative.

    Traitement :
        Sélectionne les dépenses selon la plage de dates demandée.

    Validation :
        Le filtre SQL est construit uniquement avec les dates renseignées.

    Retour :
        DataFrame contenant les dépenses.
    """
    filtre, params = _date_filter(
        "date_depense",
        date_debut,
        date_fin,
    )

    sql = f"""
        SELECT
            depense_id,
            date_depense,
            date_id,
            categorie_depense,
            montant,
            motif,
            utilisateur
        FROM fact_depenses
        {filtre}
        ORDER BY
            date_depense DESC,
            depense_id DESC
    """

    return read_sql_dataframe(sql, params)


def get_rapport_pertes(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> pd.DataFrame:
    """Retourne le rapport détaillé des pertes.

    Entrée :
        date_debut : date minimale facultative.
        date_fin : date maximale facultative.

    Traitement :
        Joint les pertes, produits et catégories.

    Validation :
        Le filtre SQL est construit uniquement avec les dates renseignées.

    Retour :
        DataFrame contenant le détail des pertes.
    """
    filtre, params = _date_filter(
        "pe.date_perte",
        date_debut,
        date_fin,
    )

    sql = f"""
        SELECT
            pe.perte_id,
            pe.date_perte,
            pe.date_id,
            p.code_produit,
            p.nom_produit,
            c.nom_categorie,
            pe.qte_perte,
            pe.motif_perte,
            pe.valeur_unitaire,
            pe.valeur_totale,
            pe.utilisateur
        FROM dim_pertes pe
        LEFT JOIN dim_produits p
            ON p.produit_id = pe.produit_id
        LEFT JOIN dim_categories c
            ON c.categorie_id = p.categorie_id
        {filtre}
        ORDER BY
            pe.date_perte DESC,
            pe.perte_id DESC
    """

    return read_sql_dataframe(sql, params)


def get_rapport_inventaire(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> pd.DataFrame:
    """Retourne le rapport détaillé des inventaires.

    Entrée :
        date_debut : date minimale facultative.
        date_fin : date maximale facultative.

    Traitement :
        Joint les inventaires, produits et catégories.

    Validation :
        Le filtre SQL est construit uniquement avec les dates renseignées.

    Retour :
        DataFrame contenant le détail des inventaires.
    """
    filtre, params = _date_filter(
        "i.date_inventaire",
        date_debut,
        date_fin,
    )

    sql = f"""
        SELECT
            i.inventaire_id,
            i.date_inventaire,
            i.date_id,
            p.code_produit,
            p.nom_produit,
            c.nom_categorie,
            i.stock_theorique,
            i.stock_physique,
            i.ecart,
            i.valeur_ecart,
            i.commentaire,
            i.utilisateur
        FROM fact_inventaire i
        LEFT JOIN dim_produits p
            ON p.produit_id = i.produit_id
        LEFT JOIN dim_categories c
            ON c.categorie_id = p.categorie_id
        {filtre}
        ORDER BY
            i.date_inventaire DESC,
            i.inventaire_id DESC
    """

    return read_sql_dataframe(sql, params)


def get_rapport_tresorerie(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> pd.DataFrame:
    """Retourne le rapport des mouvements de trésorerie.

    Entrée :
        date_debut : date minimale facultative.
        date_fin : date maximale facultative.

    Traitement :
        Sélectionne les mouvements selon la plage de dates demandée.

    Validation :
        Le filtre SQL est construit uniquement avec les dates renseignées.

    Retour :
        DataFrame contenant les mouvements de trésorerie.
    """
    filtre, params = _date_filter(
        "date_mouvement",
        date_debut,
        date_fin,
    )

    sql = f"""
        SELECT
            mouvement_id,
            date_mouvement,
            date_id,
            type_mouvement,
            montant,
            description,
            utilisateur
        FROM fact_tresorerie
        {filtre}
        ORDER BY
            date_mouvement DESC,
            mouvement_id DESC
    """

    return read_sql_dataframe(sql, params)


def get_rapport_profitabilite(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> pd.DataFrame:
    """Retourne le rapport de profitabilité par produit.

    Entrée :
        date_debut : date minimale facultative.
        date_fin : date maximale facultative.

    Traitement :
        Agrège les quantités vendues, le chiffre d'affaires, les coûts
        et la marge par produit.

    Validation :
        Le taux de marge est calculé uniquement lorsque le chiffre
        d'affaires est supérieur à zéro.

    Retour :
        DataFrame contenant la profitabilité par produit.
    """
    filtre, params = _date_filter(
        "v.date_vente",
        date_debut,
        date_fin,
    )

    sql = f"""
        SELECT
            p.produit_id,
            p.code_produit,
            p.nom_produit,
            c.nom_categorie,
            COALESCE(SUM(lv.qte_vente), 0) AS quantite_vendue,
            COALESCE(SUM(lv.montant_ligne), 0) AS chiffre_affaires,
            COALESCE(SUM(lv.cout_total), 0) AS cout_total,
            COALESCE(
                SUM(lv.montant_ligne - lv.cout_total),
                0
            ) AS marge,
            CASE
                WHEN SUM(lv.montant_ligne) > 0
                    THEN ROUND(
                        (
                            SUM(lv.montant_ligne - lv.cout_total)
                            / SUM(lv.montant_ligne)
                        ) * 100,
                        2
                    )
                ELSE 0
            END AS taux_marge
        FROM dim_lignes_vente lv
        JOIN fact_ventes v
            ON v.vente_id = lv.vente_id
        JOIN dim_produits p
            ON p.produit_id = lv.produit_id
        LEFT JOIN dim_categories c
            ON c.categorie_id = p.categorie_id
        {filtre}
        GROUP BY
            p.produit_id,
            p.code_produit,
            p.nom_produit,
            c.nom_categorie
        ORDER BY marge DESC
    """

    return read_sql_dataframe(sql, params)


def get_rapport_controle_prix(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> pd.DataFrame:
    """Compare le dernier coût d'achat unitaire au dernier prix de vente.

    Entrée :
        date_debut : date minimale facultative pour les ventes.
        date_fin : date maximale facultative pour les ventes.

    Traitement :
        Recherche le dernier achat et la dernière vente de chaque produit,
        puis calcule la marge et le statut de rentabilité.

    Validation :
        Les valeurs nulles sont remplacées par des valeurs de repli
        adaptées aux calculs.

    Retour :
        DataFrame contenant le contrôle des prix par produit.
    """
    vente_filter = ""
    params: dict[str, Any] = {}

    if date_debut:
        vente_filter += " AND v.date_vente >= :date_debut"
        params["date_debut"] = date_debut

    if date_fin:
        vente_filter += " AND v.date_vente <= :date_fin"
        params["date_fin"] = date_fin

    sql = f"""
        WITH dernier_achat AS (
            SELECT DISTINCT ON (la.produit_id)
                la.produit_id,
                a.date_achat,
                la.pu_achat_piece,
                la.pu_achat_carton,
                la.qte_par_carton
            FROM dim_lignes_achat la
            JOIN fact_achats a
                ON a.achat_id = la.achat_id
            ORDER BY
                la.produit_id,
                a.date_achat DESC,
                la.ligne_achat_id DESC
        ),
        derniere_vente AS (
            SELECT DISTINCT ON (lv.produit_id)
                lv.produit_id,
                v.date_vente,
                lv.pu_vente,
                lv.cout_unitaire
            FROM dim_lignes_vente lv
            JOIN fact_ventes v
                ON v.vente_id = lv.vente_id
            WHERE 1 = 1
                {vente_filter}
            ORDER BY
                lv.produit_id,
                v.date_vente DESC,
                lv.ligne_vente_id DESC
        )
        SELECT
            p.produit_id,
            p.code_produit,
            p.nom_produit,
            COALESCE(
                c.nom_categorie,
                'Non classe'
            ) AS nom_categorie,
            COALESCE(p.stock_actuel, 0) AS stock_actuel,
            da.date_achat AS date_dernier_achat,
            COALESCE(
                da.pu_achat_piece,
                0
            ) AS prix_achat_unitaire_dernier,
            COALESCE(
                da.pu_achat_carton,
                0
            ) AS prix_achat_carton_dernier,
            COALESCE(
                da.qte_par_carton,
                p.qte_par_carton,
                1
            ) AS qte_par_carton,
            dv.date_vente AS date_derniere_vente,
            COALESCE(dv.pu_vente, 0) AS prix_vente_dernier,
            ROUND(
                COALESCE(dv.pu_vente, 0)
                - COALESCE(
                    da.pu_achat_piece,
                    dv.cout_unitaire,
                    0
                ),
                2
            ) AS marge_unitaire_estimee,
            CASE
                WHEN COALESCE(dv.pu_vente, 0) > 0
                    THEN ROUND(
                        (
                            (
                                COALESCE(dv.pu_vente, 0)
                                - COALESCE(
                                    da.pu_achat_piece,
                                    dv.cout_unitaire,
                                    0
                                )
                            )
                            / COALESCE(dv.pu_vente, 0)
                        ) * 100,
                        2
                    )
                ELSE 0
            END AS taux_marge_estime,
            CASE
                WHEN dv.produit_id IS NULL
                    THEN 'SANS VENTE'
                WHEN da.produit_id IS NULL
                    THEN 'SANS ACHAT'
                WHEN COALESCE(dv.pu_vente, 0)
                    < COALESCE(da.pu_achat_piece, 0)
                    THEN 'NON RENTABLE'
                WHEN COALESCE(dv.pu_vente, 0)
                    = COALESCE(da.pu_achat_piece, 0)
                    THEN 'A REVOIR'
                ELSE 'RENTABLE'
            END AS statut_prix
        FROM dim_produits p
        LEFT JOIN dim_categories c
            ON c.categorie_id = p.categorie_id
        LEFT JOIN dernier_achat da
            ON da.produit_id = p.produit_id
        LEFT JOIN derniere_vente dv
            ON dv.produit_id = p.produit_id
        WHERE COALESCE(p.actif, TRUE) = TRUE
        ORDER BY
            statut_prix,
            p.nom_produit
    """

    return read_sql_dataframe(sql, params)


# ============================================================
# 4. EXPORTS
# ============================================================

def export_rapport_csv(
    dataframe: pd.DataFrame,
    chemin: str | Path,
    index: bool = False,
) -> Path:
    """Exporte un rapport au format CSV.

    Entrée :
        dataframe : données à exporter.
        chemin : chemin du fichier CSV cible.
        index : indique si l'index pandas doit être exporté.

    Traitement :
        Crée le dossier parent puis écrit le fichier en UTF-8 avec BOM.

    Validation :
        Le dossier parent est créé automatiquement s'il n'existe pas.

    Retour :
        Chemin du fichier CSV généré.
    """
    path = Path(chemin)
    path.parent.mkdir(parents=True, exist_ok=True)

    dataframe.to_csv(
        path,
        index=index,
        encoding="utf-8-sig",
    )

    return path


def export_rapports_excel(
    rapports: dict[str, pd.DataFrame],
    chemin: str | Path,
) -> Path:
    """Exporte plusieurs rapports dans un classeur Excel.

    Entrée :
        rapports : dictionnaire associant un nom à chaque DataFrame.
        chemin : chemin du fichier Excel cible.

    Traitement :
        Crée une feuille par rapport en respectant la limite Excel
        de 31 caractères pour le nom des feuilles.

    Validation :
        Le dossier parent est créé automatiquement s'il n'existe pas.

    Retour :
        Chemin du fichier Excel généré.
    """
    path = Path(chemin)
    path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        for nom, dataframe in rapports.items():
            sheet = str(nom)[:31]
            dataframe.to_excel(
                writer,
                sheet_name=sheet,
                index=False,
            )

    return path


# ============================================================
# 5. AGRÉGATION DES RAPPORTS
# ============================================================

def get_all_rapports(
    date_debut: str | None = None,
    date_fin: str | None = None,
) -> dict[str, pd.DataFrame]:
    """Retourne l'ensemble des rapports disponibles.

    Entrée :
        date_debut : date minimale facultative.
        date_fin : date maximale facultative.

    Traitement :
        Exécute chaque fonction de rapport avec la même plage de dates.

    Validation :
        Le rapport de stock est généré sans filtre de date,
        conformément à son fonctionnement initial.

    Retour :
        Dictionnaire contenant tous les DataFrames de rapport.
    """
    return {
        "ventes": get_rapport_ventes(date_debut, date_fin),
        "achats": get_rapport_achats(date_debut, date_fin),
        "stock": get_rapport_stock(),
        "depenses": get_rapport_depenses(date_debut, date_fin),
        "pertes": get_rapport_pertes(date_debut, date_fin),
        "inventaire": get_rapport_inventaire(date_debut, date_fin),
        "tresorerie": get_rapport_tresorerie(date_debut, date_fin),
        "profitabilite": get_rapport_profitabilite(
            date_debut,
            date_fin,
        ),
        "controle_prix": get_rapport_controle_prix(
            date_debut,
            date_fin,
        ),
    }
