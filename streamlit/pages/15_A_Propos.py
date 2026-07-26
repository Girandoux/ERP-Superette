# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 15_A_Propos.py
# ROLE : Informations sur l'application
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
import streamlit as st
from config.settings import APP_AUTHOR,APP_NAME,APP_VERSION,APP_YEAR,BASE_DIR,DATA_DIR,DOCS_DIR,POWERBI_DIR,REPORTS_DIR
from config.styles import hero_panel

# ============================================================
# 1. PRESENTATION DU PROJET
# ============================================================

# Cette page presente le projet, sa valeur metier, son architecture
# et les technologies mobilisees sans executer de logique transactionnelle.
hero_panel(
    "A propos du projet",
    "Gestion de Superette est une application de gestion commerciale construite pour demontrer une architecture complete : interface Streamlit, base PostgreSQL, imports CSV, tableaux analytiques, exports et tests automatises.",
    ["Projet portfolio", "Data app", "PostgreSQL", "Power BI", "Python"]
)

st.markdown(
    f"""
    <div class="system-info">
        <span><strong>Application</strong> {APP_NAME}</span>
        <span><strong>Version</strong> {APP_VERSION}</span>
        <span><strong>Annee</strong> {APP_YEAR}</span>
        <span><strong>Auteur</strong> {APP_AUTHOR}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 2. VALEUR TECHNIQUE ET FONCTIONNELLE
# ============================================================

st.subheader("Ce que le projet demontre")
st.markdown(
    """
    <div class="module-grid">
        <div class="module-card"><h4>Application metier</h4><p>CRUD complet pour produits, categories, achats, ventes, depenses, pertes, inventaire et tresorerie.</p></div>
        <div class="module-card"><h4>Base de donnees</h4><p>Modele PostgreSQL structure, contraintes, vues, fonctions, triggers et indexes pour fiabiliser les donnees.</p></div>
        <div class="module-card"><h4>Analyse & reporting</h4><p>Dashboard Streamlit, rapports exportables, requetes analytiques et preparation Power BI.</p></div>
        <div class="module-card"><h4>Qualite logicielle</h4><p>Modules separes, couche database, couche utils, pages Streamlit et tests automatises avec pytest.</p></div>
        <div class="module-card"><h4>Automatisation</h4><p>Import CSV, synchronisation du stock, sequences PostgreSQL et calculs automatiques de caisse et factures.</p></div>
        <div class="module-card"><h4>Presentation GitHub</h4><p>Structure claire, documentation, scripts SQL, donnees d'exemple, architecture lisible et evolutive.</p></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 3. UTILITE POUR LA SUPERETTE
# ============================================================

st.subheader("Pourquoi ce projet est utile pour une superette")
st.markdown(
    """
    <div class="module-grid">
        <div class="module-card"><h4>Decisions plus rapides</h4><p>Le gerant visualise les ventes, les produits sous stock minimum, les pertes et la tresorerie sans ouvrir plusieurs fichiers.</p></div>
        <div class="module-card"><h4>Controle des ecarts</h4><p>Les inventaires, pertes et corrections permettent de garder une trace des differences entre stock theorique et stock physique.</p></div>
        <div class="module-card"><h4>Base pour la BI</h4><p>Les tables et vues SQL preparent une exploitation Power BI propre pour suivre la performance commerciale.</p></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 4. MODULES FONCTIONNELS
# ============================================================

st.subheader("Modules fonctionnels")
st.markdown(
    """
    <div class="quick-grid">
        <div class="quick-card"><strong>Catalogue</strong><span>Produits, categories, codes automatiques et stock minimum</span></div>
        <div class="quick-card"><strong>Operations</strong><span>Achats, lignes d'achat, ventes et lignes de vente</span></div>
        <div class="quick-card"><strong>Finance</strong><span>Depenses, pertes, tresorerie et solde reel caisse</span></div>
        <div class="quick-card"><strong>Analyse</strong><span>Dashboard, rapports, exports et preparation Power BI</span></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 5. TECHNOLOGIES UTILISEES
# ============================================================

st.subheader("Technologies utilisees")
st.markdown(
    """
    <div class="system-info">
        <span><strong>Python</strong> logique applicative</span>
        <span><strong>Streamlit</strong> interface web</span>
        <span><strong>PostgreSQL</strong> base relationnelle</span>
        <span><strong>SQLAlchemy</strong> acces aux donnees</span>
        <span><strong>Pandas</strong> import et analyse</span>
        <span><strong>Plotly</strong> visualisations</span>
        <span><strong>pytest</strong> tests automatises</span>
        <span><strong>Power BI</strong> reporting externe</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 6. CHEMINS DU PROJET
# ============================================================

# Les chemins affiches facilitent le controle de la structure du projet
# pendant une demonstration ou une revue technique.
with st.expander("Chemins du projet"):
    st.code(f"Projet   : {BASE_DIR}")
    st.code(f"Data     : {DATA_DIR}")
    st.code(f"Reports  : {REPORTS_DIR}")
    st.code(f"Docs     : {DOCS_DIR}")
    st.code(f"Power BI : {POWERBI_DIR}")

# ============================================================
# 7. FEUILLE DE ROUTE
# ============================================================

# La feuille de route resume l'evolution fonctionnelle prevue
# sans modifier le comportement actuel de l'application.
with st.expander("Feuille de route"):
    st.write("Version 1 : Application Streamlit et CRUD principal.")
    st.write("Version 2 : PostgreSQL, rapports avances et Power BI.")
    st.write("Version 3 : Analytics, IA et Machine Learning.")
