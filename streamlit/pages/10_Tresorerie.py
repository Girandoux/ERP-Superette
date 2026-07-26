# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 10_Tresorerie.py
# ROLE : Gestion des mouvements de tresorerie
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,info_box,kpi_card,page_title
from utils.exports import render_period_export
from utils.helpers import format_money
from utils.tresorerie import add_tresorerie_display_columns,create_mouvement,delete_mouvement,filter_tresorerie_dataframe,get_monthly_tresorerie,get_mouvements_by_type,get_tresorerie_kpis,get_types_mouvements_options,list_mouvements,list_mouvements_by_date,search_mouvements,update_mouvement

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

# Le suivi distingue les entrees et les sorties afin de calculer
# un solde de caisse coherent avec les mouvements enregistres.
page_title("Tresorerie","Suivi des entrees, sorties et solde reel de caisse")
mouvements_df=add_tresorerie_display_columns(list_mouvements())
kpis=get_tresorerie_kpis()
types=get_types_mouvements_options()

# ============================================================
# 2. CONSTANTES ET FONCTIONS D'AIDE
# ============================================================

__all__ = [
    "get_mouvement_sens",
    "get_mouvement_impact",
]

ENTREE_TYPES={"Apport","Retrait_Banque","Correction"}
SORTIE_TYPES={"Retrait","Depot_Banque"}

def get_mouvement_sens(type_mouvement):
    """Retourne le sens comptable du mouvement pour l'affichage."""
    if type_mouvement in SORTIE_TYPES:
        return "Sortie"
    if type_mouvement in ENTREE_TYPES:
        return "Entree"
    return "Controle"

def get_mouvement_impact(type_mouvement,montant):
    """Formate l'impact du mouvement sur le solde de caisse."""
    if type_mouvement in SORTIE_TYPES:
        return f"- {format_money(montant)}"
    if type_mouvement in ENTREE_TYPES:
        return f"+ {format_money(montant)}"
    return format_money(montant)

# ============================================================
# 3. INDICATEURS DE TRESORERIE
# ============================================================

c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Mouvements",kpis.get("total_mouvements",0))
with c2:
    kpi_card("Entrees reelles",kpis.get("entrees_reelles_affiche",format_money(kpis.get("entrees_reelles",0))))
with c3:
    kpi_card("Sorties reelles",kpis.get("sorties_reelles_affiche",format_money(kpis.get("sorties_reelles",0))))
with c4:
    kpi_card("Solde reel caisse",kpis.get("solde_reel_caisse_affiche",format_money(kpis.get("solde_reel_caisse",0))))

# ============================================================
# 4. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_analyse,tab_export=st.tabs(["Liste","Ajouter","Modifier","Analyse","Export"])

# ============================================================
# 5. CONSULTATION DES MOUVEMENTS
# ============================================================

with tab_liste:
    st.subheader("Liste des mouvements")
    col1,col2=st.columns([2,1])
    keyword=col1.text_input("Filtrer",key="tresorerie_filtre")
    type_filter=col2.selectbox("Type",["Tous"]+types)
    filtered=filter_tresorerie_dataframe(mouvements_df,keyword,type_filter if type_filter!="Tous" else None)
    display_dataframe(filtered,use_container_width=True,hide_index=True) if not filtered.empty else empty_data_message("Aucun mouvement trouve.")

# ============================================================
# 6. CREATION D'UN MOUVEMENT
# ============================================================

with tab_ajouter:
    st.subheader("Ajouter un mouvement")
    info_box("Les mouvements de tresorerie manuels doivent rester justifies : apport, retrait, depot banque, retrait banque ou correction de caisse.")
    # Le formulaire separe les informations du mouvement
    # de sa description justificative.
    with st.container(border=True):
        col1,col2=st.columns(2)
        with col1:
            date_mouvement=st.date_input("Date du mouvement",value=date.today(),key="create_mouvement_date")
            type_mouvement=st.selectbox("Type de mouvement",types,key="create_mouvement_type")
            montant=st.number_input("Montant du mouvement",min_value=0.0,value=0.0,step=100.0,key="create_mouvement_montant")
        with col2:
            description=st.text_area("Description / justification",placeholder="Exemple : apport proprietaire, depot banque, correction caisse...",key="create_mouvement_description")
            utilisateur=st.text_input("Utilisateur",value="SYSTEM",key="create_mouvement_utilisateur")
        st.markdown("##### Resume avant validation")
        r1,r2,r3=st.columns(3)
        with r1:
            kpi_card("Sens",get_mouvement_sens(type_mouvement))
        with r2:
            kpi_card("Impact caisse",get_mouvement_impact(type_mouvement,montant))
        with r3:
            kpi_card("Utilisateur",utilisateur or "SYSTEM")
        submitted=st.button("Valider le mouvement de caisse",type="primary",key="btn_create_mouvement")
    if submitted:
        if montant<=0:
            st.error("Le montant du mouvement doit etre superieur a 0 FCFA.")
        elif not str(description or "").strip():
            st.error("Veuillez ajouter une description pour justifier ce mouvement de caisse.")
        else:
            result=create_mouvement(date_mouvement,type_mouvement,montant,description,utilisateur)
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 7. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier un mouvement")
    if mouvements_df.empty:
        empty_data_message("Aucun mouvement disponible.")
    else:
        options={f"{row['mouvement_id']} - {row['date_mouvement']} - {row['type_mouvement']}":int(row["mouvement_id"]) for _,row in mouvements_df.iterrows()}
        selected=st.selectbox("Mouvement",list(options.keys()))
        mouvement_id=options[selected]
        current=mouvements_df[mouvements_df["mouvement_id"]==mouvement_id].iloc[0].to_dict()
        with st.form("form_update_mouvement"):
            col1,col2=st.columns(2)
            with col1:
                date_mouvement=st.date_input("Date mouvement",value=current.get("date_mouvement") or date.today())
                type_mouvement=st.selectbox("Type mouvement",types,index=types.index(current.get("type_mouvement")) if current.get("type_mouvement") in types else 0)
                montant=st.number_input("Montant",min_value=0.0,value=float(current.get("montant") or 0),step=100.0)
            with col2:
                description=st.text_area("Description",value=str(current.get("description") or ""))
                utilisateur=st.text_input("Utilisateur",value=str(current.get("utilisateur") or "SYSTEM"))
            submitted=st.form_submit_button("Enregistrer les modifications",type="primary")
        col_a,col_b=st.columns(2)
        if submitted:
            result=update_mouvement(mouvement_id,date_mouvement,type_mouvement,montant,description,utilisateur)
            st.success(result["message"]) if result["success"] else st.error(result["message"])
        with col_b:
            if st.button("Supprimer ce mouvement"):
                result=delete_mouvement(mouvement_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 8. ANALYSE DE TRESORERIE
# ============================================================

with tab_analyse:
    st.subheader("Analyse de tresorerie")
    info_box("Comparez les mouvements manuels avec le solde reel de caisse pour detecter rapidement les ecarts de gestion.")
    # L'analyse rapproche les mouvements par type, leur evolution mensuelle
    # et le detail de la periode choisie.
    by_type=add_tresorerie_display_columns(get_mouvements_by_type())
    monthly=get_monthly_tresorerie()
    if not by_type.empty:
        display_dataframe(by_type,use_container_width=True,hide_index=True)
    else:
        empty_data_message("Aucune analyse par type disponible.")
    if not monthly.empty:
        display_dataframe(monthly,use_container_width=True,hide_index=True)
    col1,col2=st.columns(2)
    start=col1.date_input("Date debut",value=date.today(),key="tresorerie_start")
    end=col2.date_input("Date fin",value=date.today(),key="tresorerie_end")
    if st.button("Afficher la periode"):
        result=add_tresorerie_display_columns(list_mouvements_by_date(start,end))
        display_dataframe(result,use_container_width=True,hide_index=True) if not result.empty else empty_data_message("Aucun mouvement sur cette periode.")

# ============================================================
# 9. EXPORT DE LA TRESORERIE
# ============================================================

with tab_export:
    st.subheader("Exporter la tresorerie")
    result_df=add_tresorerie_display_columns(search_mouvements())
    if result_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_period_export("tresorerie",result_df,"tresorerie_export","date_mouvement")
