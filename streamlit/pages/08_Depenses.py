# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 08_Depenses.py
# ROLE : Gestion des depenses
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,info_box,kpi_card,page_title
from utils.depenses import add_depenses_display_columns,create_depense,delete_depense,filter_depenses_dataframe,get_categories_depenses_options,get_depenses_by_category,get_depenses_kpis,list_depenses,list_depenses_by_date,search_depenses,update_depense
from utils.exports import render_period_export
from utils.helpers import format_money

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

page_title("Depenses","Suivi des charges et sorties d'exploitation")
# Les depenses representent les sorties d'exploitation hors achats de stock.
# Elles contribuent au suivi des charges et de la tresorerie.
depenses_df=add_depenses_display_columns(list_depenses())
kpis=get_depenses_kpis()
categories=get_categories_depenses_options()

# ============================================================
# 2. INDICATEURS DES DEPENSES
# ============================================================

c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Depenses",kpis.get("total_depenses",0))
with c2:
    kpi_card("Montant total",format_money(kpis.get("montant_total",0)))
with c3:
    kpi_card("Montant moyen",format_money(kpis.get("montant_moyen",0)))
with c4:
    kpi_card("Montant max",format_money(kpis.get("montant_max",0)))

# ============================================================
# 3. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_analyse,tab_export=st.tabs(["Liste","Ajouter","Modifier","Analyse","Export"])

# ============================================================
# 4. CONSULTATION DES DEPENSES
# ============================================================

with tab_liste:
    st.subheader("Liste des depenses")
    col1,col2=st.columns([2,1])
    keyword=col1.text_input("Filtrer",key="depenses_filtre")
    categorie=col2.selectbox("Categorie",["Toutes"]+categories)
    filtered=filter_depenses_dataframe(depenses_df,keyword,categorie if categorie!="Toutes" else None)
    display_dataframe(filtered,use_container_width=True,hide_index=True) if not filtered.empty else empty_data_message("Aucune depense trouvee.")

# ============================================================
# 5. CREATION D'UNE DEPENSE
# ============================================================

with tab_ajouter:
    st.subheader("Ajouter une depense")
    info_box("Enregistrez ici uniquement les charges reelles de la boutique : loyer, transport, salaire, electricite, entretien ou frais divers.")
    # Le formulaire separe les informations comptables de la justification
    # afin de conserver une trace claire de chaque sortie.
    with st.container(border=True):
        col1,col2=st.columns(2)
        with col1:
            date_depense=st.date_input("Date de la depense",value=date.today(),key="create_depense_date")
            categorie=st.selectbox("Categorie de charge",categories,key="create_depense_categorie")
            montant=st.number_input("Montant de la depense",min_value=0.0,value=0.0,step=100.0,key="create_depense_montant")
        with col2:
            motif=st.text_area("Motif / justification",placeholder="Exemple : paiement facture electricite, transport marchandise...",key="create_depense_motif")
            utilisateur=st.text_input("Utilisateur",value="SYSTEM",key="create_depense_utilisateur")
        st.markdown("##### Resume avant validation")
        r1,r2,r3=st.columns(3)
        with r1:
            kpi_card("Categorie",categorie or "Non definie")
        with r2:
            kpi_card("Impact caisse",format_money(montant))
        with r3:
            kpi_card("Utilisateur",utilisateur or "SYSTEM")
        submitted=st.button("Valider et enregistrer la depense",type="primary",key="btn_create_depense")
    if submitted:
        if montant<=0:
            st.error("Le montant de la depense doit etre superieur a 0 FCFA.")
        elif not str(motif or "").strip():
            st.error("Veuillez ajouter un motif pour garder une trace claire de la depense.")
        else:
            # Les montants importants sont signales pour encourager la verification
            # de la piece justificative sans bloquer l'enregistrement.
            if montant>=100000:
                st.warning("Depense importante enregistree : verifiez que la piece justificative est disponible.")
            result=create_depense(date_depense,categorie,montant,motif,utilisateur)
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 6. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier une depense")
    if depenses_df.empty:
        empty_data_message("Aucune depense disponible.")
    else:
        options={f"{row['depense_id']} - {row['date_depense']} - {row['categorie_depense']}":int(row["depense_id"]) for _,row in depenses_df.iterrows()}
        selected=st.selectbox("Depense",list(options.keys()))
        depense_id=options[selected]
        current=depenses_df[depenses_df["depense_id"]==depense_id].iloc[0].to_dict()
        with st.form("form_update_depense"):
            col1,col2=st.columns(2)
            with col1:
                date_depense=st.date_input("Date depense",value=current.get("date_depense") or date.today())
                categorie=st.selectbox("Categorie",categories,index=categories.index(current.get("categorie_depense")) if current.get("categorie_depense") in categories else 0)
                montant=st.number_input("Montant",min_value=0.0,value=float(current.get("montant") or 0),step=100.0)
            with col2:
                motif=st.text_area("Motif",value=str(current.get("motif") or ""))
                utilisateur=st.text_input("Utilisateur",value=str(current.get("utilisateur") or "SYSTEM"))
            submitted=st.form_submit_button("Enregistrer les modifications",type="primary")
        col_a,col_b=st.columns(2)
        if submitted:
            result=update_depense(depense_id,date_depense,categorie,montant,motif,utilisateur)
            st.success(result["message"]) if result["success"] else st.error(result["message"])
        with col_b:
            if st.button("Supprimer cette depense"):
                result=delete_depense(depense_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 7. ANALYSE DES DEPENSES
# ============================================================

with tab_analyse:
    st.subheader("Analyse des depenses")
    info_box("Cette vue aide a identifier les postes de charge les plus lourds et a controler les sorties de caisse par periode.")
    by_category=add_depenses_display_columns(get_depenses_by_category())
    if by_category.empty:
        empty_data_message("Aucune analyse disponible.")
    else:
        display_dataframe(by_category,use_container_width=True,hide_index=True)
    col1,col2=st.columns(2)
    start=col1.date_input("Date debut",value=date.today(),key="depense_start")
    end=col2.date_input("Date fin",value=date.today(),key="depense_end")
    # L'analyse par periode permet de rapprocher les charges des sorties de caisse.
    if st.button("Afficher la periode"):
        result=add_depenses_display_columns(list_depenses_by_date(start,end))
        display_dataframe(result,use_container_width=True,hide_index=True) if not result.empty else empty_data_message("Aucune depense sur cette periode.")

# ============================================================
# 8. EXPORT DES DEPENSES
# ============================================================

with tab_export:
    st.subheader("Exporter les depenses")
    result_df=add_depenses_display_columns(search_depenses())
    if result_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_period_export("depenses",result_df,"depenses_export","date_depense")
