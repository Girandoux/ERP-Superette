# ============================================================
# PROJET : GESTION DE SUPERETTE
# MODULE DATABASE
#
# FICHIER : run_import.py
#
# DESCRIPTION :
# Fonctions d'acces aux donnees PostgreSQL utilisees par
# l'application Streamlit Gestion de Superette.
# ============================================================

import argparse
import logging
import sys
import time
from config.database import test_connection, database_information
from config.settings import APP_NAME, CSV_DIR, LOGS_DIR
from database.import_csv import import_all_tables

# ============================================================
# 1. CONFIGURATION LOGGING
# ============================================================

LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "import.log"
logger = logging.getLogger("run_import")
if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
logger.propagate = False

# ============================================================
# 2. AFFICHAGE
# ============================================================

def separator():
    """Affiche une separation."""
    logger.info("=" * 70)

def title(text):
    """Affiche un titre."""
    separator()
    logger.info(text)
    separator()

def show_start_info(clean_before, reset_seq):
    """Affiche les informations de demarrage."""
    info = database_information()
    title(f"{APP_NAME} - IMPORT CSV")
    logger.info(f"Base PostgreSQL : {info['database']}")
    logger.info(f"Serveur         : {info['host']}:{info['port']}")
    logger.info(f"Utilisateur     : {info['user']}")
    logger.info(f"Dossier CSV     : {CSV_DIR}")
    logger.info(f"Nettoyage avant : {'Oui' if clean_before else 'Non'}")
    logger.info(f"Reset sequences : {'Oui' if reset_seq else 'Non'}")

# ============================================================
# 3. ARGUMENTS CLI
# ============================================================

def parse_arguments():
    """Lit les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Import CSV vers PostgreSQL pour Gestion de Superette.")
    parser.add_argument("--no-clean", action="store_true", help="Ne vide pas les tables avant import.")
    parser.add_argument("--no-reset", action="store_true", help="Ne synchronise pas les sequences apres import.")
    return parser.parse_args()

# ============================================================
# 4. EXECUTION PRINCIPALE
# ============================================================

def run_import(clean_before=True, reset_seq=True):
    """Lance l'import complet."""
    start = time.perf_counter()
    show_start_info(clean_before, reset_seq)
    title("VERIFICATION POSTGRESQL")
    if not test_connection():
        raise ConnectionError("Connexion PostgreSQL impossible.")
    logger.info("Connexion PostgreSQL reussie.")
    title("IMPORT DES FICHIERS CSV")
    result = import_all_tables(clean_before=clean_before, reset_seq=reset_seq)
    elapsed = time.perf_counter() - start
    title("RAPPORT GENERAL")
    logger.info(f"Tables prevues : {result['tables']}")
    logger.info(f"Tables OK      : {result['success']}")
    logger.info(f"Tables erreur  : {result['failed']}")
    logger.info(f"Lignes import  : {result['rows']}")
    logger.info(f"Duree import   : {result['duration']:.2f}s")
    logger.info(f"Duree totale   : {elapsed:.2f}s")
    if result["failed_tables"]:
        logger.warning(f"Tables en erreur : {result['failed_tables']}")
    separator()
    return result

# ============================================================
# 5. PROGRAMME PRINCIPAL
# ============================================================

def main():
    """Point d'entree CLI."""
    args = parse_arguments()
    clean_before = not args.no_clean
    reset_seq = not args.no_reset
    try:
        result = run_import(clean_before=clean_before, reset_seq=reset_seq)
        if result["failed"] > 0:
            logger.error("Import termine avec erreurs.")
            return 1
        logger.info("Import termine avec succes.")
        return 0
    except KeyboardInterrupt:
        logger.error("Import interrompu par l'utilisateur.")
        return 1
    except Exception as error:
        title("ERREUR CRITIQUE")
        logger.exception(error)
        return 1

if __name__ == "__main__":
    sys.exit(main())

