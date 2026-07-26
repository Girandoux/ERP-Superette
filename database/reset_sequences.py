# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : database/reset_sequences.py
# AUTEUR : Girandoux Fandio
# DESCRIPTION : Synchronisation des sequences PostgreSQL apres
# import CSV ou insertion manuelle des identifiants.
# ============================================================

import logging
import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config.database import get_engine, test_connection
from config.settings import LOGS_DIR


# ============================================================
# 1. CONFIGURATION DU MODULE
# ============================================================

engine = get_engine()

LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "database.log"

logger = logging.getLogger("reset_sequences")

if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

logger.propagate = False

SERIAL_TABLES = {
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
    "fact_inventaire": "inventaire_id",
}


# ============================================================
# 2. OUTILS D'AFFICHAGE
# ============================================================

def separator():
    """
    Affiche une ligne de séparation dans les journaux.

    Entrée :
        Aucune.

    Traitement :
        Génère une ligne composée de 70 caractères "=".

    Validation :
        Utilise le logger configuré pour le module.

    Retour :
        Aucun.
    """
    logger.info("=" * 70)


def title(text_value):
    """
    Affiche un titre encadré par deux lignes de séparation.

    Entrée :
        Texte du titre à afficher.

    Traitement :
        Affiche une séparation, le titre, puis une seconde séparation.

    Validation :
        Le texte est transmis directement au logger.

    Retour :
        Aucun.
    """
    separator()
    logger.info(text_value)
    separator()


# ============================================================
# 3. CONTROLES POSTGRESQL
# ============================================================

def table_exists(table_name):
    """
    Vérifie si une table existe dans le schéma public PostgreSQL.

    Entrée :
        Nom de la table à contrôler.

    Traitement :
        Interroge information_schema.tables avec un paramètre SQL nommé.

    Validation :
        Convertit le résultat SQL en booléen Python.

    Retour :
        True si la table existe, sinon False.
    """
    query = """
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = :table_name
    ) AS exists;
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            {"table_name": table_name},
        ).scalar()

    return bool(result)


def get_sequence_name(table_name, column_name):
    """
    Retourne le nom réel de la séquence PostgreSQL d'une colonne SERIAL.

    Entrée :
        Nom de la table et nom de la colonne.

    Traitement :
        Appelle la fonction PostgreSQL pg_get_serial_sequence.

    Validation :
        Utilise des paramètres SQL nommés pour la table et la colonne.

    Retour :
        Nom de la séquence ou None lorsqu'aucune séquence n'est trouvée.
    """
    query = "SELECT pg_get_serial_sequence(:table_name,:column_name)"
    params = {
        "table_name": table_name,
        "column_name": column_name,
    }

    with engine.connect() as connection:
        return connection.execute(
            text(query),
            params,
        ).scalar()


def get_max_id(connection, table_name, column_name):
    """
    Retourne la valeur maximale d'une colonne d'identifiant.

    Entrée :
        Connexion active, nom de la table et nom de la colonne.

    Traitement :
        Exécute MAX sur la colonne et remplace une valeur absente par zéro.

    Validation :
        La connexion est fournie par l'appelant dans une transaction active.

    Retour :
        Valeur maximale de la colonne ou zéro.
    """
    query = text(
        f"SELECT COALESCE(MAX({column_name}),0) FROM {table_name}"
    )

    return connection.execute(query).scalar()


def get_sequence_last_value(connection, sequence_name):
    """
    Retourne la dernière valeur enregistrée dans une séquence.

    Entrée :
        Connexion active et nom de la séquence PostgreSQL.

    Traitement :
        Lit la colonne last_value de la séquence.

    Validation :
        La connexion est fournie par l'appelant dans une transaction active.

    Retour :
        Dernière valeur de la séquence.
    """
    query = text(f"SELECT last_value FROM {sequence_name}")

    return connection.execute(query).scalar()


# ============================================================
# 4. SYNCHRONISATION DES SEQUENCES
# ============================================================

def reset_sequence(table_name, column_name):
    """
    Synchronise une séquence PostgreSQL avec la valeur MAX(id).

    Entrée :
        Nom de la table et nom de la colonne SERIAL.

    Traitement :
        Vérifie la table, récupère la séquence, calcule MAX(id),
        applique setval puis relit la dernière valeur de la séquence.

    Validation :
        Retourne une erreur structurée si la table ou la séquence
        est absente, ou si PostgreSQL déclenche une exception.

    Retour :
        Dictionnaire détaillant le résultat de la synchronisation.
    """
    if not table_exists(table_name):
        logger.error(f"Table absente : {table_name}")

        return {
            "table": table_name,
            "column": column_name,
            "sequence": None,
            "success": False,
            "error": "table_absente",
        }

    sequence_name = get_sequence_name(table_name, column_name)

    if not sequence_name:
        logger.error(
            f"Sequence introuvable : {table_name}.{column_name}"
        )

        return {
            "table": table_name,
            "column": column_name,
            "sequence": None,
            "success": False,
            "error": "sequence_introuvable",
        }

    try:
        with engine.begin() as connection:
            max_id = get_max_id(
                connection,
                table_name,
                column_name,
            )
            connection.execute(
                text("SELECT setval(:sequence_name,:value,true)"),
                {
                    "sequence_name": sequence_name,
                    "value": max_id,
                },
            )
            last_value = get_sequence_last_value(
                connection,
                sequence_name,
            )

        logger.info(
            f"{table_name}.{column_name} -> "
            f"max={max_id}, sequence={last_value}"
        )

        return {
            "table": table_name,
            "column": column_name,
            "sequence": sequence_name,
            "max_id": max_id,
            "last_value": last_value,
            "success": True,
            "error": None,
        }

    except SQLAlchemyError as error:
        logger.exception(
            f"Erreur sequence {table_name}.{column_name}"
        )

        return {
            "table": table_name,
            "column": column_name,
            "sequence": sequence_name,
            "success": False,
            "error": str(error),
        }


def reset_all_sequences():
    """
    Synchronise toutes les séquences SERIAL du projet.

    Entrée :
        Aucune. Les tables et colonnes proviennent de SERIAL_TABLES.

    Traitement :
        Parcourt chaque couple table/colonne et appelle reset_sequence.

    Validation :
        Compte les opérations réussies et échouées.

    Retour :
        Rapport global contenant les résultats détaillés.
    """
    results = []

    title("SYNCHRONISATION DES SEQUENCES")

    for index, (table_name, column_name) in enumerate(
        SERIAL_TABLES.items(),
        start=1,
    ):
        logger.info(
            f"[{index}/{len(SERIAL_TABLES)}] "
            f"{table_name}.{column_name}"
        )
        results.append(
            reset_sequence(
                table_name,
                column_name,
            )
        )

    report = {
        "total": len(results),
        "success": sum(
            1 for row in results if row["success"]
        ),
        "failed": sum(
            1 for row in results if not row["success"]
        ),
        "failed_items": [
            row for row in results if not row["success"]
        ],
        "details": results,
    }

    final_report(report)

    return report


# ============================================================
# 5. RAPPORT FINAL
# ============================================================

def final_report(report):
    """
    Affiche le rapport final de synchronisation.

    Entrée :
        Dictionnaire de rapport produit par reset_all_sequences.

    Traitement :
        Affiche les totaux puis détaille les opérations en erreur.

    Validation :
        La liste des erreurs est parcourue uniquement si elle existe.

    Retour :
        Aucun.
    """
    title("RAPPORT FINAL")

    logger.info(f"Sequences prevues : {report['total']}")
    logger.info(f"Sequences OK      : {report['success']}")
    logger.info(f"Sequences erreur  : {report['failed']}")

    if report["failed_items"]:
        logger.warning("Details des erreurs :")

        for item in report["failed_items"]:
            logger.warning(
                f"{item['table']}.{item['column']} -> "
                f"{item['error']}"
            )

    separator()


# ============================================================
# 6. POINT D'ENTREE CLI
# ============================================================

def main():
    """
    Exécute la synchronisation depuis la ligne de commande.

    Entrée :
        Aucune.

    Traitement :
        Vérifie la connexion PostgreSQL puis lance la synchronisation.

    Validation :
        Retourne un code d'erreur si la connexion échoue ou si une
        séquence n'a pas pu être synchronisée.

    Retour :
        Code de sortie 0 en cas de succès, sinon 1.
    """
    if not test_connection():
        logger.error("Connexion PostgreSQL impossible.")
        return 1

    report = reset_all_sequences()

    return 0 if report["failed"] == 0 else 1


# ============================================================
# 7. EXECUTION DIRECTE
# ============================================================

if __name__ == "__main__":
    sys.exit(main())
