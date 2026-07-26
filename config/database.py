# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : config/database.py
# AUTEUR : Girandoux Fandio
# DESCRIPTION : Connexion PostgreSQL avec SQLAlchemy, sessions,
# execution SQL et echanges avec Pandas.
# ============================================================

from contextlib import contextmanager
from pathlib import Path
import re

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from config.settings import (
    DATABASE_URL,
    DB_HOST,
    DB_NAME,
    DB_PORT,
    DB_USER,
)


# ============================================================
# 1. CREATION DU MOTEUR SQLALCHEMY
# ============================================================

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


# ============================================================
# 2. VALIDATION DES NOMS DE TABLES
# ============================================================

SQL_NAME_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*$"
)


def validate_sql_name(name):
    """Verifie qu'un nom de table ou de vue est valide."""
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


# ============================================================
# 3. ACCES AU MOTEUR ET AUX SESSIONS
# ============================================================

def get_engine():
    """Retourne le moteur SQLAlchemy."""
    return engine


def get_session():
    """Retourne une nouvelle session SQLAlchemy."""
    return SessionLocal()


@contextmanager
def session_scope():
    """Ouvre une session et gere automatiquement la transaction."""
    session = SessionLocal()

    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def get_connection():
    """Ouvre une connexion SQLAlchemy."""
    return engine.connect()


# ============================================================
# 4. TEST ET INFORMATIONS DE CONNEXION
# ============================================================

def test_connection():
    """Teste la connexion a PostgreSQL."""
    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return True

    except SQLAlchemyError as error:
        print("Erreur de connexion PostgreSQL")
        print(error)

        return False


def database_information():
    """Retourne les informations non sensibles de la base."""
    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "url_hidden": (
            f"postgresql+psycopg2://{DB_USER}:***@"
            f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
        ),
    }


def print_database_information():
    """Affiche les informations non sensibles de connexion."""
    info = database_information()

    print("=" * 60)
    print("POSTGRESQL - GESTION DE SUPERETTE")
    print("=" * 60)
    print(f"Serveur     : {info['host']}")
    print(f"Port        : {info['port']}")
    print(f"Base        : {info['database']}")
    print(f"Utilisateur : {info['user']}")
    print("=" * 60)


# ============================================================
# 5. EXECUTION SQL
# ============================================================

def execute_query(query, parameters=None):
    """Execute une requete INSERT, UPDATE, DELETE ou DDL."""
    try:
        with engine.begin() as connection:
            connection.execute(
                text(query),
                parameters or {},
            )

        return True

    except SQLAlchemyError as error:
        print("Erreur SQL dans execute_query")
        print(error)

        return False


def fetch_one(query, parameters=None):
    """Retourne une ligne sous forme de dictionnaire."""
    try:
        with engine.connect() as connection:
            row = (
                connection.execute(
                    text(query),
                    parameters or {},
                )
                .mappings()
                .first()
            )

        return dict(row) if row else None

    except SQLAlchemyError as error:
        print("Erreur SQL dans fetch_one")
        print(error)

        return None


def fetch_all(query, parameters=None):
    """Retourne plusieurs lignes sous forme de dictionnaires."""
    try:
        with engine.connect() as connection:
            rows = (
                connection.execute(
                    text(query),
                    parameters or {},
                )
                .mappings()
                .all()
            )

        return [
            dict(row)
            for row in rows
        ]

    except SQLAlchemyError as error:
        print("Erreur SQL dans fetch_all")
        print(error)

        return []


def execute_sql_file(file_path):
    """
    Execute un fichier SQL simple.

    Cette fonction ne doit pas etre utilisee pour les scripts
    contenant des commandes psql comme \copy.
    """
    path = Path(file_path)

    if not path.exists():
        print(f"Fichier SQL introuvable : {path}")
        return False

    try:
        sql_content = path.read_text(
            encoding="utf-8"
        )

        with engine.begin() as connection:
            connection.exec_driver_sql(
                sql_content
            )

        return True

    except Exception as error:
        print("Erreur execution fichier SQL")
        print(error)

        return False


# ============================================================
# 6. PANDAS ET DATAFRAMES
# ============================================================

def read_sql_dataframe(query, parameters=None):
    """Retourne le resultat SQL dans un DataFrame Pandas."""
    try:
        with engine.connect() as connection:
            return pd.read_sql(
                text(query),
                connection,
                params=parameters or {},
            )

    except Exception as error:
        print("Erreur lecture DataFrame")
        print(error)

        return pd.DataFrame()


def read_table_dataframe(table_name, limit=None):
    """Lit une table complete ou un nombre limite de lignes."""
    try:
        safe_table_name = validate_sql_name(
            table_name
        )

    except (TypeError, ValueError) as error:
        print(error)
        return pd.DataFrame()

    query = f'SELECT * FROM "{safe_table_name}"'

    if limit is not None:
        try:
            safe_limit = max(
                int(limit),
                0,
            )

        except (TypeError, ValueError):
            print("La limite doit etre un nombre entier.")
            return pd.DataFrame()

        query += f" LIMIT {safe_limit}"

    return read_sql_dataframe(
        query
    )


def write_dataframe(
    dataframe,
    table_name,
    if_exists="append",
):
    """Insere un DataFrame dans une table PostgreSQL."""
    if dataframe is None or dataframe.empty:
        print("Le DataFrame ne contient aucune donnee.")
        return False

    if if_exists not in (
        "append",
        "replace",
        "fail",
    ):
        print(
            f"Valeur if_exists invalide : {if_exists}"
        )
        return False

    try:
        safe_table_name = validate_sql_name(
            table_name
        )

        dataframe.to_sql(
            name=safe_table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=1000,
        )

        return True

    except Exception as error:
        print(
            f"Erreur import DataFrame vers {table_name}"
        )
        print(error)

        return False


# ============================================================
# 7. OUTILS DE CONTROLE DE LA BASE
# ============================================================

def table_exists(table_name):
    """Verifie si une table existe dans le schema public."""
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
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


def get_tables():
    """Retourne la liste des tables et vues du schema public."""
    query = """
        SELECT
            table_name,
            table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """

    return fetch_all(
        query
    )


def count_rows(table_name):
    """Compte les lignes d'une table."""
    try:
        safe_table_name = validate_sql_name(
            table_name
        )

    except (TypeError, ValueError) as error:
        print(error)
        return 0

    result = fetch_one(
        f'SELECT COUNT(*) AS total FROM "{safe_table_name}"'
    )

    return result.get(
        "total",
        0,
    ) if result else 0


def count_all_main_tables():
    """Compte les lignes des 13 tables principales."""
    tables = [
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

    return {
        table_name: count_rows(table_name)
        for table_name in tables
        if table_exists(table_name)
    }


# ============================================================
# 8. EXECUTION DIRECTE DU FICHIER
# ============================================================

if __name__ == "__main__":
    print_database_information()

    if test_connection():
        print("Connexion PostgreSQL reussie.")
        print(
            read_sql_dataframe(
                "SELECT NOW() AS date_serveur"
            )
        )

    else:
        print("Connexion PostgreSQL impossible.")
