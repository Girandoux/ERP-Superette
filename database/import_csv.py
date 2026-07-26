# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : import_csv.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import time
import re
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from config.database import get_engine, test_connection
from config.settings import CSV_DIR, CSV_FILES, CSV_IMPORT_ORDER, LOGS_DIR

# ============================================================
# 1. CONFIGURATION
# ============================================================

engine = get_engine()
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "import.log"
logger = logging.getLogger("import_csv")
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
logger.propagate = False
IMPORT_RESULTS = {"success": [], "failed": [], "rows": 0}

# ============================================================
# 2. INSPECTION POSTGRESQL
# ============================================================

def get_inspector():
    """Retourne l'inspecteur SQLAlchemy."""
    return inspect(engine)

def table_exists(table_name):
    """Verifie si une table existe dans PostgreSQL."""
    return get_inspector().has_table(table_name)

def get_table_schema(table_name):
    """Retourne les colonnes, types, nullables et cles primaires."""
    inspector = get_inspector()
    columns = inspector.get_columns(table_name)
    pk_columns = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
    return {
        col["name"]: {
            "type": str(col["type"]).upper(),
            "nullable": col.get("nullable", True),
            "primary_key": col["name"] in pk_columns
        }
        for col in columns
    }

def get_database_schema():
    """Charge le schema des tables de l'ordre d'import."""
    schema = {}
    for table in CSV_IMPORT_ORDER:
        if table_exists(table):
            schema[table] = get_table_schema(table)
        else:
            logger.warning(f"Table absente : {table}")
    return schema

# ============================================================
# 3. LECTURE DES CSV
# ============================================================

def get_csv_path(table_name):
    """Retourne le chemin CSV attendu pour une table."""
    path = CSV_FILES.get(table_name, CSV_DIR / f"{table_name}.csv")
    if Path(path).exists():
        return Path(path)
    for file in CSV_DIR.glob("*.csv"):
        if file.stem.lower() == table_name.lower():
            return file
    return Path(path)

def read_csv_file(csv_path):
    """Lit un CSV avec detection du separateur."""
    try:
        return pd.read_csv(csv_path, sep=None, engine="python", encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(csv_path, sep=None, engine="python", encoding="latin1")

def normalize_column_names(df):
    """Nettoie les noms de colonnes."""
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    df = df[[col for col in df.columns if col and not col.startswith("unnamed")]]
    return df

# ============================================================
# 4. NETTOYAGE ET CONVERSION
# ============================================================

def replace_null_values(df):
    """Remplace les valeurs vides par None."""
    return df.replace({np.nan: None, pd.NaT: None, "": None, " ": None, "nan": None, "NaN": None, "NULL": None, "null": None})

def clean_numeric_value(value):
    """Nettoie une valeur numerique."""
    if value is None or pd.isna(value):
        return None
    value = str(value).strip().replace("FCFA", "").replace("€", "").replace("$", "").replace(" ", "")
    if value in ("", "-", "–", "—"):
        return 0
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    elif "." in value and re.fullmatch(r"\d{1,3}(\.\d{3})+", value):
        value = value.replace(".", "")
    try:
        return float(value)
    except ValueError:
        return None

def fill_table_defaults(df, table_name):
    """Complete les valeurs manquantes connues avant import."""
    df = df.copy()
    if table_name == "fact_achats":
        if "frais_enlevement" in df.columns:
            df["frais_enlevement"] = df["frais_enlevement"].fillna(0)
        if "type_achat" in df.columns:
            df["type_achat"] = df["type_achat"].fillna("Achat fournisseur")
    if table_name == "dim_lignes_achat":
        for col in ["qte_cartons", "qte_par_carton", "quantite_achat", "pu_achat_carton", "pu_achat_piece", "total_achat"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if {"qte_cartons", "quantite_achat", "qte_par_carton"}.issubset(df.columns):
            mask = (df["qte_cartons"].isna() | (df["qte_cartons"] <= 0)) & df["quantite_achat"].notna() & (df["quantite_achat"] > 0) & df["qte_par_carton"].notna() & (df["qte_par_carton"] > 0)
            df.loc[mask, "qte_cartons"] = df.loc[mask, "quantite_achat"] / df.loc[mask, "qte_par_carton"]
        if {"qte_par_carton", "quantite_achat", "qte_cartons"}.issubset(df.columns):
            mask = (df["qte_par_carton"].isna() | (df["qte_par_carton"] <= 0)) & df["quantite_achat"].notna() & (df["quantite_achat"] > 0) & df["qte_cartons"].notna() & (df["qte_cartons"] > 0)
            df.loc[mask, "qte_par_carton"] = (df.loc[mask, "quantite_achat"] / df.loc[mask, "qte_cartons"]).round()
        if {"quantite_achat", "qte_cartons", "qte_par_carton"}.issubset(df.columns):
            mask = df["qte_par_carton"].isna() & df["quantite_achat"].notna() & df["qte_cartons"].notna() & (df["qte_cartons"] != 0)
            df.loc[mask, "qte_par_carton"] = (df.loc[mask, "quantite_achat"] / df.loc[mask, "qte_cartons"]).round()
            mask = (df["quantite_achat"].isna() | (df["quantite_achat"] <= 0)) & df["qte_cartons"].notna() & df["qte_par_carton"].notna()
            df.loc[mask, "quantite_achat"] = (df.loc[mask, "qte_cartons"] * df.loc[mask, "qte_par_carton"]).round()
        if {"pu_achat_piece", "qte_par_carton", "pu_achat_carton"}.issubset(df.columns):
            mask = df["pu_achat_carton"].isna() & df["pu_achat_piece"].notna() & df["qte_par_carton"].notna()
            df.loc[mask, "pu_achat_carton"] = df.loc[mask, "pu_achat_piece"] * df.loc[mask, "qte_par_carton"]
        if {"total_achat", "qte_cartons", "pu_achat_carton"}.issubset(df.columns):
            mask = df["pu_achat_carton"].isna() & df["total_achat"].notna() & df["qte_cartons"].notna() & (df["qte_cartons"] != 0)
            df.loc[mask, "pu_achat_carton"] = df.loc[mask, "total_achat"] / df.loc[mask, "qte_cartons"]
            mask = (df["total_achat"].isna() | (df["total_achat"] <= 0)) & df["qte_cartons"].notna() & df["pu_achat_carton"].notna()
            df.loc[mask, "total_achat"] = df.loc[mask, "qte_cartons"] * df.loc[mask, "pu_achat_carton"]
        if {"date_fabrication", "date_peremption"}.issubset(df.columns):
            mask = df["date_fabrication"].notna() & df["date_peremption"].notna() & (df["date_peremption"] < df["date_fabrication"])
            df.loc[mask, "date_peremption"] = None
            if mask.any():
                logger.warning(f"{table_name} : {int(mask.sum())} date(s) de peremption incoherente(s) videe(s)")
        for col in ["qte_cartons", "qte_par_carton", "quantite_achat", "pu_achat_carton", "pu_achat_piece", "total_achat"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)
    if table_name == "fact_inventaire":
        for col in ["stock_theorique", "ecart", "valeur_ecart"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        for col in ["stock_theorique", "stock_physique"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)
        if "utilisateur" in df.columns:
            df["utilisateur"] = df["utilisateur"].fillna("SYSTEM")
    if table_name in ["fact_depenses", "dim_pertes", "fact_tresorerie"]:
        for col in ["montant", "qte_perte", "valeur_unitaire", "valeur_totale"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        if "utilisateur" in df.columns:
            df["utilisateur"] = df["utilisateur"].fillna("SYSTEM")
    if table_name == "dim_produits":
        if "qte_par_carton" in df.columns:
            df["qte_par_carton"] = df["qte_par_carton"].fillna(1)
        if "stock_min" in df.columns:
            df["stock_min"] = df["stock_min"].fillna(0)
        if "stock_actuel" in df.columns:
            df["stock_actuel"] = df["stock_actuel"].fillna(0)
        if "actif" in df.columns:
            df["actif"] = df["actif"].fillna(True)
    if table_name == "dim_pertes" and "motif_perte" in df.columns:
        df["motif_perte"] = df["motif_perte"].apply(normalize_motif_perte)
    return df

def normalize_motif_perte(value):
    """Normalise les motifs de perte selon la contrainte PostgreSQL."""
    if value is None or pd.isna(value):
        return "Inventaire"
    key = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    accents = {"é": "e", "è": "e", "ê": "e", "à": "a", "â": "a", "ù": "u", "û": "u", "ô": "o", "î": "i", "ï": "i"}
    for old, new in accents.items():
        key = key.replace(old, new)
    mapping = {
        "perime": "Perime",
        "perimee": "Perime",
        "expiration": "Perime",
        "casse": "Casse",
        "cassee": "Casse",
        "vole": "Vole",
        "volee": "Vole",
        "vol": "Vole",
        "don": "Don",
        "inventaire": "Inventaire",
        "ecart_inventaire": "Inventaire",
        "consommation_interne": "Consommation_Interne",
        "consommation": "Consommation_Interne"
    }
    return mapping.get(key, "Inventaire")

def apply_business_filters(df, table_name):
    """Supprime ou corrige les lignes incompatibles avec les contraintes metier."""
    before = len(df)
    if table_name == "dim_produits" and "code_produit" in df.columns:
        df = df.dropna(subset=["code_produit"])
        df = make_unique_product_codes(df)
    if table_name == "dim_lignes_achat":
        positive_cols = [col for col in ["qte_cartons", "qte_par_carton", "quantite_achat", "pu_achat_piece", "total_achat"] if col in df.columns]
        for col in positive_cols:
            df = df[df[col].fillna(0) > 0]
    if table_name == "dim_lignes_vente":
        positive_cols = [col for col in ["qte_vente", "pu_vente", "montant_ligne"] if col in df.columns]
        for col in positive_cols:
            df = df[df[col].fillna(0) > 0]
    if table_name == "dim_pertes":
        positive_cols = [col for col in ["qte_perte", "valeur_unitaire", "valeur_totale"] if col in df.columns]
        for col in positive_cols:
            df = df[df[col].fillna(0) >= 0]
    removed = before - len(df)
    if removed:
        logger.warning(f"{table_name} : {removed} ligne(s) incompatible(s) corrigee(s)/supprimee(s) avant import")
    return df

def make_unique_product_codes(df):
    """Rend code_produit unique sans supprimer les produits du CSV."""
    if "code_produit" not in df.columns:
        return df
    df = df.copy()
    duplicated = df["code_produit"].duplicated(keep=False)
    if not duplicated.any():
        return df
    counters = {}
    changed = 0
    for index, row in df[duplicated].iterrows():
        code = str(row["code_produit"]).strip()
        counters[code] = counters.get(code, 0) + 1
        if counters[code] == 1:
            continue
        suffix = row.get("produit_id", counters[code])
        df.at[index, "code_produit"] = f"{code}_{suffix}"
        changed += 1
    if changed:
        logger.warning(f"dim_produits : {changed} code_produit doublon(s) renomme(s) automatiquement")
    return df

def convert_column(df, column, sql_type):
    """Convertit une colonne selon son type PostgreSQL."""
    if column not in df.columns:
        return df
    sql_type = sql_type.upper()
    if any(t in sql_type for t in ["NUMERIC", "DECIMAL", "DOUBLE", "REAL", "FLOAT"]):
        df[column] = df[column].apply(clean_numeric_value)
    elif any(t in sql_type for t in ["INTEGER", "BIGINT", "SMALLINT", "SERIAL"]):
        df[column] = pd.to_numeric(df[column], errors="coerce").round().astype("Int64")
    elif "DATE" in sql_type or "TIMESTAMP" in sql_type:
        df[column] = pd.to_datetime(df[column], dayfirst=True, errors="coerce")
        if "DATE" in sql_type and "TIMESTAMP" not in sql_type:
            df[column] = df[column].dt.date
    elif "BOOL" in sql_type:
        mapping = {"TRUE": True, "FALSE": False, "YES": True, "NO": False, "OUI": True, "NON": False, "Y": True, "N": False, "1": True, "0": False, "T": True, "F": False}
        df[column] = df[column].astype(str).str.strip().str.upper().map(mapping)
    return df

def prepare_dataframe(df, table_name, schema):
    """Prepare un DataFrame pour PostgreSQL."""
    df = normalize_column_names(df)
    table_schema = schema[table_name]
    sql_columns = list(table_schema.keys())
    for column in sql_columns:
        if column not in df.columns:
            df[column] = None
    df = df[[col for col in sql_columns if col in df.columns]]
    for column, info in table_schema.items():
        df = convert_column(df, column, info["type"])
    df = replace_null_values(df)
    df = fill_table_defaults(df, table_name)
    df = df.dropna(how="all").drop_duplicates()
    pk_columns = [col for col, info in table_schema.items() if info["primary_key"]]
    if pk_columns:
        df = df.dropna(subset=pk_columns)
    required = [col for col, info in table_schema.items() if not info["nullable"] and not info["primary_key"]]
    if required:
        df = df.dropna(subset=[col for col in required if col in df.columns])
    if pk_columns:
        before = len(df)
        df = df.drop_duplicates(subset=pk_columns, keep="first")
        removed = before - len(df)
        if removed:
            logger.warning(f"{table_name} : {removed} doublon(s) supprime(s) sur cle primaire {pk_columns}")
    df = apply_business_filters(df, table_name)
    return df.where(pd.notnull(df), None)

# ============================================================
# 5. VALIDATION
# ============================================================

def validate_csv_file(table_name):
    """Verifie l'existence du fichier CSV."""
    csv_path = get_csv_path(table_name)
    if not csv_path.exists():
        logger.error(f"CSV absent : {csv_path}")
        return False
    return True

def validate_dataframe(df, table_name, schema):
    """Valide le DataFrame avant import."""
    if df.empty:
        logger.warning(f"{table_name} : fichier vide.")
        return False
    table_schema = schema[table_name]
    required = [col for col, info in table_schema.items() if not info["nullable"] and not info["primary_key"]]
    missing_required = [col for col in required if col in df.columns and df[col].isna().any()]
    if missing_required:
        logger.warning(f"{table_name} : valeurs nulles dans colonnes obligatoires {missing_required}")
    pk_columns = [col for col, info in table_schema.items() if info["primary_key"]]
    if pk_columns and df.duplicated(subset=pk_columns).any():
        logger.error(f"{table_name} : doublons detectes sur cle primaire {pk_columns}")
        return False
    return True

# ============================================================
# 6. IMPORT POSTGRESQL
# ============================================================

def import_dataframe(df, table_name):
    """Importe un DataFrame dans PostgreSQL."""
    try:
        ensure_dim_date_rows(df, table_name)
        with engine.begin() as connection:
            df.to_sql(table_name, connection, if_exists="append", index=False, method="multi", chunksize=1000)
        logger.info(f"{table_name} : {len(df)} ligne(s) importee(s).")
        return True, len(df)
    except Exception as error:
        logger.exception(f"Erreur import {table_name} : {error}")
        return False, 0

def ensure_dim_date_rows(df, table_name):
    """Ajoute automatiquement dans dim_date les date_id manquantes utilisees par les faits."""
    if table_name == "dim_date" or "date_id" not in df.columns or df.empty:
        return
    dates = pd.to_datetime(df["date_id"], errors="coerce").dropna().dt.date.unique()
    if len(dates) == 0:
        return
    rows = []
    with engine.begin() as connection:
        for value in dates:
            exists = connection.execute(text("SELECT 1 FROM dim_date WHERE date_id=:date_id"), {"date_id": value}).first()
            if exists:
                continue
            rows.append({
                "date_id": value,
                "jour": value.day,
                "mois": value.month,
                "annee": value.year,
                "trimestre": f"T{(value.month - 1) // 3 + 1}",
                "nom_mois": value.strftime("%B")
            })
        if rows:
            pd.DataFrame(rows).to_sql("dim_date", connection, if_exists="append", index=False, method="multi")
            logger.info(f"dim_date : {len(rows)} date(s) manquante(s) ajoutee(s) automatiquement.")

def import_table(table_name, schema=None):
    """Importe une table depuis son CSV."""
    schema = schema or get_database_schema()
    if table_name not in schema:
        logger.error(f"Schema introuvable pour {table_name}.")
        return False, 0
    if not validate_csv_file(table_name):
        return False, 0
    csv_path = get_csv_path(table_name)
    logger.info(f"Import {table_name} depuis {csv_path.name}")
    df = read_csv_file(csv_path)
    df = prepare_dataframe(df, table_name, schema)
    if not validate_dataframe(df, table_name, schema):
        return False, 0
    return import_dataframe(df, table_name)

def truncate_tables():
    """Vide les 13 tables avant import."""
    tables = ",".join(reversed(CSV_IMPORT_ORDER))
    query = f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"
    try:
        with engine.begin() as connection:
            connection.execute(text(query))
        logger.info("Tables videes avec succes.")
        return True
    except SQLAlchemyError as error:
        logger.exception(f"Erreur TRUNCATE : {error}")
        return False

def reset_sequences():
    """Synchronise les sequences SERIAL apres import."""
    id_columns = {
        "dim_categories": "categorie_id",
        "dim_produits": "produit_id",
        "dim_acheteurs": "acheteur_id",
        "dim_vendeurs": "vendeur_id",
        "fact_achats": "achat_id",
        "dim_lignes_achat": "ligne_achat_id",
        "fact_ventes": "vente_id",
        "dim_lignes_vente": "ligne_vente_id",
        "fact_depenses": "depense_id",
        "dim_pertes": "perte_id",
        "fact_tresorerie": "mouvement_id",
        "fact_inventaire": "inventaire_id"
    }
    try:
        with engine.begin() as connection:
            for table, id_col in id_columns.items():
                if table_exists(table):
                    query = text(f"SELECT setval(pg_get_serial_sequence('{table}','{id_col}'),COALESCE((SELECT MAX({id_col}) FROM {table}),1),true)")
                    connection.execute(query)
        logger.info("Sequences synchronisees.")
        return True
    except SQLAlchemyError as error:
        logger.exception(f"Erreur reset sequences : {error}")
        return False

def synchronize_stock_actuel():
    """Recalcule le stock actuel depuis achats, ventes et pertes importes."""
    query = """
    UPDATE dim_produits p
    SET stock_actuel = GREATEST(COALESCE(a.qte_achat,0)-COALESCE(v.qte_vente,0)-COALESCE(pe.qte_perte,0),0)
    FROM dim_produits base
    LEFT JOIN (
        SELECT produit_id,SUM(quantite_achat)::INTEGER AS qte_achat
        FROM dim_lignes_achat GROUP BY produit_id
    ) a ON a.produit_id=base.produit_id
    LEFT JOIN (
        SELECT produit_id,SUM(qte_vente)::INTEGER AS qte_vente
        FROM dim_lignes_vente GROUP BY produit_id
    ) v ON v.produit_id=base.produit_id
    LEFT JOIN (
        SELECT produit_id,SUM(qte_perte)::INTEGER AS qte_perte
        FROM dim_pertes GROUP BY produit_id
    ) pe ON pe.produit_id=base.produit_id
    WHERE p.produit_id=base.produit_id
    """
    try:
        with engine.begin() as connection:
            result = connection.execute(text(query))
        logger.info(f"Stock actuel synchronise : {result.rowcount} produit(s).")
        return True
    except SQLAlchemyError as error:
        logger.exception(f"Erreur synchronisation stock : {error}")
        return False

# ============================================================
# 7. IMPORT COMPLET ET RAPPORT
# ============================================================

def import_all_tables(clean_before=True, reset_seq=True):
    """Importe tous les CSV selon l'ordre des cles etrangeres."""
    start = time.perf_counter()
    IMPORT_RESULTS["success"].clear()
    IMPORT_RESULTS["failed"].clear()
    IMPORT_RESULTS["rows"] = 0
    logger.info("=" * 70)
    logger.info("DEBUT IMPORT CSV - GESTION DE SUPERETTE")
    logger.info("=" * 70)
    if not CSV_DIR.exists():
        raise FileNotFoundError(f"Dossier CSV introuvable : {CSV_DIR}")
    if not test_connection():
        raise ConnectionError("Connexion PostgreSQL impossible.")
    schema = get_database_schema()
    if clean_before and not truncate_tables():
        raise RuntimeError("Impossible de vider les tables avant import.")
    for index, table in enumerate(CSV_IMPORT_ORDER, start=1):
        table_start = time.perf_counter()
        logger.info(f"[{index}/{len(CSV_IMPORT_ORDER)}] {table}")
        success, rows = import_table(table, schema)
        duration = time.perf_counter() - table_start
        if success:
            IMPORT_RESULTS["success"].append(table)
            IMPORT_RESULTS["rows"] += rows
            logger.info(f"OK {table} : {rows} ligne(s), {duration:.2f}s")
        else:
            IMPORT_RESULTS["failed"].append(table)
            logger.error(f"ECHEC {table} : {duration:.2f}s")
    if reset_seq:
        reset_sequences()
    synchronize_stock_actuel()
    result = {
        "tables": len(CSV_IMPORT_ORDER),
        "success": len(IMPORT_RESULTS["success"]),
        "failed": len(IMPORT_RESULTS["failed"]),
        "failed_tables": IMPORT_RESULTS["failed"],
        "rows": IMPORT_RESULTS["rows"],
        "duration": time.perf_counter() - start
    }
    final_report(result)
    return result

def final_report(result):
    """Affiche le rapport final."""
    logger.info("=" * 70)
    logger.info("RAPPORT FINAL IMPORT CSV")
    logger.info("=" * 70)
    logger.info(f"Tables prevues : {result['tables']}")
    logger.info(f"Tables OK      : {result['success']}")
    logger.info(f"Tables erreur  : {result['failed']}")
    logger.info(f"Lignes import  : {result['rows']}")
    logger.info(f"Duree totale   : {result['duration']:.2f}s")
    if result["failed_tables"]:
        logger.warning(f"Tables en erreur : {result['failed_tables']}")
    logger.info("IMPORT TERMINE AVEC SUCCES" if result["failed"] == 0 else "IMPORT TERMINE AVEC ERREURS")
    logger.info("=" * 70)

# ============================================================
# 8. EXECUTION DIRECTE
# ============================================================

if __name__ == "__main__":
    import_all_tables(clean_before=True, reset_seq=True)

