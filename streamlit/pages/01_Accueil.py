# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 01_Accueil.py
# ROLE : Page d'accueil et vue generale de l'application
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
import streamlit as st

# Cette page Streamlit est executee directement et n'expose pas d'API publique.
__all__: list[str] = []
from config.database import count_all_main_tables,database_information
from config.settings import APP_AUTHOR,APP_VERSION
from config.styles import display_dataframe,empty_data_message,hero_panel,info_box,kpi_card
from utils.dashboard import get_dashboard_cards,get_dashboard_status,load_dashboard_data
from utils.helpers import format_money

# ============================================================
# 1. CHARGEMENT DES DONNEES
# ============================================================

dashboard_data=load_dashboard_data()
dashboard_cards=get_dashboard_cards()
dashboard_status=get_dashboard_status()
db_info=database_information()
status_data=dashboard_status.get("data",{}) if dashboard_status.get("success") else {}

# ============================================================
# 2. PRESENTATION DE L'APPLICATION
# ============================================================

hero_panel(
    "Gestion de Superette",
    "Tableau de bord operationnel pour piloter les ventes, achats, stock, tresorerie et alertes de gestion depuis une interface Streamlit connectee a PostgreSQL.",
    ["Streamlit", "PostgreSQL", "SQLAlchemy", "Power BI", "Tests automatises"]
)

# ============================================================
# 3. INDICATEURS PRINCIPAUX
# ============================================================

st.subheader("Pilotage principal")
info_box("Vue rapide des indicateurs essentiels : ventes, benefice, valeur stock, tresorerie et alertes.")
cols=st.columns(3)
for index,card in enumerate(dashboard_cards[:6]):
    with cols[index%3]:
        kpi_card(card["title"],card["value"])

# ============================================================
# 4. ETAT GENERAL DU SYSTEME
# ============================================================

st.subheader("Etat du systeme")
col1,col2,col3=st.columns([1,1,2])
with col1:
    kpi_card("Statut",status_data.get("status","INDISPONIBLE"))
with col2:
    kpi_card("Alertes stock",status_data.get("alertes_stock",0))
with col3:
    if dashboard_status.get("success"):
        st.success("Application connectee et donnees chargees.")
        info_box("Lecture rapide : si le statut est critique, commencez par les alertes stock et les produits sous minimum.")
    else:
        st.warning("Les donnees du dashboard ne sont pas disponibles.")

# ============================================================
# 5. RACCOURCIS DE NAVIGATION
# ============================================================

st.subheader("Acces rapide")
st.markdown(
    """
    <div class="quick-grid">
        <div class="quick-card"><strong>Catalogue</strong><span>Produits, categories et stock</span></div>
        <div class="quick-card"><strong>Operations</strong><span>Achats, ventes et lignes</span></div>
        <div class="quick-card"><strong>Finance</strong><span>Depenses, pertes et tresorerie</span></div>
        <div class="quick-card"><strong>Analyse</strong><span>Rapports, dashboard et exports</span></div>
    </div>
    """,
    unsafe_allow_html=True
)
c1,c2,c3,c4=st.columns(4)
with c1:
    st.page_link("pages/02_Produits.py",label="Produits")
    st.page_link("pages/03_Categories.py",label="Categories")
with c2:
    st.page_link("pages/04_Achats.py",label="Achats")
    st.page_link("pages/06_Ventes.py",label="Ventes")
with c3:
    st.page_link("pages/08_Depenses.py",label="Depenses")
    st.page_link("pages/10_Tresorerie.py",label="Tresorerie")
with c4:
    st.page_link("pages/12_Rapports.py",label="Rapports")
    st.page_link("pages/13_Dashboard.py",label="Dashboard")

# ============================================================
# 6. APERCUS OPERATIONNELS
# ============================================================

tab_stock,tab_top,tab_tresorerie,tab_tables=st.tabs(["Alertes stock","Top produits","Tresorerie","Tables"])
with tab_stock:
    df=dashboard_data.get("alertes_stock")
    if df is not None and not df.empty:
        display_dataframe(df,use_container_width=True,hide_index=True)
    else:
        empty_data_message("Aucune alerte stock actuellement.")
with tab_top:
    df=dashboard_data.get("top_produits_vendus")
    if df is not None and not df.empty:
        display_dataframe(df,use_container_width=True,hide_index=True)
    else:
        empty_data_message("Aucune vente disponible pour le moment.")
with tab_tresorerie:
    kpis=dashboard_data.get("kpis",{})
    kpi_card("Solde reel caisse",format_money(kpis.get("solde_tresorerie",0)))
    df=dashboard_data.get("flux_tresorerie")
    if df is not None and not df.empty:
        display_dataframe(df,use_container_width=True,hide_index=True)
    else:
        empty_data_message("Aucun mouvement de tresorerie disponible.")
with tab_tables:
    counts=count_all_main_tables()
    if counts:
        display_dataframe({"Table":list(counts.keys()),"Lignes":list(counts.values())},use_container_width=True,hide_index=True)
    else:
        empty_data_message("Aucune table principale detectee.")

# ============================================================
# 7. INFORMATIONS DU SYSTEME
# ============================================================

st.subheader("Informations")
server=f"{db_info.get('host')}:{db_info.get('port')}"
st.markdown(
    f"""
    <div class="system-info">
        <span><strong>Version</strong> {APP_VERSION}</span>
        <span><strong>Base</strong> {db_info.get("database","")}</span>
        <span><strong>Serveur</strong> {server}</span>
        <span><strong>Auteur</strong> {APP_AUTHOR}</span>
    </div>
    """,
    unsafe_allow_html=True
)

