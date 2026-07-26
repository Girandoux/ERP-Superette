# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : inventaire_db.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from config.database import get_engine
from database.database_utils import fetch_one, execute_query, read_sql_dataframe, record_exists
from database.dates_db import date_exists,ensure_month_dates
from database.produits_db import product_exists

logger = logging.getLogger("database")
engine = get_engine()
TABLE_NAME = "fact_inventaire"
PRODUITS_TABLE = "dim_produits"
DATE_TABLE = "dim_date"
PERTES_TABLE = "dim_pertes"
ID_COLUMN = "inventaire_id"


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

def _float(value):
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

def ensure_inventaire_cloture_columns():
    """Ajoute les colonnes de cloture si la base existe deja."""
    queries = [
        f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS cloture BOOLEAN NOT NULL DEFAULT FALSE",
        f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS date_cloture TIMESTAMP",
        f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS perte_id INTEGER",
        f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS ajustement_stock INTEGER NOT NULL DEFAULT 0"
    ]
    ok = True
    for query in queries:
        ok = execute_query(query) and ok
    return ok

def inventaire_exists(inventaire_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    return record_exists(f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": inventaire_id})

def validate_inventaire_data(date_inventaire, produit_id, stock_physique):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    if not date_inventaire:
        return False, "Date inventaire invalide."
    if not ensure_month_dates(date_inventaire):
        return False, "Le mois de l'inventaire n'a pas pu etre cree dans dim_date."
    if not date_exists(date_inventaire):
        return False, "La date d'inventaire n'existe pas dans dim_date."
    if not produit_id or not product_exists(produit_id):
        return False, "Produit invalide."
    if _int(stock_physique) < 0:
        return False, "Le stock physique ne peut pas etre negatif."
    return True, "OK"

def get_all_inventaires():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    query = f"""
    SELECT i.*,p.code_produit,p.nom_produit
    FROM {TABLE_NAME} i LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = i.produit_id
    ORDER BY i.date_inventaire DESC,i.inventaire_id DESC
    """
    return read_sql_dataframe(query)

def get_inventaire_by_id(inventaire_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    return fetch_one(f"SELECT * FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id", {"id": inventaire_id})

def search_inventaires(keyword=None, produit_id=None):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    query = f"SELECT i.*,p.code_produit,p.nom_produit FROM {TABLE_NAME} i LEFT JOIN {PRODUITS_TABLE} p ON p.produit_id = i.produit_id WHERE 1=1"
    params = {}
    if keyword:
        query += " AND (p.code_produit ILIKE :keyword OR p.nom_produit ILIKE :keyword OR i.commentaire ILIKE :keyword OR i.utilisateur ILIKE :keyword)"
        params["keyword"] = f"%{keyword}%"
    if produit_id:
        query += " AND i.produit_id = :produit_id"
        params["produit_id"] = produit_id
    query += " ORDER BY i.date_inventaire DESC,i.inventaire_id DESC"
    return read_sql_dataframe(query, params)

def get_inventaires_by_date(start_date, end_date):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    return read_sql_dataframe(f"SELECT * FROM {TABLE_NAME} WHERE date_inventaire BETWEEN :start AND :end ORDER BY date_inventaire DESC", {"start": start_date, "end": end_date})

def insert_inventaire(date_inventaire, produit_id, stock_physique, commentaire=None, utilisateur="SYSTEM"):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    valid, message = validate_inventaire_data(date_inventaire, produit_id, stock_physique)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    INSERT INTO {TABLE_NAME} (date_inventaire,date_id,produit_id,stock_theorique,stock_physique,ecart,valeur_ecart,commentaire,utilisateur,cloture,ajustement_stock)
    VALUES (:date_inventaire,:date_id,:produit_id,0,:stock_physique,0,0,:commentaire,:utilisateur,FALSE,0)
    """
    return execute_query(query, {"date_inventaire": date_inventaire, "date_id": date_inventaire, "produit_id": produit_id, "stock_physique": _int(stock_physique), "commentaire": _txt(commentaire) or None, "utilisateur": _txt(utilisateur) or "SYSTEM"})

def update_inventaire(inventaire_id, date_inventaire, produit_id, stock_physique, commentaire=None, utilisateur="SYSTEM"):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    current = get_inventaire_by_id(inventaire_id)
    if not current or bool(current.get("cloture", False)):
        return False
    valid, message = validate_inventaire_data(date_inventaire, produit_id, stock_physique)
    if not valid:
        logger.warning(message)
        return False
    query = f"""
    UPDATE {TABLE_NAME}
    SET date_inventaire = :date_inventaire,date_id = :date_id,produit_id = :produit_id,stock_physique = :stock_physique,commentaire = :commentaire,utilisateur = :utilisateur
    WHERE {ID_COLUMN} = :id AND COALESCE(cloture,FALSE)=FALSE
    """
    return execute_query(query, {"id": inventaire_id, "date_inventaire": date_inventaire, "date_id": date_inventaire, "produit_id": produit_id, "stock_physique": _int(stock_physique), "commentaire": _txt(commentaire) or None, "utilisateur": _txt(utilisateur) or "SYSTEM"})

def delete_inventaire(inventaire_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    current = get_inventaire_by_id(inventaire_id)
    if not current or bool(current.get("cloture", False)):
        return False
    return execute_query(f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id AND COALESCE(cloture,FALSE)=FALSE", {"id": inventaire_id})

def cloturer_inventaire(inventaire_id, utilisateur="SYSTEM"):
    """Cloture un inventaire, cree une perte si manque et aligne le stock reel."""
    ensure_inventaire_cloture_columns()
    utilisateur = _txt(utilisateur) or "SYSTEM"
    try:
        with engine.begin() as connection:
            row = connection.execute(text(f"""
                SELECT i.*,p.stock_actuel,COALESCE(cout.pu_achat_piece,0) AS cout_unitaire
                FROM {TABLE_NAME} i
                JOIN {PRODUITS_TABLE} p ON p.produit_id=i.produit_id
                LEFT JOIN (
                    SELECT DISTINCT ON (produit_id) produit_id,pu_achat_piece
                    FROM dim_lignes_achat
                    ORDER BY produit_id,ligne_achat_id DESC
                ) cout ON cout.produit_id=i.produit_id
                WHERE i.{ID_COLUMN}=:id
                FOR UPDATE OF i
            """), {"id": inventaire_id}).mappings().first()
            if not row:
                return {"success": False, "message": "Inventaire introuvable.", "data": None}
            data = dict(row)
            if bool(data.get("cloture", False)):
                return {"success": False, "message": "Cet inventaire est deja cloture.", "data": data}
            produit_id = data["produit_id"]
            stock_theorique = _int(data.get("stock_theorique"))
            stock_physique = _int(data.get("stock_physique"))
            ecart = _int(data.get("ecart"))
            cout_unitaire = _float(data.get("cout_unitaire"))
            perte_id = None
            connection.execute(text(f"UPDATE {PRODUITS_TABLE} SET stock_actuel=:stock WHERE produit_id=:produit_id"), {"stock": stock_theorique, "produit_id": produit_id})
            if ecart < 0:
                qte_perte = abs(ecart)
                perte = connection.execute(text(f"""
                    INSERT INTO {PERTES_TABLE} (date_perte,date_id,produit_id,qte_perte,motif_perte,valeur_unitaire,valeur_totale,utilisateur)
                    VALUES (:date_perte,:date_id,:produit_id,:qte_perte,'Inventaire',:valeur_unitaire,0,:utilisateur)
                    RETURNING perte_id
                """), {
                    "date_perte": data["date_inventaire"],
                    "date_id": data["date_id"],
                    "produit_id": produit_id,
                    "qte_perte": qte_perte,
                    "valeur_unitaire": cout_unitaire,
                    "utilisateur": utilisateur
                }).mappings().first()
                perte_id = perte["perte_id"] if perte else None
                connection.execute(text(f"UPDATE {PRODUITS_TABLE} SET stock_actuel=:stock WHERE produit_id=:produit_id"), {"stock": stock_theorique, "produit_id": produit_id})
            connection.execute(text(f"""
                UPDATE {TABLE_NAME}
                SET cloture=TRUE,date_cloture=CURRENT_TIMESTAMP,perte_id=:perte_id,ajustement_stock=:ecart,utilisateur=:utilisateur
                WHERE {ID_COLUMN}=:id
            """), {"id": inventaire_id, "perte_id": perte_id, "ecart": ecart, "utilisateur": utilisateur})
            connection.execute(text(f"UPDATE {PRODUITS_TABLE} SET stock_actuel=:stock WHERE produit_id=:produit_id"), {"stock": stock_physique, "produit_id": produit_id})
            return {"success": True, "message": "Inventaire cloture et stock actualise.", "data": {"inventaire_id": inventaire_id, "produit_id": produit_id, "ecart": ecart, "perte_id": perte_id, "stock_final": stock_physique}}
    except SQLAlchemyError as error:
        logger.exception("Erreur cloture inventaire: %s", error)
        return {"success": False, "message": "Cloture de l'inventaire impossible.", "data": str(error)}


def cloturer_inventaires_by_date(date_inventaire, utilisateur="SYSTEM"):
    """Cloture tous les inventaires ouverts d'une date."""
    ensure_inventaire_cloture_columns()
    rows = read_sql_dataframe(
        f"SELECT {ID_COLUMN} FROM {TABLE_NAME} WHERE date_inventaire=:date_inventaire AND COALESCE(cloture,FALSE)=FALSE ORDER BY {ID_COLUMN}",
        {"date_inventaire": date_inventaire}
    )
    if rows.empty:
        return {"success": False, "message": "Aucun inventaire ouvert pour cette date.", "data": {"date": str(date_inventaire), "total": 0}}
    successes=[]
    errors=[]
    for _,row in rows.iterrows():
        result=cloturer_inventaire(int(row[ID_COLUMN]), utilisateur)
        if result.get("success"):
            successes.append(result.get("data"))
        else:
            errors.append({"inventaire_id": int(row[ID_COLUMN]), "message": result.get("message")})
    data={"date": str(date_inventaire), "total": len(rows), "clotures": len(successes), "erreurs": errors}
    if errors:
        return {"success": False, "message": "Cloture partielle terminee avec erreurs.", "data": data}
    return {"success": True, "message": "Tous les inventaires ouverts de cette date sont clotures.", "data": data}

def corriger_inventaire_cloture(inventaire_id, nouveau_stock_physique, commentaire=None, utilisateur="SYSTEM"):
    """Cree une correction tracee pour un inventaire deja cloture."""
    ensure_inventaire_cloture_columns()
    source=get_inventaire_by_id(inventaire_id)
    if not source:
        return {"success": False, "message": "Inventaire source introuvable.", "data": None}
    if not bool(source.get("cloture", False)):
        return {"success": False, "message": "La correction est reservee aux inventaires deja clotures.", "data": source}
    stock_final=_int(nouveau_stock_physique)
    if stock_final<0:
        return {"success": False, "message": "Le nouveau stock physique ne peut pas etre negatif.", "data": None}
    note=_txt(commentaire) or "Correction apres cloture"
    note=f"CORRECTION inventaire #{inventaire_id} - {note}"
    try:
        with engine.begin() as connection:
            connection.execute(text(f"UPDATE {PRODUITS_TABLE} SET stock_actuel=:stock WHERE produit_id=:produit_id"), {"stock": source["stock_physique"], "produit_id": source["produit_id"]})
            new_id=connection.execute(text(f"""
                INSERT INTO {TABLE_NAME} (date_inventaire,date_id,produit_id,stock_theorique,stock_physique,ecart,valeur_ecart,commentaire,utilisateur,cloture,ajustement_stock)
                VALUES (CURRENT_DATE,CURRENT_DATE,:produit_id,0,:stock_physique,0,0,:commentaire,:utilisateur,FALSE,0)
                RETURNING {ID_COLUMN}
            """), {"produit_id": source["produit_id"], "stock_physique": stock_final, "commentaire": note, "utilisateur": _txt(utilisateur) or "SYSTEM"}).scalar()
        result=cloturer_inventaire(new_id, utilisateur)
        if not result.get("success"):
            return result
        data=result.get("data") or {}
        data["source_inventaire_id"]=inventaire_id
        data["correction_inventaire_id"]=new_id
        data["nouveau_stock_physique"]=stock_final
        return {"success": True, "message": "Correction inventaire creee, cloturee et stock actualise.", "data": data}
    except SQLAlchemyError as error:
        logger.exception("Erreur correction inventaire: %s", error)
        return {"success": False, "message": "Correction inventaire impossible.", "data": str(error)}
def get_inventaire_ecarts(include_closed=False):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    query = f"""
    SELECT i.*,p.code_produit,p.nom_produit
    FROM {TABLE_NAME} i JOIN {PRODUITS_TABLE} p ON p.produit_id = i.produit_id
    WHERE i.ecart <> 0
    """
    if not include_closed:
        query += " AND COALESCE(i.cloture,FALSE)=FALSE"
    query += " ORDER BY ABS(i.ecart) DESC"
    return read_sql_dataframe(query)

def get_inventaire_history_for_product(produit_id, exclude_id=None, limit=10):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    query = f"""
    SELECT i.*,p.code_produit,p.nom_produit
    FROM {TABLE_NAME} i JOIN {PRODUITS_TABLE} p ON p.produit_id=i.produit_id
    WHERE i.produit_id=:produit_id
    """
    params = {"produit_id": produit_id, "limit": int(limit)}
    if exclude_id:
        query += " AND i.inventaire_id <> :exclude_id"
        params["exclude_id"] = exclude_id
    query += " ORDER BY i.date_inventaire DESC,i.inventaire_id DESC LIMIT :limit"
    return read_sql_dataframe(query, params)

def compare_inventaire_with_previous(inventaire_id):
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    current = fetch_one(f"""
        SELECT i.*,p.code_produit,p.nom_produit
        FROM {TABLE_NAME} i JOIN {PRODUITS_TABLE} p ON p.produit_id=i.produit_id
        WHERE i.{ID_COLUMN}=:id
    """, {"id": inventaire_id})
    if not current:
        return None
    previous = fetch_one(f"""
        SELECT i.*,p.code_produit,p.nom_produit
        FROM {TABLE_NAME} i JOIN {PRODUITS_TABLE} p ON p.produit_id=i.produit_id
        WHERE i.produit_id=:produit_id AND i.{ID_COLUMN}<>:id
        ORDER BY i.date_inventaire DESC,i.inventaire_id DESC
        LIMIT 1
    """, {"produit_id": current["produit_id"], "id": inventaire_id})
    return {
        "current": current,
        "previous": previous,
        "delta_stock_physique": _int(current.get("stock_physique")) - _int(previous.get("stock_physique")) if previous else None,
        "delta_ecart": _int(current.get("ecart")) - _int(previous.get("ecart")) if previous else None
    }


def get_controle_stock(date_debut, date_fin):
    """Controle le stock par produit sur une periode.
    Les pertes Inventaire sont informatives; elles sont deja incluses dans le stock compte.
    Si le stock brut devient negatif, la vente excedentaire est signalee comme MANQUANT.
    """
    ensure_inventaire_cloture_columns()
    query = f"""
    WITH params AS (
        SELECT CAST(:date_debut AS date) AS date_debut,CAST(:date_fin AS date) AS date_fin
    ),
    dernier_inventaire AS (
        SELECT DISTINCT ON (i.produit_id)
            i.produit_id,
            i.date_inventaire,
            GREATEST(COALESCE(i.stock_physique,0),0) AS stock_dernier_inventaire
        FROM {TABLE_NAME} i
        CROSS JOIN params p
        WHERE i.date_inventaire <= p.date_debut
          AND COALESCE(i.cloture,FALSE)=TRUE
        ORDER BY i.produit_id,i.date_inventaire DESC,i.{ID_COLUMN} DESC
    ),
    base_produits AS (
        SELECT
            p.produit_id,
            p.code_produit,
            p.nom_produit,
            COALESCE(c.nom_categorie,'Non classe') AS nom_categorie,
            COALESCE(p.stock_actuel,0) AS stock_actuel,
            COALESCE(di.stock_dernier_inventaire,0) AS stock_dernier_inventaire,
            di.date_inventaire AS date_dernier_inventaire,
            CASE WHEN di.date_inventaire IS NULL THEN prm.date_debut ELSE di.date_inventaire END::date AS date_debut_mouvements,
            prm.date_fin
        FROM {PRODUITS_TABLE} p
        CROSS JOIN params prm
        LEFT JOIN dim_categories c ON c.categorie_id=p.categorie_id
        LEFT JOIN dernier_inventaire di ON di.produit_id=p.produit_id
        WHERE COALESCE(p.actif,TRUE)=TRUE
    ),
    achats_periode AS (
        SELECT bp.produit_id,COALESCE(SUM(COALESCE(la.quantite_achat,0)),0) AS quantite_achetee
        FROM base_produits bp
        LEFT JOIN fact_achats a ON a.date_achat >= bp.date_debut_mouvements AND a.date_achat <= bp.date_fin
        LEFT JOIN dim_lignes_achat la ON la.achat_id=a.achat_id AND la.produit_id=bp.produit_id
        GROUP BY bp.produit_id
    ),
    ventes_periode AS (
        SELECT bp.produit_id,COALESCE(SUM(COALESCE(lv.qte_vente,0)),0) AS quantite_vendue
        FROM base_produits bp
        LEFT JOIN fact_ventes v ON v.date_vente >= bp.date_debut_mouvements AND v.date_vente <= bp.date_fin
        LEFT JOIN dim_lignes_vente lv ON lv.vente_id=v.vente_id AND lv.produit_id=bp.produit_id
        GROUP BY bp.produit_id
    ),
    pertes_signalees AS (
        SELECT bp.produit_id,COALESCE(SUM(COALESCE(pe.qte_perte,0)),0) AS quantite_perdue_signalee
        FROM base_produits bp
        LEFT JOIN dim_pertes pe ON pe.produit_id=bp.produit_id
            AND pe.date_perte >= bp.date_debut_mouvements
            AND pe.date_perte <= bp.date_fin
            AND UPPER(COALESCE(pe.motif_perte,'')) <> 'INVENTAIRE'
        GROUP BY bp.produit_id
    ),
    pertes_inventaire AS (
        SELECT bp.produit_id,COALESCE(SUM(COALESCE(pe.qte_perte,0)),0) AS quantite_perdue_inventaire
        FROM base_produits bp
        LEFT JOIN dim_pertes pe ON pe.produit_id=bp.produit_id
            AND pe.date_perte >= bp.date_debut_mouvements
            AND pe.date_perte <= bp.date_fin
            AND UPPER(COALESCE(pe.motif_perte,'')) = 'INVENTAIRE'
        GROUP BY bp.produit_id
    ),
    controle_base AS (
        SELECT
            bp.produit_id,
            bp.code_produit,
            bp.nom_produit,
            bp.nom_categorie,
            bp.stock_actuel,
            bp.stock_dernier_inventaire,
            bp.date_dernier_inventaire,
            bp.date_debut_mouvements,
            COALESCE(ap.quantite_achetee,0) AS quantite_achetee,
            COALESCE(vp.quantite_vendue,0) AS quantite_vendue,
            COALESCE(ps.quantite_perdue_signalee,0) AS quantite_perdue,
            COALESCE(ps.quantite_perdue_signalee,0) AS quantite_perdue_signalee,
            COALESCE(pi.quantite_perdue_inventaire,0) AS quantite_perdue_inventaire,
            bp.stock_dernier_inventaire
            + COALESCE(ap.quantite_achetee,0)
            - COALESCE(vp.quantite_vendue,0)
            - COALESCE(ps.quantite_perdue_signalee,0) AS stock_theorique_brut
        FROM base_produits bp
        LEFT JOIN achats_periode ap ON ap.produit_id=bp.produit_id
        LEFT JOIN ventes_periode vp ON vp.produit_id=bp.produit_id
        LEFT JOIN pertes_signalees ps ON ps.produit_id=bp.produit_id
        LEFT JOIN pertes_inventaire pi ON pi.produit_id=bp.produit_id
    ),
    controle AS (
        SELECT *,
            GREATEST(stock_theorique_brut,0) AS stock_theorique_attendu,
            ABS(LEAST(stock_theorique_brut,0)) AS vente_excedentaire
        FROM controle_base
    )
    SELECT *,
        CASE WHEN stock_theorique_brut<0 THEN stock_theorique_brut ELSE stock_actuel-stock_theorique_attendu END AS ecart_controle
    FROM controle
    ORDER BY nom_categorie,nom_produit
    """
    return read_sql_dataframe(query, {"date_debut": str(date_debut), "date_fin": str(date_fin)})

def synchroniser_stock_depuis_controle(date_debut, date_fin):
    """Aligne dim_produits.stock_actuel sur le stock theorique attendu du controle.
    Les pertes Inventaire ne sont pas retirees une seconde fois.
    """
    ensure_inventaire_cloture_columns()
    query = f"""
    WITH params AS (
        SELECT CAST(:date_debut AS date) AS date_debut,CAST(:date_fin AS date) AS date_fin
    ),
    dernier_inventaire AS (
        SELECT DISTINCT ON (i.produit_id)
            i.produit_id,
            i.date_inventaire,
            GREATEST(COALESCE(i.stock_physique,0),0) AS stock_dernier_inventaire
        FROM {TABLE_NAME} i
        CROSS JOIN params p
        WHERE i.date_inventaire <= p.date_debut
          AND COALESCE(i.cloture,FALSE)=TRUE
        ORDER BY i.produit_id,i.date_inventaire DESC,i.{ID_COLUMN} DESC
    ),
    base_produits AS (
        SELECT
            p.produit_id,
            COALESCE(di.stock_dernier_inventaire,0) AS stock_dernier_inventaire,
            CASE WHEN di.date_inventaire IS NULL THEN prm.date_debut ELSE di.date_inventaire END::date AS date_debut_mouvements,
            prm.date_fin
        FROM {PRODUITS_TABLE} p
        CROSS JOIN params prm
        LEFT JOIN dernier_inventaire di ON di.produit_id=p.produit_id
        WHERE COALESCE(p.actif,TRUE)=TRUE
    ),
    achats_periode AS (
        SELECT bp.produit_id,COALESCE(SUM(COALESCE(la.quantite_achat,0)),0) AS quantite_achetee
        FROM base_produits bp
        LEFT JOIN fact_achats a ON a.date_achat >= bp.date_debut_mouvements AND a.date_achat <= bp.date_fin
        LEFT JOIN dim_lignes_achat la ON la.achat_id=a.achat_id AND la.produit_id=bp.produit_id
        GROUP BY bp.produit_id
    ),
    ventes_periode AS (
        SELECT bp.produit_id,COALESCE(SUM(COALESCE(lv.qte_vente,0)),0) AS quantite_vendue
        FROM base_produits bp
        LEFT JOIN fact_ventes v ON v.date_vente >= bp.date_debut_mouvements AND v.date_vente <= bp.date_fin
        LEFT JOIN dim_lignes_vente lv ON lv.vente_id=v.vente_id AND lv.produit_id=bp.produit_id
        GROUP BY bp.produit_id
    ),
    pertes_signalees AS (
        SELECT bp.produit_id,COALESCE(SUM(COALESCE(pe.qte_perte,0)),0) AS quantite_perdue_signalee
        FROM base_produits bp
        LEFT JOIN dim_pertes pe ON pe.produit_id=bp.produit_id
            AND pe.date_perte >= bp.date_debut_mouvements
            AND pe.date_perte <= bp.date_fin
            AND UPPER(COALESCE(pe.motif_perte,'')) <> 'INVENTAIRE'
        GROUP BY bp.produit_id
    ),
    controle AS (
        SELECT
            bp.produit_id,
            GREATEST(
                bp.stock_dernier_inventaire
                + COALESCE(ap.quantite_achetee,0)
                - COALESCE(vp.quantite_vendue,0)
                - COALESCE(ps.quantite_perdue_signalee,0),
                0
            ) AS stock_calcule
        FROM base_produits bp
        LEFT JOIN achats_periode ap ON ap.produit_id=bp.produit_id
        LEFT JOIN ventes_periode vp ON vp.produit_id=bp.produit_id
        LEFT JOIN pertes_signalees ps ON ps.produit_id=bp.produit_id
    )
    UPDATE {PRODUITS_TABLE} p
    SET stock_actuel=controle.stock_calcule
    FROM controle
    WHERE p.produit_id=controle.produit_id
      AND COALESCE(p.stock_actuel,0)<>controle.stock_calcule
    RETURNING p.produit_id
    """
    params = {"date_debut": str(date_debut), "date_fin": str(date_fin)}
    try:
        with engine.begin() as connection:
            rows = connection.execute(text(query), params).fetchall()
            return len(rows)
    except SQLAlchemyError as error:
        logger.exception("Erreur synchronisation controle stock: %s", error)
        return 0

def get_inventaire_statistics():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    ensure_inventaire_cloture_columns()
    query = f"""
    SELECT COUNT(*) AS total_controles,
    COUNT(*) FILTER (WHERE COALESCE(cloture,FALSE)=TRUE) AS clotures,
    COUNT(*) FILTER (WHERE COALESCE(cloture,FALSE)=FALSE AND ecart = 0) AS conformes,
    COUNT(*) FILTER (WHERE COALESCE(cloture,FALSE)=FALSE AND ecart > 0) AS surplus,
    COUNT(*) FILTER (WHERE COALESCE(cloture,FALSE)=FALSE AND ecart < 0) AS manquants,
    COALESCE(SUM(ABS(ecart)) FILTER (WHERE COALESCE(cloture,FALSE)=FALSE),0) AS total_ecarts,
    COALESCE(SUM(valeur_ecart) FILTER (WHERE COALESCE(cloture,FALSE)=FALSE),0) AS valeur_ecarts
    FROM {TABLE_NAME}
    """
    return fetch_one(query) or {}

def get_inventaire_kpis():
    """
     Entree : parametres fournis par l'application ou les autres modules.
     Traitement : applique la logique existante sans modifier le comportement.
     Validation : conserve les controles presents dans le code d'origine.
     Retour : valeur, dictionnaire ou DataFrame attendu par l'appelant.
    """
    stats = get_inventaire_statistics()
    return {
        "total_controles": int(stats.get("total_controles", 0)),
        "clotures": int(stats.get("clotures", 0)),
        "conformes": int(stats.get("conformes", 0)),
        "surplus": int(stats.get("surplus", 0)),
        "manquants": int(stats.get("manquants", 0)),
        "total_ecarts": int(stats.get("total_ecarts", 0)),
        "valeur_ecarts": float(stats.get("valeur_ecarts", 0))
    }

__all__ = ["get_all_inventaires","get_inventaire_by_id","search_inventaires","get_inventaires_by_date","insert_inventaire","update_inventaire","delete_inventaire","cloturer_inventaire","cloturer_inventaires_by_date","corriger_inventaire_cloture","get_inventaire_ecarts","get_inventaire_history_for_product","compare_inventaire_with_previous","get_controle_stock","synchroniser_stock_depuis_controle","get_inventaire_statistics","get_inventaire_kpis"]

