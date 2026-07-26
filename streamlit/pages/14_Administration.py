# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 14_Administration.py
# ROLE : Administration, controle base et imports
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
import streamlit as st
from config.database import count_all_main_tables,database_information,get_tables,test_connection
from config.settings import CSV_DIR,DATA_DIR,REPORTS_DIR
from config.styles import display_dataframe,empty_data_message,info_box,kpi_card,page_title
from utils.imports import check_csv_files,get_import_order,get_import_resume,import_all_tables,import_one_table,preview_csv,reset_import_sequences

# ============================================================
# 1. TITRE ET ETAT DU SYSTEME
# ============================================================

page_title("Administration","Controle technique de la base, des CSV et des imports")
# L'administration verifie d'abord la connexion PostgreSQL et les chemins
# necessaires avant tout controle CSV ou import de donnees.
db_info=database_information()
connected=test_connection()

status_label="Connecte" if connected else "Erreur"
st.markdown(
    f"""
    <div class="admin-info">
        <span><strong>PostgreSQL</strong> {status_label}</span>
        <span><strong>Base</strong> {db_info.get("database","")}</span>
        <span title="{CSV_DIR}"><strong>CSV</strong> {CSV_DIR}</span>
        <span title="{REPORTS_DIR}"><strong>Reports</strong> {REPORTS_DIR}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# 2. ORGANISATION DES ONGLETS
# ============================================================

tab_base,tab_csv,tab_import,tab_tables=st.tabs(["Base de donnees","CSV","Import","Tables"])

# ============================================================
# 3. CONTROLE DE LA BASE DE DONNEES
# ============================================================

with tab_base:
    st.subheader("Connexion PostgreSQL")
    info_box("Cette zone permet de verifier rapidement l'etat technique de l'application avant un import ou une demonstration.")
    c1,c2,c3=st.columns(3)
    with c1:
        kpi_card("Connexion",status_label)
    with c2:
        kpi_card("Base",db_info.get("database",""))
    with c3:
        kpi_card("Serveur",f"{db_info.get('host')}:{db_info.get('port')}")
    if connected:
        st.success("Connexion PostgreSQL active.")
    else:
        st.error("Connexion PostgreSQL impossible.")
    with st.expander("Details techniques PostgreSQL"):
        st.json(db_info)
        st.caption(f"Dossier data : {DATA_DIR}")

# ============================================================
# 4. CONTROLE DES FICHIERS CSV
# ============================================================

with tab_csv:
    st.subheader("Fichiers CSV attendus")
    # Le controle CSV compare les fichiers disponibles avec l'ordre
    # d'import attendu par l'application.
    resume=get_import_resume()
    info_box("Controlez ici que les 13 fichiers CSV attendus existent avant de lancer un import complet.")
    st.caption(f"Dossier CSV : {resume['csv_dir']}")
    files=check_csv_files()["files"]
    rows=[{"table":table,"existe":info["exists"],"lignes":info["rows"],"chemin":info["path"]} for table,info in files.items()]
    found=sum(1 for row in rows if row["existe"])
    c1,c2,c3=st.columns(3)
    with c1:
        kpi_card("CSV trouves",found)
    with c2:
        kpi_card("CSV attendus",len(rows))
    with c3:
        kpi_card("Manquants",len(rows)-found)
    display_dataframe(rows,use_container_width=True,hide_index=True)
    table_preview=st.selectbox("Apercu CSV",get_import_order())
    preview=preview_csv(table_preview,limit=20)
    display_dataframe(preview,use_container_width=True,hide_index=True) if not preview.empty else empty_data_message("CSV introuvable ou vide.")

# ============================================================
# 5. IMPORT ET MAINTENANCE
# ============================================================

with tab_import:
    st.subheader("Import PostgreSQL")
    info_box("L'import complet est une action sensible : il peut vider les tables avant de recharger les CSV selon l'option choisie.")
    table=st.selectbox("Table a importer",get_import_order())
    # L'import cible limite le risque en chargeant une seule table.
    # L'import complet reste isole dans une zone de maintenance.
    with st.container(border=True):
        st.markdown("##### Import cible")
        if st.button("Importer cette table",type="primary"):
            result=import_one_table(table)
            st.success(result["message"]) if result["success"] else st.error(result["message"])
    with st.expander("Import complet et maintenance",expanded=False):
        st.warning("A utiliser seulement apres verification des CSV et de la connexion PostgreSQL.")
        clean_before=st.checkbox("Vider les tables avant import complet",value=True)
        reset_after=st.checkbox("Synchroniser les sequences apres import",value=True)
        col1,col2=st.columns(2)
        # L'import complet peut nettoyer les tables puis resynchroniser
        # les sequences selon les options choisies.
        if col1.button("Import complet"):
            result=import_all_tables(clean_before=clean_before,reset_after=reset_after)
            st.success(result["message"]) if result["success"] else st.error(result["message"])
        if col2.button("Reset sequences"):
            result=reset_import_sequences()
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 6. CONTROLE DES TABLES ET VOLUMES
# ============================================================

with tab_tables:
    st.subheader("Tables et volumes")
    # Le controle final rapproche les tables principales et leurs volumes
    # pour confirmer le resultat des imports.
    counts=count_all_main_tables()
    if counts:
        total_lignes=sum(int(value or 0) for value in counts.values())
        c1,c2=st.columns(2)
        with c1:
            kpi_card("Tables principales",len(counts))
        with c2:
            kpi_card("Lignes chargees",total_lignes)
        display_dataframe({"table":list(counts.keys()),"lignes":list(counts.values())},use_container_width=True,hide_index=True)
    else:
        empty_data_message("Aucune table principale trouvee.")
    tables=get_tables()
    with st.expander("Tables et vues PostgreSQL"):
        display_dataframe(tables,use_container_width=True,hide_index=True) if tables else empty_data_message("Aucune table ou vue detectee.")


