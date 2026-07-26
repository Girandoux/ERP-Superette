# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 04_Achats.py
# ROLE : Gestion des factures d'achat
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,info_box,kpi_card,page_title
from database.acheteurs_db import get_all_acheteurs
from utils.achats import add_achats_display_columns,create_achat,delete_achat,get_achats_kpis,get_next_numero_facture,list_achats,list_achats_by_date,search_achats,update_achat
from utils.exports import render_export_buttons, render_period_export
from utils.helpers import format_money

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

page_title("Achats","Creation et suivi des factures fournisseurs")
# Une facture represente l'en-tete de l'achat. Les produits sont ajoutes
# ensuite dans les lignes d'achat, qui alimentent le stock et le total.
achats_df=add_achats_display_columns(list_achats())
kpis=get_achats_kpis()
acheteurs_df=get_all_acheteurs()
acheteurs_options={row["nom_acheteur"]:int(row["acheteur_id"]) for _,row in acheteurs_df.iterrows()} if not acheteurs_df.empty else {}
type_achat_options=["Achat fournisseur","Stock initial","Retour fournisseur","Correction"]
next_numero_facture=get_next_numero_facture()

# ============================================================
# 2. INDICATEURS DES ACHATS
# ============================================================

c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Factures",kpis.get("total_achats",0))
with c2:
    kpi_card("Total factures",format_money(kpis.get("montant_total",0)))
with c3:
    kpi_card("Montant moyen",format_money(kpis.get("montant_moyen",0)))
with c4:
    kpi_card("Montant max",format_money(kpis.get("montant_max",0)))

# ============================================================
# 3. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_rechercher,tab_export=st.tabs(["Liste","Nouvelle facture","Modifier","Rechercher","Export"])

# ============================================================
# 4. CONSULTATION DES FACTURES
# ============================================================

with tab_liste:
    st.subheader("Historique des achats")
    info_box("Une facture d'achat contient l'en-tete fournisseur. Le montant reel est recalcule automatiquement avec les lignes d'achat et les frais d'enlevement.")
    if achats_df.empty:
        empty_data_message("Aucune facture d'achat disponible.")
    else:
        display_dataframe(achats_df,use_container_width=True,hide_index=True)

# ============================================================
# 5. CREATION D'UNE FACTURE
# ============================================================

with tab_ajouter:
    st.subheader("Nouvelle facture")
    info_box("Creez d'abord la facture, puis ajoutez les produits dans la page Lignes d'achat. Le total facture suivra automatiquement les lignes saisies.")
    if not acheteurs_options:
        st.warning("Aucun acheteur disponible. Creez d'abord les acheteurs.")
    # Le formulaire separe l'identification de la facture des informations
    # financieres afin de faciliter la saisie.
    with st.container(border=True):
        col1,col2=st.columns(2)
        with col1:
            numero=st.text_input("Numero de facture",value=next_numero_facture,help="Numero propose automatiquement selon le dernier numero existant.",key="create_achat_numero")
            st.caption(f"Prochain numero propose : {next_numero_facture}")
            date_achat=st.date_input("Date d'achat",value=date.today(),key="create_achat_date")
            acheteur_label=st.selectbox("Acheteur",list(acheteurs_options.keys()) or ["Aucun acheteur"],key="create_achat_acheteur")
        with col2:
            type_achat=st.selectbox("Type d'achat",type_achat_options,key="create_achat_type")
            frais=st.number_input("Frais d'enlevement",min_value=0.0,value=0.0,step=100.0,key="create_achat_frais")
            st.info("Le total facture est recalcule automatiquement avec les lignes d'achat.")
        st.markdown("##### Resume avant creation")
        r1,r2,r3=st.columns(3)
        with r1:
            kpi_card("Facture",numero or next_numero_facture)
        with r2:
            kpi_card("Acheteur",acheteur_label)
        with r3:
            kpi_card("Frais",format_money(frais))
        submitted=st.button("Valider et creer la facture",type="primary",key="btn_create_achat")
    if submitted:
        if not acheteurs_options.get(acheteur_label):
            st.error("Veuillez selectionner un acheteur valide avant de creer la facture.")
        elif not str(numero or "").strip():
            st.error("Le numero de facture est obligatoire.")
        else:
            result=create_achat(date_achat,numero,acheteurs_options.get(acheteur_label),frais,type_achat)
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 6. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier une facture")
    if achats_df.empty:
        empty_data_message("Aucune facture disponible.")
    else:
        options={f"{row['numero_facture']} - {row['date_achat']}":int(row["achat_id"]) for _,row in achats_df.iterrows()}
        selected=st.selectbox("Facture",list(options.keys()))
        achat_id=options[selected]
        current=achats_df[achats_df["achat_id"]==achat_id].iloc[0].to_dict()
        with st.form("form_update_achat"):
            col1,col2=st.columns(2)
            with col1:
                numero=st.text_input("Numero de facture",value=str(current.get("numero_facture","")))
                date_achat=st.date_input("Date d'achat",value=current.get("date_achat") or date.today())
            with col2:
                current_acheteur=next((label for label,aid in acheteurs_options.items() if aid==current.get("acheteur_id")),None)
                acheteur_label=st.selectbox("Acheteur",list(acheteurs_options.keys()) or ["Aucun acheteur"],index=list(acheteurs_options.keys()).index(current_acheteur) if current_acheteur in acheteurs_options else 0)
                current_type=str(current.get("type_achat") or "Achat fournisseur")
                type_achat=st.selectbox("Type d'achat",type_achat_options,index=type_achat_options.index(current_type) if current_type in type_achat_options else 0)
                frais=st.number_input("Frais d'enlevement",min_value=0.0,value=float(current.get("frais_enlevement") or 0),step=100.0)
            submitted=st.form_submit_button("Enregistrer les modifications",type="primary")
        col_a,col_b=st.columns(2)
        if submitted:
            result=update_achat(achat_id,date_achat,numero,acheteurs_options.get(acheteur_label),frais,type_achat)
            st.success(result["message"]) if result["success"] else st.error(result["message"])
        with col_b:
            if st.button("Supprimer cette facture"):
                result=delete_achat(achat_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 7. RECHERCHE DES ACHATS
# ============================================================

with tab_rechercher:
    st.subheader("Recherche")
    col1,col2,col3=st.columns(3)
    keyword=col1.text_input("Facture ou acheteur")
    start=col2.date_input("Date debut",value=date.today(),key="achat_start")
    end=col3.date_input("Date fin",value=date.today(),key="achat_end")
    if "achats_search_result" not in st.session_state:
        st.session_state["achats_search_result"]=None
    # Le dernier resultat reste memorise pendant la navigation dans la page.
    if st.button("Rechercher par periode",key="search_achats_period"):
        st.session_state["achats_search_result"]=add_achats_display_columns(list_achats_by_date(start,end))
    elif keyword:
        st.session_state["achats_search_result"]=add_achats_display_columns(search_achats(keyword))
    result=st.session_state["achats_search_result"]
    if result is not None:
        if result.empty:
            empty_data_message("Aucun achat trouve.")
        else:
            display_dataframe(result,use_container_width=True,hide_index=True)
            render_export_buttons("recherche_achats",result,"recherche_achats")

# ============================================================
# 8. EXPORT DES ACHATS
# ============================================================

with tab_export:
    st.subheader("Exporter les achats")
    if achats_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_period_export("achats",achats_df,"achats_export","date_achat")
