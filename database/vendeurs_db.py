# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : database/vendeurs_db.py
# AUTEUR : Girandoux Fandio
# DESCRIPTION : CRUD, recherche et statistiques pour la table
# dim_vendeurs.
# ============================================================

import logging

import pandas as pd

from database.database_utils import (
    execute_query,
    fetch_one,
    get_scalar,
    read_sql_dataframe,
    record_exists,
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("database")

TABLE_NAME = "dim_vendeurs"
VENTES_TABLE = "fact_ventes"
ID_COLUMN = "vendeur_id"
NAME_COLUMN = "nom_vendeur"


# ============================================================
# 2. VALIDATION ET NORMALISATION
# ============================================================

def _normalize_name(value):
    """
    Nettoie et normalise un nom de vendeur.

    Entrée :
        Valeur reçue depuis l'interface ou la base de données.

    Traitement :
        Supprime les espaces inutiles au début, à la fin et entre les mots.

    Validation :
        Une valeur None est transformée en chaîne vide.

    Retour :
        Nom normalisé sous forme de chaîne de caractères.
    """
    if value is None:
        return ""

    return " ".join(str(value).strip().split())


def validate_vendeur_name(nom_vendeur):
    """
    Valide le nom d'un vendeur.

    Entrée :
        Nom du vendeur à contrôler.

    Traitement :
        Normalise le nom avant d'appliquer les règles métier.

    Validation :
        Vérifie que le nom n'est pas vide et ne dépasse pas 100 caractères.

    Retour :
        Tuple composé d'un booléen et d'un message de validation.
    """
    nom_vendeur = _normalize_name(nom_vendeur)

    if not nom_vendeur:
        return False, "Le nom vendeur est obligatoire."

    if len(nom_vendeur) > 100:
        return False, "Le nom vendeur ne doit pas depasser 100 caracteres."

    return True, "OK"


def vendeur_name_exists(nom_vendeur, exclude_id=None):
    """
    Vérifie si un vendeur portant le même nom existe déjà.

    Entrée :
        Nom du vendeur et identifiant facultatif à exclure.

    Traitement :
        Recherche le nom sans tenir compte de la casse.

    Validation :
        Exclut l'identifiant courant lors d'une modification.

    Retour :
        True si le vendeur existe, sinon False.
    """
    query = (
        f"SELECT 1 FROM {TABLE_NAME} "
        f"WHERE LOWER({NAME_COLUMN}) = LOWER(:name)"
    )
    params = {"name": _normalize_name(nom_vendeur)}

    if exclude_id is not None:
        query += f" AND {ID_COLUMN} <> :id"
        params["id"] = exclude_id

    return record_exists(query, params)


def can_save_vendeur(nom_vendeur, exclude_id=None):
    """
    Vérifie si un vendeur peut être enregistré.

    Entrée :
        Nom du vendeur et identifiant facultatif à exclure.

    Traitement :
        Contrôle le format du nom puis recherche les doublons.

    Validation :
        Refuse les noms invalides ou déjà présents.

    Retour :
        Tuple composé d'un booléen et d'un message.
    """
    valid, message = validate_vendeur_name(nom_vendeur)

    if not valid:
        return False, message

    if vendeur_name_exists(nom_vendeur, exclude_id):
        return False, "Ce vendeur existe deja."

    return True, "OK"


# ============================================================
# 3. LECTURE ET RECHERCHE
# ============================================================

def get_all_vendeurs():
    """
    Retourne tous les vendeurs.

    Entrée :
        Aucune.

    Traitement :
        Sélectionne tous les vendeurs triés par nom.

    Validation :
        La requête est exécutée par l'utilitaire commun de lecture.

    Retour :
        DataFrame contenant les vendeurs.
    """
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY {NAME_COLUMN}"

    return read_sql_dataframe(query)


def get_vendeur_by_id(vendeur_id):
    """
    Retourne un vendeur à partir de son identifiant.

    Entrée :
        Identifiant du vendeur.

    Traitement :
        Recherche une ligne correspondant à l'identifiant fourni.

    Validation :
        Utilise un paramètre SQL nommé.

    Retour :
        Ligne du vendeur ou None.
    """
    query = f"SELECT * FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"

    return fetch_one(query, {"id": vendeur_id})


def get_vendeur_by_name(nom_vendeur):
    """
    Retourne un vendeur à partir de son nom.

    Entrée :
        Nom du vendeur.

    Traitement :
        Normalise le nom puis effectue une recherche insensible à la casse.

    Validation :
        Utilise un paramètre SQL nommé.

    Retour :
        Ligne du vendeur ou None.
    """
    query = (
        f"SELECT * FROM {TABLE_NAME} "
        f"WHERE LOWER({NAME_COLUMN}) = LOWER(:name)"
    )
    params = {"name": _normalize_name(nom_vendeur)}

    return fetch_one(query, params)


def vendeur_exists(vendeur_id):
    """
    Vérifie si un vendeur existe.

    Entrée :
        Identifiant du vendeur.

    Traitement :
        Recherche l'existence d'une ligne correspondante.

    Validation :
        Utilise un paramètre SQL nommé.

    Retour :
        True si le vendeur existe, sinon False.
    """
    query = f"SELECT 1 FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"

    return record_exists(query, {"id": vendeur_id})


def search_vendeurs(keyword):
    """
    Recherche des vendeurs par nom.

    Entrée :
        Mot-clé de recherche.

    Traitement :
        Normalise le mot-clé puis utilise une recherche ILIKE.

    Validation :
        Retourne un DataFrame vide lorsque le mot-clé est absent.

    Retour :
        DataFrame contenant les vendeurs correspondants.
    """
    keyword = _normalize_name(keyword)

    if not keyword:
        return pd.DataFrame()

    query = (
        f"SELECT * FROM {TABLE_NAME} "
        f"WHERE {NAME_COLUMN} ILIKE :keyword "
        f"ORDER BY {NAME_COLUMN}"
    )
    params = {"keyword": f"%{keyword}%"}

    return read_sql_dataframe(query, params)


def count_vendeurs():
    """
    Compte le nombre total de vendeurs.

    Entrée :
        Aucune.

    Traitement :
        Exécute une requête COUNT sur la table des vendeurs.

    Validation :
        Convertit une valeur absente en zéro.

    Retour :
        Nombre total de vendeurs.
    """
    value = get_scalar(f"SELECT COUNT(*) FROM {TABLE_NAME}")

    return int(value or 0)


# ============================================================
# 4. INSERTION ET MODIFICATION
# ============================================================

def insert_vendeur(nom_vendeur):
    """
    Insère un nouveau vendeur.

    Entrée :
        Nom du vendeur.

    Traitement :
        Normalise, valide puis insère le vendeur.

    Validation :
        Refuse les noms invalides ou déjà existants.

    Retour :
        Résultat booléen de l'opération d'insertion.
    """
    nom_vendeur = _normalize_name(nom_vendeur)
    valid, message = can_save_vendeur(nom_vendeur)

    if not valid:
        logger.warning(message)
        return False

    query = (
        f"INSERT INTO {TABLE_NAME} ({NAME_COLUMN}) "
        "VALUES (:name)"
    )
    params = {"name": nom_vendeur}

    return execute_query(query, params)


def create_vendeur(nom_vendeur):
    """
    Crée un vendeur depuis l'interface Streamlit.

    Entrée :
        Nom du vendeur.

    Traitement :
        Délègue l'enregistrement à insert_vendeur.

    Validation :
        Réutilise les contrôles présents dans insert_vendeur.

    Retour :
        Résultat booléen de l'opération.
    """
    return insert_vendeur(nom_vendeur)


def update_vendeur(vendeur_id, nom_vendeur):
    """
    Modifie le nom d'un vendeur existant.

    Entrée :
        Identifiant et nouveau nom du vendeur.

    Traitement :
        Vérifie l'existence, normalise le nom puis exécute la mise à jour.

    Validation :
        Refuse les vendeurs inexistants, les noms invalides et les doublons.

    Retour :
        Résultat booléen de l'opération de modification.
    """
    if not vendeur_exists(vendeur_id):
        logger.warning("Vendeur inexistant.")
        return False

    nom_vendeur = _normalize_name(nom_vendeur)
    valid, message = can_save_vendeur(
        nom_vendeur,
        exclude_id=vendeur_id,
    )

    if not valid:
        logger.warning(message)
        return False

    query = (
        f"UPDATE {TABLE_NAME} "
        f"SET {NAME_COLUMN} = :name "
        f"WHERE {ID_COLUMN} = :id"
    )
    params = {
        "id": vendeur_id,
        "name": nom_vendeur,
    }

    return execute_query(query, params)


# ============================================================
# 5. SUPPRESSION PROTEGEE
# ============================================================

def count_ventes_by_vendeur(vendeur_id):
    """
    Compte les ventes liées à un vendeur.

    Entrée :
        Identifiant du vendeur.

    Traitement :
        Compte les ventes associées dans fact_ventes.

    Validation :
        Retourne zéro lorsqu'aucun résultat n'est trouvé.

    Retour :
        Nombre de ventes liées au vendeur.
    """
    query = (
        f"SELECT COUNT(*) AS total "
        f"FROM {VENTES_TABLE} "
        f"WHERE {ID_COLUMN} = :id"
    )
    result = fetch_one(query, {"id": vendeur_id})

    return int(result["total"]) if result else 0


def can_delete_vendeur(vendeur_id):
    """
    Vérifie si un vendeur peut être supprimé.

    Entrée :
        Identifiant du vendeur.

    Traitement :
        Vérifie l'existence puis compte les ventes associées.

    Validation :
        Bloque la suppression lorsqu'une vente utilise ce vendeur.

    Retour :
        Tuple composé d'un booléen et d'un message.
    """
    if not vendeur_exists(vendeur_id):
        return False, "Vendeur inexistant."

    total = count_ventes_by_vendeur(vendeur_id)

    if total > 0:
        return (
            False,
            f"Suppression impossible : {total} vente(s) "
            "utilisent ce vendeur.",
        )

    return True, "OK"


def delete_vendeur(vendeur_id):
    """
    Supprime un vendeur lorsqu'aucune vente ne l'utilise.

    Entrée :
        Identifiant du vendeur.

    Traitement :
        Vérifie l'autorisation puis exécute la suppression.

    Validation :
        Refuse la suppression si le vendeur est inexistant ou utilisé.

    Retour :
        Résultat booléen de l'opération.
    """
    valid, message = can_delete_vendeur(vendeur_id)

    if not valid:
        logger.warning(message)
        return False

    query = f"DELETE FROM {TABLE_NAME} WHERE {ID_COLUMN} = :id"

    return execute_query(query, {"id": vendeur_id})


# ============================================================
# 6. STATISTIQUES ET INDICATEURS
# ============================================================

def get_vendeurs_with_ventes():
    """
    Retourne les vendeurs avec leurs statistiques de vente.

    Entrée :
        Aucune.

    Traitement :
        Agrège le nombre et le montant total des ventes par vendeur.

    Validation :
        Conserve les vendeurs sans vente grâce à une jointure LEFT JOIN.

    Retour :
        DataFrame contenant les statistiques par vendeur.
    """
    query = f"""
        SELECT
            v.{ID_COLUMN},
            v.{NAME_COLUMN},
            COUNT(f.vente_id) AS total_ventes,
            COALESCE(SUM(f.total_vente), 0) AS montant_total
        FROM {TABLE_NAME} v
        LEFT JOIN {VENTES_TABLE} f
            ON f.{ID_COLUMN} = v.{ID_COLUMN}
        GROUP BY
            v.{ID_COLUMN},
            v.{NAME_COLUMN}
        ORDER BY
            v.{NAME_COLUMN}
    """

    return read_sql_dataframe(query)


def get_vendeur_kpis():
    """
    Retourne les principaux indicateurs liés aux vendeurs.

    Entrée :
        Aucune.

    Traitement :
        Calcule le nombre total, les vendeurs utilisés, non utilisés
        et le montant cumulé des ventes.

    Validation :
        Retourne des indicateurs à zéro lorsque le DataFrame est vide.

    Retour :
        Dictionnaire contenant les KPI des vendeurs.
    """
    df = get_vendeurs_with_ventes()

    if df.empty:
        return {
            "total_vendeurs": 0,
            "vendeurs_utilises": 0,
            "vendeurs_non_utilises": 0,
            "montant_total_ventes": 0,
        }

    used = int((df["total_ventes"] > 0).sum())

    return {
        "total_vendeurs": len(df),
        "vendeurs_utilises": used,
        "vendeurs_non_utilises": len(df) - used,
        "montant_total_ventes": float(df["montant_total"].sum()),
    }


# ============================================================
# 7. INTERFACE PUBLIQUE DU MODULE
# ============================================================

__all__ = [
    "get_all_vendeurs",
    "get_vendeur_by_id",
    "get_vendeur_by_name",
    "vendeur_exists",
    "search_vendeurs",
    "count_vendeurs",
    "insert_vendeur",
    "create_vendeur",
    "update_vendeur",
    "delete_vendeur",
    "can_delete_vendeur",
    "count_ventes_by_vendeur",
    "get_vendeurs_with_ventes",
    "get_vendeur_kpis",
]
