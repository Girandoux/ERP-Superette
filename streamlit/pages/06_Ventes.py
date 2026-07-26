# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 06_Ventes.py
# ROLE : Gestion des ventes
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,kpi_card,page_title
from database.vendeurs_db import get_all_vendeurs
from utils.exports import render_export_buttons, render_period_export
from utils.helpers import format_money
from utils.ventes import add_ventes_display_columns,create_vente,delete_vente,get_ventes_kpis,list_ventes,list_ventes_by_date,search_ventes,update_vente

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

page_title("Ventes","Creation et suivi des ventes clients")
# La vente contient l'en-tete de l'operation. Les lignes de vente ajoutent
# les produits, recalculent le total et diminuent le stock.
ventes_df=add_ventes_display_columns(list_ventes())
kpis=get_ventes_kpis()
vendeurs_df=get_all_vendeurs()
vendeurs_options={row["nom_vendeur"]:int(row["vendeur_id"]) for _,row in vendeurs_df.iterrows()} if not vendeurs_df.empty else {}

# ============================================================
# 2. INDICATEURS DES VENTES
# ============================================================

c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Ventes",kpis.get("total_ventes",0))
with c2:
    kpi_card("Chiffre d'affaires",format_money(kpis.get("chiffre_affaires",0)))
with c3:
    kpi_card("Ticket moyen",format_money(kpis.get("ticket_moyen",0)))
with c4:
    kpi_card("Vente max",format_money(kpis.get("vente_max",0)))

# ============================================================
# 3. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_rechercher,tab_export=st.tabs(["Liste","Nouvelle vente","Modifier","Rechercher","Export"])

# ============================================================
# 4. CONSULTATION DES VENTES
# ============================================================

with tab_liste:
    st.subheader("Historique des ventes")
    if ventes_df.empty:
        empty_data_message("Aucune vente disponible.")
    else:
        display_dataframe(ventes_df,use_container_width=True,hide_index=True)

# ============================================================
# 5. CREATION D'UNE VENTE
# ============================================================

with tab_ajouter:
    st.subheader("Nouvelle vente")
    if not vendeurs_options:
        st.warning("Aucun vendeur disponible. Creez d'abord les vendeurs.")
    # Le total n'est pas saisi ici : il depend des lignes de vente rattachees.
    with st.form("form_create_vente",clear_on_submit=True):
        col1,col2=st.columns(2)
        with col1:
            date_vente=st.date_input("Date de vente",value=date.today())
            vendeur_label=st.selectbox("Vendeur",list(vendeurs_options.keys()) or ["Aucun vendeur"])
        with col2:
            st.info("Le total vente sera recalcule automatiquement avec les lignes de vente.")
        submitted=st.form_submit_button("Enregistrer la vente",type="primary")
    if submitted:
        result=create_vente(date_vente,vendeurs_options.get(vendeur_label))
        st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 6. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier une vente")
    if ventes_df.empty:
        empty_data_message("Aucune vente disponible.")
    else:
        options={f"Vente {row['vente_id']} - {row['date_vente']}":int(row["vente_id"]) for _,row in ventes_df.iterrows()}
        selected=st.selectbox("Vente",list(options.keys()))
        vente_id=options[selected]
        current=ventes_df[ventes_df["vente_id"]==vente_id].iloc[0].to_dict()
        with st.form("form_update_vente"):
            col1,col2=st.columns(2)
            with col1:
                date_vente=st.date_input("Date de vente",value=current.get("date_vente") or date.today())
            with col2:
                current_vendeur=next((label for label,vid in vendeurs_options.items() if vid==current.get("vendeur_id")),None)
                vendeur_label=st.selectbox("Vendeur",list(vendeurs_options.keys()) or ["Aucun vendeur"],index=list(vendeurs_options.keys()).index(current_vendeur) if current_vendeur in vendeurs_options else 0)
            submitted=st.form_submit_button("Enregistrer les modifications",type="primary")
        col_a,col_b=st.columns(2)
        if submitted:
            result=update_vente(vente_id,date_vente,vendeurs_options.get(vendeur_label))
            st.success(result["message"]) if result["success"] else st.error(result["message"])
        with col_b:
            if st.button("Supprimer cette vente"):
                result=delete_vente(vente_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 7. RECHERCHE DES VENTES
# ============================================================

with tab_rechercher:
    st.subheader("Recherche")
    col1,col2,col3=st.columns(3)
    keyword=col1.text_input("ID vente ou vendeur")
    start=col2.date_input("Date debut",value=date.today(),key="vente_start")
    end=col3.date_input("Date fin",value=date.today(),key="vente_end")
    if "ventes_search_result" not in st.session_state:
        st.session_state["ventes_search_result"]=None
    # Le resultat est conserve dans la session pour rester visible apres l'action.
    if st.button("Rechercher par periode",key="search_ventes_period"):
        st.session_state["ventes_search_result"]=add_ventes_display_columns(list_ventes_by_date(start,end))
    elif keyword:
        st.session_state["ventes_search_result"]=add_ventes_display_columns(search_ventes(keyword))
    result=st.session_state["ventes_search_result"]
    if result is not None:
        if result.empty:
            empty_data_message("Aucune vente trouvee.")
        else:
            display_dataframe(result,use_container_width=True,hide_index=True)
            render_export_buttons("recherche_ventes",result,"recherche_ventes")

# ============================================================
# 8. EXPORT DES VENTES
# ============================================================

with tab_export:
    st.subheader("Exporter les ventes")
    if ventes_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_period_export("ventes",ventes_df,"ventes_export","date_vente")
