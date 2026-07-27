# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : config/settings.py
# AUTEUR : Girandoux Fandio
# DESCRIPTION : Parametres generaux du projet, chemins,
# configuration PostgreSQL, SQLAlchemy et Streamlit.
# ============================================================

import os
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


# ============================================================
# 1. CHARGEMENT DU FICHIER .ENV
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


# ============================================================
# 2. FONCTIONS DE LECTURE DES VARIABLES .ENV
# ============================================================

def get_bool_env(variable_name, default=False):
    """Convertit une variable d'environnement en booleen."""
    default_value = "true" if default else "false"
    value = os.getenv(variable_name, default_value)

    return value.strip().lower() in (
        "true",
        "1",
        "yes",
        "oui",
    )


def get_int_env(variable_name, default):
    """Convertit une variable d'environnement en entier."""
    try:
        return int(os.getenv(variable_name, str(default)))
    except (TypeError, ValueError):
        return default


# ============================================================
# 3. INFORMATIONS GENERALES DE L'APPLICATION
# ============================================================

APP_NAME = os.getenv("APP_NAME", "Gestion Superette")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = get_bool_env("DEBUG", True)

APP_VERSION = "1.0.0"
APP_AUTHOR = "Girandoux Fandio"
APP_YEAR = str(date.today().year)


# ============================================================
# 4. CHEMINS PRINCIPAUX DU PROJET
# ============================================================

CONFIG_DIR = BASE_DIR / "config"
DATABASE_DIR = BASE_DIR / "database"
SQL_DIR = BASE_DIR / "sql"
DATA_DIR = BASE_DIR / "data"
CSV_DIR = DATA_DIR / "raw" / "csv"
EXCEL_DIR = DATA_DIR / "raw" / "excel"
PAGES_DIR = BASE_DIR / "streamlit" / "pages"
UTILS_DIR = BASE_DIR / "utils"
POWERBI_DIR = BASE_DIR / "powerbi"
REPORTS_DIR = BASE_DIR / "reports"
IMAGES_DIR = BASE_DIR / "images"
DOCS_DIR = BASE_DIR / "docs"
LOGS_DIR = BASE_DIR / "logs"
TESTS_DIR = BASE_DIR / "tests"
STREAMLIT_DIR = BASE_DIR / ".streamlit"


# ============================================================
# 5. CHEMINS DES RAPPORTS
# ============================================================

REPORTS_PDF_DIR = REPORTS_DIR / "pdf"
REPORTS_EXCEL_DIR = REPORTS_DIR / "excel"
REPORTS_CSV_DIR = REPORTS_DIR / "csv"
REPORTS_IMAGES_DIR = REPORTS_DIR / "images"


# ============================================================
# 6. CHEMINS DES IMAGES
# ============================================================

LOGO_PATH = IMAGES_DIR / "logo.png"
BANNER_PATH = IMAGES_DIR / "banner.png"
FAVICON_PATH = IMAGES_DIR / "favicon.ico"


# ============================================================
# 7. CONFIGURATION POSTGRESQL
# ============================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "Superette")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Encodage utile si le mot de passe contient des caracteres speciaux.
DB_USER_ENCODED = quote_plus(DB_USER)
DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

DEFAULT_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER_ENCODED}:"
    f"{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_DATABASE_URL,
)


# ============================================================
# 8. CONFIGURATION AUTHENTIFICATION SIMPLE V1
# ============================================================

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
SESSION_TIMEOUT_MINUTES = get_int_env(
    "SESSION_TIMEOUT_MINUTES",
    60,
)


# ============================================================
# 9. CONFIGURATION STREAMLIT
# ============================================================

PAGE_TITLE = "Gestion de Superette"
PAGE_ICON = "🏪"
PAGE_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"


# ============================================================
# 10. FICHIERS CSV ATTENDUS
# ============================================================

CSV_FILES = {
    "dim_date": CSV_DIR / "dim_date.csv",
    "dim_categories": CSV_DIR / "dim_categories.csv",
    "dim_produits": CSV_DIR / "dim_produits.csv",
    "dim_acheteurs": CSV_DIR / "dim_acheteurs.csv",
    "dim_vendeurs": CSV_DIR / "dim_vendeurs.csv",
    "fact_achats": CSV_DIR / "fact_achats.csv",
    "dim_lignes_achat": CSV_DIR / "dim_lignes_achat.csv",
    "fact_ventes": CSV_DIR / "fact_ventes.csv",
    "dim_lignes_vente": CSV_DIR / "dim_lignes_vente.csv",
    "fact_depenses": CSV_DIR / "fact_depenses.csv",
    "dim_pertes": CSV_DIR / "dim_pertes.csv",
    "fact_tresorerie": CSV_DIR / "fact_tresorerie.csv",
    "fact_inventaire": CSV_DIR / "fact_inventaire.csv",
}

CSV_IMPORT_ORDER = [
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


# ============================================================
# 11. FONCTIONS UTILITAIRES DE CONFIGURATION
# ============================================================

def get_database_url():
    """Retourne l'URL SQLAlchemy de connexion a PostgreSQL."""
    return DATABASE_URL


def get_project_path(*parts):
    """Construit un chemin absolu depuis la racine du projet."""
    return BASE_DIR.joinpath(*parts)


def create_required_dirs():
    """Cree les dossiers necessaires s'ils n'existent pas."""
    required_dirs = [
        CSV_DIR,
        EXCEL_DIR,
        REPORTS_PDF_DIR,
        REPORTS_EXCEL_DIR,
        REPORTS_CSV_DIR,
        REPORTS_IMAGES_DIR,
        IMAGES_DIR,
        DOCS_DIR,
        LOGS_DIR,
    ]

    for directory in required_dirs:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


def is_development():
    """Indique si l'application tourne en mode developpement."""
    return APP_ENV.strip().lower() == "development"

