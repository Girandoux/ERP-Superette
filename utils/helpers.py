# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/helpers.py
# ROLE : Fonctions utilitaires generales
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

import json
import logging
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Any

from config.settings import STREAMLIT_DIR

# ============================================================
# 1. CONFIGURATION
# ============================================================

logger = logging.getLogger("utils")

# ============================================================
# 2. TEXTES ET FORMATS
# ============================================================


def clean_text(value: Any, default: str = "") -> str:
    """Nettoie une valeur texte."""
    if value is None:
        return default

    text = str(value).strip()
    return re.sub(r"\s+", " ", text) if text else default


def normalize_text(value: Any) -> str:
    """Retourne un texte minuscule sans accents pour les recherches."""
    text = clean_text(value).lower()
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def slugify(value: Any, separator: str = "_") -> str:
    """Transforme un texte en identifiant simple."""
    text = normalize_text(value)
    text = re.sub(r"[^a-z0-9]+", separator, text).strip(separator)
    return text or "sans_nom"


def format_money(value: Any, currency: str = "FCFA") -> str:
    """Formate un montant."""
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0.0

    return f"{amount:,.0f} {currency}".replace(",", " ")


def format_quantity(value: Any, unit: str = "") -> str:
    """Formate une quantite."""
    try:
        quantity = float(value or 0)
    except (TypeError, ValueError):
        quantity = 0.0

    text = (
        f"{quantity:,.2f}"
        .replace(",", " ")
        .rstrip("0")
        .rstrip(".")
    )
    return f"{text} {unit}".strip()


def format_percent(value: Any) -> str:
    """Formate un pourcentage."""
    try:
        percent = float(value or 0)
    except (TypeError, ValueError):
        percent = 0.0

    return f"{percent:.2f} %"


# ============================================================
# 3. DATES
# ============================================================


def today() -> date:
    """Retourne la date du jour."""
    return date.today()


def now() -> datetime:
    """Retourne la date et heure actuelle."""
    return datetime.now()


def parse_date(
    value: Any,
    default: date | None = None,
) -> date | None:
    """Convertit une valeur en date."""
    if value in (None, ""):
        return default

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    date_formats = (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
    )

    for date_format in date_formats:
        try:
            return datetime.strptime(
                str(value).strip(),
                date_format,
            ).date()
        except ValueError:
            continue

    return default


def date_to_str(
    value: Any,
    fmt: str = "%Y-%m-%d",
) -> str:
    """Convertit une date en texte."""
    parsed_date = parse_date(value)
    return parsed_date.strftime(fmt) if parsed_date else ""


def get_date_id(value: Any = None) -> date:
    """Retourne la date_id utilisee par la base."""
    return parse_date(value, default=today()) or today()


# ============================================================
# 4. NOMBRES ET LISTES
# ============================================================


def to_int(value: Any, default: int = 0) -> int:
    """Convertit une valeur en entier."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    """Convertit une valeur en decimal."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_divide(
    numerator: Any,
    denominator: Any,
    default: float = 0.0,
) -> float:
    """Division protegee contre zero et valeurs invalides."""
    numerator_value = to_float(numerator)
    denominator_value = to_float(denominator)

    if denominator_value == 0:
        return default

    return numerator_value / denominator_value


def unique_list(values: list[Any]) -> list[Any]:
    """Retourne une liste sans doublons en gardant l'ordre."""
    result = []

    for value in values:
        if value not in result:
            result.append(value)

    return result


def chunk_list(
    values: list[Any],
    size: int,
) -> list[list[Any]]:
    """Decoupe une liste en blocs."""
    if size <= 0:
        return [values]

    return [
        values[index:index + size]
        for index in range(0, len(values), size)
    ]


# ============================================================
# 5. FICHIERS
# ============================================================


def ensure_dir(path: str | Path) -> Path:
    """Cree un dossier si necessaire."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_parent(path: str | Path) -> Path:
    """Cree le dossier parent d'un fichier si necessaire."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    return file_path


def file_exists(path: str | Path) -> bool:
    """Verifie si un fichier existe."""
    return Path(path).is_file()


def get_file_size(path: str | Path) -> int:
    """Retourne la taille d'un fichier en octets."""
    file_path = Path(path)
    return file_path.stat().st_size if file_path.exists() else 0


# ============================================================
# 6. REPONSES STANDARD
# ============================================================


def success_response(
    message: str = "Operation reussie",
    data: Any = None,
) -> dict[str, Any]:
    """Retourne une reponse standard positive."""
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str = "Erreur",
    data: Any = None,
) -> dict[str, Any]:
    """Retourne une reponse standard negative."""
    return {
        "success": False,
        "message": message,
        "data": data,
    }


def log_exception(
    message: str,
    error: Exception,
) -> dict[str, Any]:
    """Journalise une exception et retourne une reponse standard."""
    logger.exception("%s : %s", message, error)
    return error_response(f"{message} : {error}")


# ============================================================
# 7. ETAT LOCAL DE L'INTERFACE
# ============================================================


def _ui_state_path() -> Path:
    """Retourne le fichier local de memorisation de l'interface."""
    ensure_dir(STREAMLIT_DIR)
    return STREAMLIT_DIR / "ui_state.json"


def load_ui_state() -> dict[str, Any]:
    """Charge les preferences locales de l'interface."""
    path = _ui_state_path()

    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        logger.warning(
            "Chargement ui_state impossible : %s",
            error,
        )
        return {}


def save_ui_state(state: dict[str, Any]) -> bool:
    """Sauvegarde les preferences locales de l'interface."""
    try:
        path = _ui_state_path()
        content = json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
        )
        path.write_text(content, encoding="utf-8")
        return True
    except (OSError, TypeError) as error:
        logger.warning(
            "Sauvegarde ui_state impossible : %s",
            error,
        )
        return False


def get_ui_state(
    key: str,
    default: Any = None,
) -> Any:
    """Retourne une valeur memorisee de l'interface."""
    return load_ui_state().get(key, default)


def set_ui_state(key: str, value: Any) -> bool:
    """Memorise une valeur de l'interface."""
    state = load_ui_state()
    safe_value = _json_safe_ui_value(value)

    if safe_value is None and value is not None:
        logger.warning(
            "Valeur ui_state non sauvegardable pour la cle : %s",
            key,
        )
        return False

    state[key] = safe_value
    return save_ui_state(state)


def _json_safe_ui_value(value: Any) -> Any:
    """Convertit une valeur Streamlit en valeur sauvegardable."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, datetime):
        return {
            "__type__": "datetime",
            "value": value.isoformat(),
        }

    if isinstance(value, date):
        return {
            "__type__": "date",
            "value": value.isoformat(),
        }

    if isinstance(value, (list, tuple)):
        return [
            _json_safe_ui_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _json_safe_ui_value(item)
            for key, item in value.items()
        }

    return None


def _restore_ui_value(value: Any) -> Any:
    """Restaure une valeur sauvegardee pour Streamlit."""
    if isinstance(value, dict) and value.get("__type__") == "date":
        return parse_date(value.get("value"))

    if (
        isinstance(value, dict)
        and value.get("__type__") == "datetime"
    ):
        try:
            return datetime.fromisoformat(
                value.get("value", "")
            )
        except (TypeError, ValueError):
            return None

    if isinstance(value, list):
        return [
            _restore_ui_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: _restore_ui_value(item)
            for key, item in value.items()
        }

    return value


def restore_ui_state_to_session(session_state: Any) -> None:
    """Recharge les champs memorises dans la session Streamlit."""
    for key, value in load_ui_state().items():
        if key not in session_state:
            session_state[key] = _restore_ui_value(value)


def save_session_ui_state(session_state: Any) -> bool:
    """Sauvegarde les champs simples de la session Streamlit."""
    state = load_ui_state()

    for key, value in dict(session_state).items():
        key = str(key)

        if key.startswith(("FormSubmitter:", "pending_")):
            continue

        safe_value = _json_safe_ui_value(value)
        if safe_value is not None:
            state[key] = safe_value

    return save_ui_state(state)


__all__ = [
    "clean_text",
    "normalize_text",
    "slugify",
    "format_money",
    "format_quantity",
    "format_percent",
    "today",
    "now",
    "parse_date",
    "date_to_str",
    "get_date_id",
    "to_int",
    "to_float",
    "safe_divide",
    "unique_list",
    "chunk_list",
    "ensure_dir",
    "ensure_parent",
    "file_exists",
    "get_file_size",
    "success_response",
    "error_response",
    "log_exception",
    "load_ui_state",
    "save_ui_state",
    "get_ui_state",
    "set_ui_state",
    "restore_ui_state_to_session",
    "save_session_ui_state",
]
