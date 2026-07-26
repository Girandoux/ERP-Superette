# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : database_utils.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import logging
import re
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config.database import (
    execute_query,
    fetch_all,
    fetch_one,
    get_engine,
    read_sql_dataframe,
    test_connection,
)
from config.settings import LOGS_DIR


# ============================================================
# 1. CONFIGURATION GENERALE
# ============================================================

engine = get_engine()

LOGS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

logger = logging.getLogger(
    "database"
)

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    console_handler = logging.StreamHandler()

    file_handler = logging.FileHandler(
        LOGS_DIR / "database.log",
        encoding="utf-8",
    )

    console_handler.setFormatter(
        formatter
    )

    file_handler.setFormatter(
        formatter
    )

    logger.setLevel(
        logging.INFO
    )

    logger.addHandler(
        console_handler
    )

    logger.addHandler(
        file_handler
    )

logger.propagate = False

MAIN_TABLES = [
    "dim_date",
    "dim_categories",
    "dim_produits",
    "dim_acheteurs",
    "dim_vendeurs",
    "fact_achats",
    "dim_lignes_achat",
    "fact_ventes",
    "dim_lignes_vente",
    "fact_depenses",
    "dim_pertes",
    "fact_tresorerie",
    "fact_inventaire",
]

SQL_NAME_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*$"
)


# ============================================================
# 2. VALIDATION DES TABLES ET COLONNES
# ============================================================

def table_exists(table_name):
    """Verifie si une table ou une vue existe dans le schema public."""
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = :table_name

            UNION ALL

            SELECT 1
            FROM information_schema.views
            WHERE table_schema = 'public'
              AND table_name = :table_name
        ) AS exists;
    """

    result = fetch_one(
        query,
        {
            "table_name": table_name,
        },
    )

    return bool(
        result
        and result.get("exists")
    )


def check_connection():
    """Verifie que PostgreSQL repond correctement."""
    is_ok = test_connection()

    if is_ok:
        logger.info(
            "Connexion PostgreSQL valide."
        )

    else:
        logger.error(
            "Connexion PostgreSQL impossible."
        )

    return is_ok


def get_table_columns(table_name):
    """Retourne les colonnes d'une table ou d'une vue."""
    query = """
        SELECT
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = :table_name
        ORDER BY ordinal_position;
    """

    return fetch_all(
        query,
        {
            "table_name": table_name,
        },
    )


def get_column_names(table_name):
    """Retourne uniquement les noms des colonnes."""
    return [
        column["column_name"]
        for column in get_table_columns(table_name)
    ]


def validate_sql_name(name):
    """Verifie qu'un nom SQL est correctement forme."""
    if not isinstance(name, str):
        raise TypeError(
            "Le nom SQL doit etre une chaine de caracteres."
        )

    name = name.strip()

    if not SQL_NAME_PATTERN.fullmatch(name):
        raise ValueError(
            f"Nom SQL invalide : {name}"
        )

    return name


def validate_table_name(table_name):
    """Verifie le nom et l'existence d'une table ou d'une vue."""
    safe_table_name = validate_sql_name(
        table_name
    )

    if not table_exists(
        safe_table_name
    ):
        raise ValueError(
            f"La table ou la vue '{safe_table_name}' n'existe pas."
        )

    return safe_table_name


def validate_column_name(table_name, column_name):
    """Verifie qu'une colonne existe dans une table."""
    safe_column_name = validate_sql_name(
        column_name
    )

    if safe_column_name not in get_column_names(
        table_name
    ):
        raise ValueError(
            f"Colonne '{safe_column_name}' invalide pour {table_name}."
        )

    return safe_column_name


def validate_columns(table_name, data):
    """Verifie que les colonnes fournies existent dans la table."""
    if not isinstance(data, dict):
        raise TypeError(
            "Les donnees doivent etre fournies sous forme de dictionnaire."
        )

    table_columns = set(
        get_column_names(table_name)
    )

    invalid_columns = [
        column
        for column in data
        if column not in table_columns
    ]

    if invalid_columns:
        raise ValueError(
            f"Colonnes invalides pour {table_name} : "
            f"{invalid_columns}"
        )

    return True


def build_order_by(table_name, order_by):
    """Valide une clause ORDER BY simple."""
    if not order_by:
        return ""

    parts = order_by.strip().split()

    if len(parts) > 2:
        raise ValueError(
            "La clause ORDER BY est invalide."
        )

    column_name = validate_column_name(
        table_name,
        parts[0],
    )

    direction = ""

    if len(parts) == 2:
        direction = parts[1].upper()

        if direction not in (
            "ASC",
            "DESC",
        ):
            raise ValueError(
                "Le tri doit etre ASC ou DESC."
            )

    return (
        f' ORDER BY "{column_name}"'
        f"{f' {direction}' if direction else ''}"
    )


# ============================================================
# 3. LECTURE DES DONNEES
# ============================================================

def get_all(
    table_name,
    order_by=None,
    limit=None,
):
    """Lit toutes les lignes d'une table ou d'une vue."""
    safe_table_name = validate_table_name(
        table_name
    )

    query = (
        f'SELECT * FROM "{safe_table_name}"'
    )

    query += build_order_by(
        safe_table_name,
        order_by,
    )

    if limit is not None:
        query += " LIMIT :limit"

        return read_sql_dataframe(
            query,
            {
                "limit": max(
                    int(limit),
                    0,
                ),
            },
        )

    return read_sql_dataframe(
        query
    )


def get_by_id(
    table_name,
    id_column,
    record_id,
):
    """Retourne une ligne par son identifiant."""
    safe_table_name = validate_table_name(
        table_name
    )

    safe_id_column = validate_column_name(
        safe_table_name,
        id_column,
    )

    query = (
        f'SELECT * FROM "{safe_table_name}" '
        f'WHERE "{safe_id_column}" = :record_id'
    )

    return fetch_one(
        query,
        {
            "record_id": record_id,
        },
    )


def get_where(
    table_name,
    conditions=None,
    order_by=None,
    limit=None,
):
    """Lit les lignes selon des conditions simples."""
    safe_table_name = validate_table_name(
        table_name
    )

    conditions = conditions or {}

    validate_columns(
        safe_table_name,
        conditions,
    )

    query = (
        f'SELECT * FROM "{safe_table_name}"'
    )

    if conditions:
        where_clause = " AND ".join(
            f'"{column}" = :{column}'
            for column in conditions
        )

        query += (
            f" WHERE {where_clause}"
        )

    query += build_order_by(
        safe_table_name,
        order_by,
    )

    parameters = dict(
        conditions
    )

    if limit is not None:
        parameters["limit"] = max(
            int(limit),
            0,
        )

        query += " LIMIT :limit"

    return read_sql_dataframe(
        query,
        parameters,
    )


def search_text(
    table_name,
    column_name,
    search_value,
    order_by=None,
    limit=100,
):
    """Recherche un texte sans tenir compte de la casse."""
    safe_table_name = validate_table_name(
        table_name
    )

    safe_column_name = validate_column_name(
        safe_table_name,
        column_name,
    )

    query = (
        f'SELECT * FROM "{safe_table_name}" '
        f'WHERE "{safe_column_name}" ILIKE :search_value'
    )

    query += build_order_by(
        safe_table_name,
        order_by,
    )

    query += " LIMIT :limit"

    return read_sql_dataframe(
        query,
        {
            "search_value": f"%{search_value}%",
            "limit": max(
                int(limit),
                0,
            ),
        },
    )


def count_records(
    table_name,
    conditions=None,
):
    """Compte les lignes avec des conditions optionnelles."""
    safe_table_name = validate_table_name(
        table_name
    )

    conditions = conditions or {}

    validate_columns(
        safe_table_name,
        conditions,
    )

    query = (
        f'SELECT COUNT(*) AS total FROM "{safe_table_name}"'
    )

    if conditions:
        where_clause = " AND ".join(
            f'"{column}" = :{column}'
            for column in conditions
        )

        query += (
            f" WHERE {where_clause}"
        )

    result = fetch_one(
        query,
        conditions,
    )

    return result.get(
        "total",
        0,
    ) if result else 0


def get_scalar(
    query,
    parameters=None,
):
    """Retourne une valeur unique comme COUNT, SUM, MAX ou MIN."""
    try:
        with engine.connect() as connection:
            return connection.execute(
                text(query),
                parameters or {},
            ).scalar()

    except SQLAlchemyError as error:
        log_database_error(
            error
        )

        return None


def record_exists(
    query,
    parameters=None,
):
    """Verifie si une requete retourne au moins une ligne."""
    return fetch_one(
        query,
        parameters or {},
    ) is not None


# ============================================================
# 4. INSERTION DES DONNEES
# ============================================================

def insert_record(
    table_name,
    data,
    returning="*",
):
    """Insere une ligne et retourne la ligne creee."""
    safe_table_name = validate_table_name(
        table_name
    )

    if not data:
        raise ValueError(
            "Aucune donnee a inserer."
        )

    validate_columns(
        safe_table_name,
        data,
    )

    columns = ", ".join(
        f'"{column}"'
        for column in data
    )

    values = ", ".join(
        f":{column}"
        for column in data
    )

    if returning == "*":
        returning_clause = "*"

    else:
        returning_column = validate_column_name(
            safe_table_name,
            returning,
        )

        returning_clause = (
            f'"{returning_column}"'
        )

    query = (
        f'INSERT INTO "{safe_table_name}" '
        f"({columns}) "
        f"VALUES ({values}) "
        f"RETURNING {returning_clause}"
    )

    try:
        with engine.begin() as connection:
            row = (
                connection.execute(
                    text(query),
                    data,
                )
                .mappings()
                .first()
            )

        logger.info(
            "Insertion reussie dans %s.",
            safe_table_name,
        )

        return dict(row) if row else None

    except SQLAlchemyError as error:
        log_database_error(
            error
        )

        return None


def insert_many(
    table_name,
    rows,
):
    """Insere plusieurs lignes avec SQLAlchemy."""
    safe_table_name = validate_table_name(
        table_name
    )

    if not rows:
        return 0

    first_columns = set(
        rows[0].keys()
    )

    for row in rows:
        if set(row.keys()) != first_columns:
            raise ValueError(
                "Toutes les lignes doivent contenir les memes colonnes."
            )

        validate_columns(
            safe_table_name,
            row,
        )

    columns = ", ".join(
        f'"{column}"'
        for column in rows[0]
    )

    values = ", ".join(
        f":{column}"
        for column in rows[0]
    )

    query = text(
        f'INSERT INTO "{safe_table_name}" '
        f"({columns}) "
        f"VALUES ({values})"
    )

    try:
        with engine.begin() as connection:
            connection.execute(
                query,
                rows,
            )

        logger.info(
            "%s lignes inserees dans %s.",
            len(rows),
            safe_table_name,
        )

        return len(rows)

    except SQLAlchemyError as error:
        log_database_error(
            error
        )

        return 0


def insert_dataframe(
    table_name,
    dataframe,
    if_exists="append",
):
    """Insere un DataFrame dans une table."""
    safe_table_name = validate_table_name(
        table_name
    )

    if dataframe is None or dataframe.empty:
        return 0

    if if_exists not in (
        "append",
        "replace",
        "fail",
    ):
        raise ValueError(
            "if_exists doit etre append, replace ou fail."
        )

    try:
        dataframe.to_sql(
            safe_table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=1000,
        )

        logger.info(
            "%s lignes importees dans %s.",
            len(dataframe),
            safe_table_name,
        )

        return len(dataframe)

    except Exception as error:
        log_database_error(
            error
        )

        return 0


# ============================================================
# 5. MODIFICATION ET SUPPRESSION
# ============================================================

def update_record(
    table_name,
    id_column,
    record_id,
    data,
):
    """Modifie une ligne selon son identifiant."""
    safe_table_name = validate_table_name(
        table_name
    )

    safe_id_column = validate_column_name(
        safe_table_name,
        id_column,
    )

    if not data:
        return False

    validate_columns(
        safe_table_name,
        data,
    )

    set_clause = ", ".join(
        f'"{column}" = :{column}'
        for column in data
    )

    parameters = dict(
        data
    )

    parameters["record_id"] = record_id

    query = (
        f'UPDATE "{safe_table_name}" '
        f"SET {set_clause} "
        f'WHERE "{safe_id_column}" = :record_id'
    )

    return execute_query(
        query,
        parameters,
    )


def delete_record(
    table_name,
    id_column,
    record_id,
):
    """Supprime une ligne selon son identifiant."""
    safe_table_name = validate_table_name(
        table_name
    )

    safe_id_column = validate_column_name(
        safe_table_name,
        id_column,
    )

    query = (
        f'DELETE FROM "{safe_table_name}" '
        f'WHERE "{safe_id_column}" = :record_id'
    )

    return execute_query(
        query,
        {
            "record_id": record_id,
        },
    )


def execute_transaction(sql_list):
    """Execute plusieurs requetes dans une seule transaction."""
    if not sql_list:
        return False

    try:
        with engine.begin() as connection:
            for query, parameters in sql_list:
                connection.execute(
                    text(query),
                    parameters or {},
                )

        logger.info(
            "Transaction validee."
        )

        return True

    except SQLAlchemyError as error:
        log_database_error(
            error
        )

        return False


def soft_delete_product(produit_id):
    """Desactive un produit sans le supprimer."""
    return update_record(
        "dim_produits",
        "produit_id",
        produit_id,
        {
            "actif": False,
        },
    )


def activate_product(produit_id):
    """Reactive un produit."""
    return update_record(
        "dim_produits",
        "produit_id",
        produit_id,
        {
            "actif": True,
        },
    )


# ============================================================
# 6. REQUETES ET VUES
# ============================================================

def read_view(
    view_name,
    order_by=None,
    limit=None,
):
    """Lit une vue SQL."""
    return get_all(
        view_name,
        order_by=order_by,
        limit=limit,
    )


def run_select(
    query,
    parameters=None,
):
    """Execute une requete SELECT et retourne un DataFrame."""
    return read_sql_dataframe(
        query,
        parameters or {},
    )


def run_action(
    query,
    parameters=None,
):
    """Execute une requete d'action."""
    return execute_query(
        query,
        parameters or {},
    )


def get_dashboard_global():
    """Retourne les KPI globaux si la vue existe."""
    if table_exists(
        "vw_dashboard_global"
    ):
        return fetch_one(
            "SELECT * FROM vw_dashboard_global"
        )

    return {}


# ============================================================
# 7. CONTROLES ET MAINTENANCE
# ============================================================

def count_main_tables():
    """Compte les lignes des 13 tables principales."""
    return {
        table: count_records(table)
        for table in MAIN_TABLES
        if table_exists(table)
    }


def truncate_table(
    table_name,
    restart_identity=True,
    cascade=True,
):
    """Vide une table. A utiliser avec prudence."""
    safe_table_name = validate_table_name(
        table_name
    )

    query = (
        f'TRUNCATE TABLE "{safe_table_name}"'
    )

    if restart_identity:
        query += " RESTART IDENTITY"

    if cascade:
        query += " CASCADE"

    return execute_query(
        query
    )


def reset_sequence(
    table_name,
    id_column,
):
    """Synchronise une sequence SERIAL apres import CSV."""
    safe_table_name = validate_table_name(
        table_name
    )

    safe_id_column = validate_column_name(
        safe_table_name,
        id_column,
    )

    query = """
        SELECT setval(
            pg_get_serial_sequence(
                :table_name,
                :id_column
            ),
            COALESCE(
                (
                    SELECT MAX("{id_column}")
                    FROM "{table_name}"
                ),
                1
            ),
            true
        );
    """.format(
        table_name=safe_table_name,
        id_column=safe_id_column,
    )

    return execute_query(
        query,
        {
            "table_name": safe_table_name,
            "id_column": safe_id_column,
        },
    )


def database_health_check():
    """Retourne un controle rapide des tables principales."""
    existing_tables = [
        table
        for table in MAIN_TABLES
        if table_exists(table)
    ]

    missing_tables = [
        table
        for table in MAIN_TABLES
        if table not in existing_tables
    ]

    return {
        "tables_existantes": existing_tables,
        "tables_manquantes": missing_tables,
        "lignes": count_main_tables(),
    }


def database_version():
    """Retourne la version de PostgreSQL."""
    value = get_scalar(
        "SELECT version()"
    )

    return (
        value
        if value
        else "Version inconnue"
    )


def database_info():
    """Retourne des informations utiles sur PostgreSQL."""
    return {
        "postgres_version": database_version(),
        "engine": engine.name,
        "driver": engine.driver,
        "url": engine.url.render_as_string(
            hide_password=True
        ),
    }


def log_database_error(error):
    """Journalise une erreur PostgreSQL."""
    logger.error(
        "=" * 70
    )

    logger.exception(
        "%s",
        error,
    )

    logger.error(
        "=" * 70
    )


# ============================================================
# 8. EXPORT SIMPLE
# ============================================================

def export_query_to_csv(
    query,
    output_path,
    parameters=None,
):
    """Exporte le resultat d'une requete vers CSV."""
    dataframe = run_select(
        query,
        parameters or {},
    )

    if dataframe.empty:
        return False

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
    )

    return True


def export_table_to_csv(
    table_name,
    output_path,
):
    """Exporte une table ou une vue vers CSV."""
    dataframe = get_all(
        table_name
    )

    if dataframe.empty:
        return False

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        path,
        index=False,
        encoding="utf-8-sig",
    )

    return True


# ============================================================
# 9. ALIASES COMPATIBLES AVEC LES FUTURS MODULES
# ============================================================

read_dataframe = read_sql_dataframe
write_dataframe = insert_dataframe
count_rows = count_records


# ============================================================
# FIN DU FICHIER
# ============================================================

