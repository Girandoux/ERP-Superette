# ============================================================
# PROJET : GESTION DE SUPERETTE ERP
# FICHIER : app.py
# AUTEUR : Girandoux Fandio
#
# DESCRIPTION
# ------------------------------------------------------------
# Point d'entrée principal de l'application Streamlit.
#
# Version 1 : Interface Streamlit
# Version 2 : PostgreSQL et Power BI
# Version 3 : Intelligence artificielle et Machine Learning
# ============================================================

from __future__ import annotations

import streamlit as st

from config.database import database_information, test_connection
from config.settings import (
    LOGO_PATH,
    PAGE_LAYOUT,
    PAGE_TITLE,
    SIDEBAR_STATE,
)
from config.styles import app_header, footer, load_global_style
from utils.helpers import (
    restore_ui_state_to_session,
    save_session_ui_state,
)


# ============================================================
# 1. CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🛒",
    layout=PAGE_LAYOUT,
    initial_sidebar_state=SIDEBAR_STATE,
)


# ============================================================
# 2. CHARGEMENT DU STYLE GLOBAL
# ============================================================

load_global_style()


# ============================================================
# 3. RESTAURATION DE L'ETAT DE L'INTERFACE
# ============================================================

restore_ui_state_to_session(st.session_state)


# ============================================================
# 4. VERIFICATION DE LA CONNEXION POSTGRESQL
# ============================================================

@st.cache_data(ttl=30, show_spinner=False)
def check_database_connection() -> bool:
    """
    Teste la connexion PostgreSQL.

    Le résultat reste en cache pendant 30 secondes afin
    d'éviter une nouvelle vérification à chaque interaction.
    """

    return test_connection()


db_connected = check_database_connection()
db_info = database_information()


# ============================================================
# 5. AFFICHAGE DE LA CONNEXION DANS LA BARRE LATERALE
# ============================================================

database_name = db_info.get("database", "Non définie")
database_host = db_info.get("host", "Non défini")
database_port = db_info.get("port", "Non défini")

with st.sidebar:
    st.markdown("### Connexion PostgreSQL")

    st.caption(f"Base : {database_name}")
    st.caption(f"Serveur : {database_host}:{database_port}")

    if db_connected:
        st.success("Connexion active")
    else:
        st.error("Connexion impossible")


# ============================================================
# 6. ARRET DE L'APPLICATION EN CAS D'ERREUR
# ============================================================

if not db_connected:
    st.error(
        "Impossible de se connecter à PostgreSQL. "
        "Vérifiez le fichier `.env`, le serveur PostgreSQL "
        "et l'existence de la base de données."
    )

    st.info(
        "Après avoir corrigé la configuration, "
        "actualisez la page ou redémarrez l'application."
    )

    st.stop()


# ============================================================
# 7. LOGO ET EN-TETE PRINCIPAL
# ============================================================

app_header(
    title="Gestion de Supérette",
    subtitle="Système professionnel de gestion commerciale",
    logo_path=LOGO_PATH,
)


# ============================================================
# 8. DEFINITION DES PAGES STREAMLIT
# ============================================================

page_accueil = st.Page(
    "streamlit/pages/01_Accueil.py",
    title="Accueil",
    icon="🏠",
    default=True,
)

page_produits = st.Page(
    "streamlit/pages/02_Produits.py",
    title="Produits",
    icon="📦",
)

page_categories = st.Page(
    "streamlit/pages/03_Categories.py",
    title="Catégories",
    icon="📂",
)

page_achats = st.Page(
    "streamlit/pages/04_Achats.py",
    title="Achats",
    icon="🚚",
)

page_lignes_achat = st.Page(
    "streamlit/pages/05_Lignes_Achat.py",
    title="Lignes d'achat",
    icon="🧾",
)

page_ventes = st.Page(
    "streamlit/pages/06_Ventes.py",
    title="Ventes",
    icon="🛒",
)

page_lignes_vente = st.Page(
    "streamlit/pages/07_Lignes_Vente.py",
    title="Lignes de vente",
    icon="📄",
)

page_depenses = st.Page(
    "streamlit/pages/08_Depenses.py",
    title="Dépenses",
    icon="💸",
)

page_pertes = st.Page(
    "streamlit/pages/09_Pertes.py",
    title="Pertes",
    icon="⚠️",
)

page_tresorerie = st.Page(
    "streamlit/pages/10_Tresorerie.py",
    title="Trésorerie",
    icon="🏦",
)

page_inventaire = st.Page(
    "streamlit/pages/11_Inventaire.py",
    title="Inventaire",
    icon="📋",
)

page_rapports = st.Page(
    "streamlit/pages/12_Rapports.py",
    title="Rapports",
    icon="📈",
)

page_dashboard = st.Page(
    "streamlit/pages/13_Dashboard.py",
    title="Dashboard",
    icon="📊",
)

page_administration = st.Page(
    "streamlit/pages/14_Administration.py",
    title="Administration",
    icon="⚙️",
)

page_a_propos = st.Page(
    "streamlit/pages/15_A_Propos.py",
    title="À propos",
    icon="ℹ️",
)


# ============================================================
# 9. CREATION DU MENU DE NAVIGATION
# ============================================================

navigation = st.navigation(
    {
        "Gestion": [
            page_accueil,
            page_produits,
            page_categories,
            page_achats,
            page_lignes_achat,
            page_ventes,
            page_lignes_vente,
        ],
        "Finance": [
            page_depenses,
            page_pertes,
            page_tresorerie,
            page_inventaire,
        ],
        "Analyse": [
            page_rapports,
            page_dashboard,
        ],
        "Administration": [
            page_administration,
            page_a_propos,
        ],
    }
)


# ============================================================
# 10. EXECUTION DE LA PAGE SELECTIONNEE
# ============================================================

navigation.run()


# ============================================================
# 11. PIED DE PAGE ET SAUVEGARDE DE L'INTERFACE
# ============================================================

footer()

save_session_ui_state(st.session_state)
