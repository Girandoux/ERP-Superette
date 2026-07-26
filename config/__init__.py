# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : config/__init__.py
# AUTEUR : Girandoux Fandio
# DESCRIPTION : Initialisation du package config.
# ============================================================

from config.settings import (
    APP_NAME,
    APP_ENV,
    DEBUG,
    APP_VERSION,
    APP_AUTHOR,
    APP_YEAR,
    BASE_DIR,
    DATABASE_URL,
    get_database_url,
    get_project_path,
    create_required_dirs,
    is_development
)

__all__ = [
    "APP_NAME",
    "APP_ENV",
    "DEBUG",
    "APP_VERSION",
    "APP_AUTHOR",
    "APP_YEAR",
    "BASE_DIR",
    "DATABASE_URL",
    "get_database_url",
    "get_project_path",
    "create_required_dirs",
    "is_development"
]
