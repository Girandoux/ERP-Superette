# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : config/styles.py
# AUTEUR : Girandoux Fandio
# DESCRIPTION : Styles Streamlit centralises pour l'application.
# ============================================================

import base64
import html
from pathlib import Path

import pandas as pd
import streamlit as st

from config.settings import (
    APP_AUTHOR,
    APP_NAME,
    APP_YEAR,
)


# ============================================================
# 1. COULEURS PRINCIPALES
# ============================================================

PRIMARY_COLOR = "#047857"
SECONDARY_COLOR = "#2563EB"
SUCCESS_COLOR = "#047857"
WARNING_COLOR = "#D97706"
DANGER_COLOR = "#DC2626"
INFO_COLOR = "#2563EB"
LIGHT_BG = "#F8FAFC"
BORDER_COLOR = "#E2E8F0"
TEXT_COLOR = "#0F172A"
MUTED_COLOR = "#64748B"


# ============================================================
# 2. FONCTION DE SECURISATION HTML
# ============================================================

def escape_html(value):
    """Protege un texte avant son insertion dans du HTML."""
    return html.escape(
        str(value)
    )


# ============================================================
# 3. STYLE GLOBAL
# ============================================================

def load_global_style():
    """Charge le CSS global de l'application."""
    st.markdown(
        f"""
        <style>
        .main .block-container {{
            padding-top: 0.65rem;
            padding-bottom: 1.2rem;
            max-width: 1420px;
        }}

        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(
                180deg,
                #FFFFFF 0%,
                #F8FAFC 100%
            );
        }}

        h1,
        h2,
        h3,
        h4 {{
            color: {TEXT_COLOR};
            font-weight: 700;
        }}

        p,
        span,
        div,
        label {{
            font-family: Arial, sans-serif;
        }}

        [data-testid="stSidebar"] {{
            background: {LIGHT_BG};
            border-right: 1px solid {BORDER_COLOR};
        }}

        [data-testid="stSidebarNav"]::before {{
            content: "Navigation";
            display: block;
            color: {TEXT_COLOR};
            font-size: 22px;
            font-weight: 800;
            line-height: 1.2;
            padding: 0.6rem 1.5rem 1rem 1.5rem;
        }}

        [data-testid="stSidebarNav"] ul {{
            padding-top: 0;
        }}

        [data-testid="stSidebarNav"] [role="heading"],
        [data-testid="stSidebarNav"] li > div > p {{
            color: {TEXT_COLOR};
            font-size: 20px;
            font-weight: 800;
            line-height: 1.25;
            margin-top: 0.9rem;
            margin-bottom: 0.45rem;
        }}

        [data-testid="stSidebarNav"] a,
        [data-testid="stSidebarNav"] a span {{
            color: {MUTED_COLOR};
            font-weight: 500;
            font-size: 16px;
        }}

        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a[aria-current="page"] span {{
            color: {PRIMARY_COLOR};
            font-weight: 700;
        }}

        [data-testid="stSidebarNav"] a:hover span {{
            color: {SECONDARY_COLOR};
        }}

        [data-testid="stSidebar"] h3 {{
            color: {TEXT_COLOR};
            font-size: 20px;
            font-weight: 800;
        }}

        [data-testid="stMetricValue"] {{
            color: {PRIMARY_COLOR};
            font-weight: 700;
        }}

        .stButton > button {{
            border-radius: 8px;
            border: 1px solid {PRIMARY_COLOR};
            background: {PRIMARY_COLOR};
            color: white;
            font-weight: 600;
        }}

        .stButton > button:hover {{
            background: {SECONDARY_COLOR};
            border-color: {SECONDARY_COLOR};
            color: white;
        }}

        .stTextInput input,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] {{
            border-radius: 8px;
        }}

        hr {{
            margin: 1rem 0;
            border-color: {BORDER_COLOR};
        }}

        .app-header {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            margin: 0 0 0.65rem 0;
            padding: 0.35rem 0 0.55rem 0;
        }}

        .app-logo {{
            width: 76px;
            height: 76px;
            object-fit: contain;
            border-radius: 8px;
        }}

        .app-header-text h1 {{
            margin: 0;
            color: {TEXT_COLOR};
            font-size: 38px;
            line-height: 1.05;
            font-weight: 800;
        }}

        .app-header-text p {{
            margin: 0.35rem 0 0 0;
            color: {MUTED_COLOR};
            font-size: 18px;
        }}

        .pro-hero {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            background: linear-gradient(
                135deg,
                #FFFFFF 0%,
                #ECFDF5 100%
            );
            padding: 22px 24px;
            margin: 0.3rem 0 1rem 0;
        }}

        .pro-hero h2 {{
            margin: 0;
            color: {TEXT_COLOR};
            font-size: 34px;
            font-weight: 850;
            line-height: 1.12;
        }}

        .pro-hero p {{
            margin: 0.55rem 0 0 0;
            color: {MUTED_COLOR};
            font-size: 16px;
            max-width: 900px;
        }}

        .pro-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }}

        .pro-badge {{
            border: 1px solid #99F6E4;
            background: #F0FDFA;
            color: {PRIMARY_COLOR};
            border-radius: 999px;
            padding: 5px 10px;
            font-size: 13px;
            font-weight: 700;
        }}

        .pro-panel {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            background: white;
            padding: 14px 16px;
            margin: 0.5rem 0;
        }}

        .pro-panel-title {{
            color: {TEXT_COLOR};
            font-size: 16px;
            font-weight: 800;
            margin-bottom: 8px;
        }}

        .pro-muted {{
            color: {MUTED_COLOR};
            font-size: 14px;
            line-height: 1.5;
        }}

        .quick-grid {{
            display: grid;
            grid-template-columns: repeat(
                4,
                minmax(0, 1fr)
            );
            gap: 10px;
            margin: 0.5rem 0 0.8rem 0;
        }}

        .quick-card {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            background: white;
            padding: 12px 14px;
            color: {TEXT_COLOR};
        }}

        .quick-card strong {{
            display: block;
            color: {TEXT_COLOR};
            font-size: 15px;
            margin-bottom: 3px;
        }}

        .quick-card span {{
            color: {MUTED_COLOR};
            font-size: 13px;
        }}

        .module-grid {{
            display: grid;
            grid-template-columns: repeat(
                3,
                minmax(0, 1fr)
            );
            gap: 12px;
            margin: 0.5rem 0 1rem 0;
        }}

        .module-card {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            background: white;
            padding: 14px;
        }}

        .module-card h4 {{
            font-size: 16px;
            margin: 0 0 8px 0;
        }}

        .module-card p {{
            font-size: 14px;
            color: {MUTED_COLOR};
            margin: 0;
            line-height: 1.5;
        }}

        .system-info {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 0.4rem;
        }}

        .system-info span {{
            display: inline-flex;
            gap: 6px;
            align-items: center;
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            background: white;
            color: {MUTED_COLOR};
            font-size: 14px;
            padding: 7px 10px;
        }}

        .system-info strong {{
            color: {TEXT_COLOR};
            font-weight: 700;
        }}

        .admin-info {{
            display: grid;
            grid-template-columns: repeat(
                4,
                minmax(0, 1fr)
            );
            gap: 10px;
            margin: 0.5rem 0 0.8rem 0;
        }}

        .admin-info span {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            background: white;
            color: {MUTED_COLOR};
            font-size: 13px;
            line-height: 1.35;
            padding: 9px 10px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .admin-info strong {{
            display: block;
            color: {TEXT_COLOR};
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 2px;
        }}

        .line-summary-card {{
            border: 1px solid #DFE7EF;
            border-radius: 8px;
            padding: 10px 12px;
            background: #FFFFFF;
            min-height: 76px;
        }}

        .line-summary-label {{
            font-size: 0.78rem;
            color: #53657D;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            margin-bottom: 6px;
        }}

        .line-summary-value {{
            font-size: 1.45rem;
            line-height: 1.1;
            font-weight: 800;
            color: {PRIMARY_COLOR};
        }}

        @media (max-width: 900px) {{
            .quick-grid,
            .module-grid,
            .admin-info {{
                grid-template-columns: repeat(
                    2,
                    minmax(0, 1fr)
                );
            }}
        }}

        @media (max-width: 700px) {{
            .app-header {{
                justify-content: flex-start;
                gap: 12px;
            }}

            .app-logo {{
                width: 54px;
                height: 54px;
            }}

            .app-header-text h1 {{
                font-size: 30px;
            }}
        }}

        @media (max-width: 560px) {{
            .quick-grid,
            .module-grid,
            .admin-info {{
                grid-template-columns: 1fr;
            }}
        }}

        /* TABLE_HEADER_PORTFOLIO */
        [data-testid="stDataFrame"] [role="columnheader"],
        [data-testid="stDataFrame"] thead tr th,
        .stDataFrame thead tr th {{
            background-color: #F3F4F6 !important;
            color: #334155 !important;
            font-weight: 700 !important;
        }}

        [data-testid="stDataFrame"] [role="gridcell"],
        [data-testid="stDataFrame"] tbody tr td {{
            border-color: #E5E7EB !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 4. EN-TETE ET PIED DE PAGE
# ============================================================

def image_to_base64(path):
    """Convertit une image locale en base64."""
    if not path:
        return ""

    try:
        image_path = Path(path)

        if image_path.exists():
            return base64.b64encode(
                image_path.read_bytes()
            ).decode("utf-8")

    except (OSError, ValueError):
        return ""

    return ""


def app_header(
    title=None,
    subtitle=None,
    logo_path=None,
):
    """Affiche un en-tete principal avec logo et titre."""
    title = escape_html(
        title or APP_NAME
    )

    subtitle = escape_html(
        subtitle
        or "Systeme professionnel de gestion commerciale"
    )

    logo_base64 = image_to_base64(
        logo_path
    )

    if logo_base64:
        logo_html = (
            "<img "
            f"src='data:image/png;base64,{logo_base64}' "
            "class='app-logo' "
            "alt='Logo'>"
        )

    else:
        logo_html = ""

    st.markdown(
        f"""
        <div class="app-header">
            {logo_html}
            <div class="app-header-text">
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()


def page_title(title, subtitle=None):
    """Affiche le titre d'une page."""
    safe_title = escape_html(
        title
    )

    st.markdown(
        (
            "<h2 style='margin-bottom:0.2rem;'>"
            f"{safe_title}"
            "</h2>"
        ),
        unsafe_allow_html=True,
    )

    if subtitle:
        safe_subtitle = escape_html(
            subtitle
        )

        st.markdown(
            (
                f"<p style='color:{MUTED_COLOR};margin-top:0;'>"
                f"{safe_subtitle}"
                "</p>"
            ),
            unsafe_allow_html=True,
        )

    st.divider()


def footer():
    """Affiche le pied de page."""
    st.divider()

    st.caption(
        f"Ã‚Â© {APP_YEAR} {APP_AUTHOR} | "
        f"{APP_NAME} | "
        "Python - Streamlit - PostgreSQL - Power BI"
    )


# ============================================================
# 5. COMPOSANTS VISUELS
# ============================================================

def hero_panel(title, subtitle, badges=None):
    """Affiche une introduction pour les pages principales."""
    badges = badges or []

    badges_html = "".join(
        (
            "<span class='pro-badge'>"
            f"{escape_html(badge_text)}"
            "</span>"
        )
        for badge_text in badges
    )

    st.markdown(
        f"""
        <div class="pro-hero">
            <h2>{escape_html(title)}</h2>
            <p>{escape_html(subtitle)}</p>
            <div class="pro-badges">{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def _numeric_value_for_color(value):
    """Convertit une valeur KPI en nombre quand c'est possible."""
    try:
        cleaned = (
            str(value)
            .replace("FCFA", "")
            .replace("%", "")
            .replace("\u00a0", " ")
            .replace(" ", "")
            .replace(",", ".")
        )
        return float(cleaned)
    except (TypeError, ValueError):
        return None


def kpi_color(title, value=None):
    """Retourne une couleur KPI coherente avec le dashboard Power BI."""
    text = str(title or "").lower()
    numeric = _numeric_value_for_color(value)
    if numeric is not None and numeric < 0:
        return DANGER_COLOR
    if numeric is not None and numeric == 0 and any(word in text for word in ("alerte", "rupture", "manquant", "perte", "ecart", "ÃƒÂ©cart")):
        return SUCCESS_COLOR
    danger_words = ("rupture", "ruptures", "manquant", "manquants", "perte", "pertes", "erreur", "critique", "non rentable", "non rentables", "sortie", "sorties")
    warning_words = ("alerte", "alertes", "attention", "depense", "depenses", "dÃƒÂ©pense", "dÃƒÂ©penses", "ecart", "ÃƒÂ©cart")
    info_words = ("achat", "achats", "facture", "factures", "mouvement", "mouvements", "surplus")
    if any(word in text for word in danger_words):
        return DANGER_COLOR
    if any(word in text for word in warning_words):
        return WARNING_COLOR
    if any(word in text for word in info_words):
        return SECONDARY_COLOR
    return SUCCESS_COLOR
def kpi_card(
    title,
    value,
    help_text=None,
    color=None,
):
    """Affiche une carte KPI compacte."""
    help_html = ""
    card_color = color or kpi_color(title, value)

    if help_text:
        help_html = (
            f"<small style='color:{MUTED_COLOR};font-size:12px;'>"
            f"{escape_html(help_text)}"
            "</small>"
        )

    st.markdown(
        f"""
        <div style="
            border:1px solid {BORDER_COLOR};
            border-radius:8px;
            padding:10px 12px;
            background:white;
            box-shadow:0 1px 2px rgba(15,23,42,0.04);
            min-height:72px;
        ">
            <div style="
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:8px;
            ">
                <div style="
                    color:{MUTED_COLOR};
                    font-size:12px;
                    font-weight:700;
                    text-transform:uppercase;
                    letter-spacing:0.02em;
                ">
                    {escape_html(title)}
                </div>
                <div style="
                    width:7px;
                    height:7px;
                    border-radius:999px;
                    background:{escape_html(card_color)};
                    flex:0 0 auto;
                "></div>
            </div>
            <div style="
                color:{escape_html(card_color)};
                font-size:clamp(18px,1.65vw,22px);
                font-weight:800;
                line-height:1.1;
                margin-top:5px;
                word-break:break-word;
                overflow-wrap:anywhere;
            ">
                {escape_html(value)}
            </div>
            {help_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_box(message, color=INFO_COLOR):
    """Affiche un message d'information."""
    st.markdown(
        f"""
        <div style="
            border-left:4px solid {escape_html(color)};
            background:{LIGHT_BG};
            padding:10px 12px;
            border-radius:6px;
            margin:8px 0;
            min-height:54px;
            display:flex;
            align-items:center;
            min-height:54px;
            display:flex;
            align-items:center;
        ">
            <span style="color:{TEXT_COLOR};">
                {escape_html(message)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(text, color=PRIMARY_COLOR):
    """Affiche un badge colore."""
    st.markdown(
        (
            f"<span style='background:{escape_html(color)};"
            "color:white;"
            "border-radius:999px;"
            "padding:4px 10px;"
            "font-size:13px;"
            "font-weight:600;'>"
            f"{escape_html(text)}"
            "</span>"
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# 6. MESSAGES STANDARD
# ============================================================

def success_message(message):
    """Affiche un message de succes."""
    st.success(message)


def warning_message(message):
    """Affiche un message d'avertissement."""
    st.warning(message)


def error_message(message):
    """Affiche un message d'erreur."""
    st.error(message)


def empty_data_message(
    message="Aucune donnee disponible.",
):
    """Affiche un message lorsqu'un tableau est vide."""
    info_box(
        message,
        color=WARNING_COLOR,
    )


# ============================================================
# 7. TABLEAUX
# ============================================================

def format_money_value(value):
    """Formate une valeur monetaire pour Streamlit."""
    try:
        amount = float(
            value or 0
        )

    except (TypeError, ValueError):
        return value

    return (
        f"{amount:,.0f} FCFA"
        .replace(",", " ")
    )


def is_money_column(column_name):
    """Detecte les colonnes monetaires."""
    column = str(
        column_name
    ).lower()

    if column.endswith(
        "_affiche"
    ):
        return False

    non_money_columns = {
        "nom_categorie",
        "categorie_depense",
        "motif_perte",
        "type_mouvement",
        "type_vente",
        "unite",
        "utilisateur",
        "actif",
        "statut",
        "status",
        "statut_ecart",
        "statut_cloture",
        "description",
        "qte_cartons",
        "qte_par_carton",
        "qte_vente",
        "qte_perte",
        "quantite_achat",
        "quantite_vendue",
        "quantite_totale",
        "stock_actuel",
        "stock_min",
        "stock_minimum",
        "stock_theorique",
        "stock_physique",
        "stock_final",
        "ecart",
        "total_depenses",
        "total_pertes",
        "total_mouvements",
        "total_categories",
        "total_produits",
        "total_achats",
        "total_ventes",
        "total_lignes",
        "annee",
        "mois",
        "jour",
        "semaine",
        "trimestre",
    }

    if (
        column in non_money_columns
        or column.endswith("_id")
        or column.startswith("date_")
        or column.startswith("code_")
        or column.startswith("nom_")
    ):
        return False

    money_columns = {
        "montant",
        "montant_ligne",
        "montant_total",
        "montant_moyen",
        "montant_max",
        "montant_min",
        "total_achat",
        "total_facture",
        "total_vente",
        "total_stock",
        "frais_enlevement",
        "prix",
        "prix_moyen",
        "pu_vente",
        "pu_achat_carton",
        "pu_achat_piece",
        "cout_unitaire",
        "cout_total",
        "cout_achat",
        "cout_stock",
        "valeur_stock",
        "valeur_unitaire",
        "valeur_totale",
        "valeur_ecart",
        "valeur_perdue",
        "chiffre_affaires",
        "benefice",
        "benefice_net",
        "marge",
        "marge_brute",
        "solde",
        "solde_reel_caisse",
        "entrees",
        "sorties",
        "entrees_reelles",
        "sorties_reelles",
    }

    money_prefixes = (
        "pu_",
        "prix_",
        "cout_",
        "montant_",
        "valeur_",
        "marge_",
        "benefice_",
        "solde_",
        "frais_",
    )

    return (
        column in money_columns
        or any(
            column.startswith(prefix)
            for prefix in money_prefixes
        )
    )


def format_money_columns(dataframe):
    """Formate les colonnes monetaires numeriques."""
    result = dataframe.copy()

    for column in result.columns:
        if (
            is_money_column(column)
            and pd.api.types.is_numeric_dtype(
                result[column]
            )
        ):
            result[column] = result[column].apply(
                format_money_value
            )

    return result


def prepare_dataframe_for_display(dataframe):
    """Prepare un tableau propre pour l'affichage."""
    if dataframe is None:
        return None

    result = pd.DataFrame(
        dataframe
    ).copy()

    if result.empty:
        return result

    raw_columns_to_hide = []
    rename_map = {}

    for column in result.columns:
        column_name = str(
            column
        )

        if column_name.endswith(
            "_affiche"
        ):
            base_name = column_name[:-8]
            rename_map[column] = base_name

            if base_name in result.columns:
                raw_columns_to_hide.append(
                    base_name
                )

    if raw_columns_to_hide:
        result = result.drop(
            columns=list(
                dict.fromkeys(
                    raw_columns_to_hide
                )
            ),
            errors="ignore",
        )

    if rename_map:
        result = result.rename(
            columns=rename_map
        )

    return format_money_columns(
        result
    )


def style_status_cells(dataframe):
    """Colore les statuts importants dans les tableaux."""
    def cell_style(value):
        text = str(
            value
        ).strip().upper()

        if text == "SURPLUS":
            return (
                "background-color:#DBEAFE;"
                "color:#1D4ED8;"
                "font-weight:800;"
            )

        if text == "CONFORME":
            return (
                "background-color:#DCFCE7;"
                "color:#15803D;"
                "font-weight:800;"
            )

        if text == "MANQUANT":
            return (
                "background-color:#FEE2E2;"
                "color:#B91C1C;"
                "font-weight:800;"
            )

        return ""

    styled_dataframe = dataframe.style

    if "statut_ecart" in dataframe.columns:
        styled_dataframe = styled_dataframe.map(
            cell_style,
            subset=["statut_ecart"],
        )

    return styled_dataframe


def display_dataframe(
    dataframe,
    *args,
    **kwargs,
):
    """Affiche un tableau Streamlit nettoye."""
    result = prepare_dataframe_for_display(
        dataframe
    )

    if result is None or result.empty:
        empty_data_message()
        return

    kwargs.setdefault(
        "use_container_width",
        True,
    )

    kwargs.setdefault(
        "hide_index",
        True,
    )

    if "statut_ecart" in result.columns:
        st.dataframe(
            style_status_cells(result),
            *args,
            **kwargs,
        )

    else:
        st.dataframe(
            result,
            *args,
            **kwargs,
        )


def show_dataframe(
    dataframe,
    height=420,
    use_container_width=True,
):
    """Affiche un DataFrame avec une configuration standard."""
    display_dataframe(
        dataframe,
        height=height,
        use_container_width=use_container_width,
    )


