# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 09_Pertes.py
# ROLE : Gestion des pertes de stock
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,kpi_card,page_title
from utils.calculs import calcul_valeur_perte
from utils.exports import render_period_export
from utils.helpers import format_money,format_quantity
from utils.pertes import add_pertes_display_columns,create_perte,delete_perte,filter_pertes_dataframe,get_motifs_pertes_options,get_pertes_by_motif,get_pertes_kpis,list_pertes,list_pertes_by_date,search_pertes,update_perte
from utils.produits import get_produits_options

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

page_title("Pertes","Enregistrement des produits perdus, casses ou perimes")
# Une perte represente une sortie de stock sans vente : produit perime,
# casse, vole, donne ou corrige apres inventaire.
pertes_df=add_pertes_display_columns(list_pertes())
kpis=get_pertes_kpis()
motifs=get_motifs_pertes_options()
produits_options=get_produits_options(active_only=True)

# ============================================================
# 2. INDICATEURS DES PERTES
# ============================================================

c1,c2,c3=st.columns(3)
with c1:
    kpi_card("Pertes",kpis.get("total_pertes",0))
with c2:
    kpi_card("Quantite perdue",format_quantity(kpis.get("quantite_perdue",0)))
with c3:
    kpi_card("Valeur perdue",format_money(kpis.get("valeur_perdue",0)))

# ============================================================
# 3. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_analyse,tab_export=st.tabs(["Liste","Ajouter","Modifier","Analyse","Export"])

# ============================================================
# 4. CONSULTATION DES PERTES
# ============================================================

with tab_liste:
    st.subheader("Liste des pertes")
    col1,col2=st.columns([2,1])
    keyword=col1.text_input("Filtrer",key="pertes_filtre")
    motif=col2.selectbox("Motif",["Tous"]+motifs)
    filtered=filter_pertes_dataframe(pertes_df,keyword,motif if motif!="Tous" else None)
    display_dataframe(filtered,use_container_width=True,hide_index=True) if not filtered.empty else empty_data_message("Aucune perte trouvee.")

# ============================================================
# 5. CREATION D'UNE PERTE
# ============================================================

with tab_ajouter:
    st.subheader("Ajouter une perte")
    st.markdown("""
    <div style="border:1px solid #fee2e2;border-left:4px solid #dc2626;border-radius:8px;background:#fffafa;padding:14px 16px;margin:8px 0 18px 0;">
        <strong>Controle des pertes</strong><br>
        Enregistrez uniquement les produits non vendables : perimes, casses, voles, dons ou corrections d'inventaire.
    </div>
    """,unsafe_allow_html=True)
    if not produits_options:
        st.warning("Aucun produit actif disponible.")
    with st.container(border=True):
        col1,col2=st.columns(2)
        with col1:
            date_perte=st.date_input("Date de la perte",value=date.today(),key="create_perte_date")
            produit_label=st.selectbox("Produit concerne",list(produits_options.keys()) or ["Aucun produit"],key="create_perte_produit")
            qte_perte=st.number_input("Quantite perdue",min_value=1,value=1,step=1,key="create_perte_qte")
        with col2:
            motif=st.selectbox("Motif de perte",motifs,key="create_perte_motif")
            valeur_unitaire=st.number_input("Valeur unitaire estimee",min_value=0.0,value=0.0,step=100.0,key="create_perte_valeur_unitaire")
            utilisateur=st.text_input("Utilisateur",value="SYSTEM",key="create_perte_utilisateur")
        # La valeur totale permet de mesurer l'impact financier de la sortie de stock.
        valeur_totale=calcul_valeur_perte(qte_perte,valeur_unitaire)
        col_a,col_b,col_c=st.columns(3)
        with col_a:
            kpi_card("Quantite",format_quantity(qte_perte))
        with col_b:
            kpi_card("Valeur unitaire",format_money(valeur_unitaire))
        with col_c:
            kpi_card("Impact financier",format_money(valeur_totale))
        # Le message depend du motif afin de distinguer perte definitive, don
        # et correction d'inventaire.
        if motif in ["Perime","Casse","Vole"]:
            st.warning("Cette perte diminuera le stock et sera comptabilisee comme perte definitive.")
        elif motif=="Don":
            st.info("Cette sortie sera tracee comme don afin de separer les pertes commerciales des dons.")
        elif motif=="Inventaire":
            st.info("Pour une correction apres cloture, utilisez de preference l'onglet Inventaire > Correction.")
        submitted=st.button("Valider et enregistrer la perte",type="primary",key="btn_create_perte")
    if submitted:
        produit_id=produits_options.get(produit_label)
        if not produit_id:
            st.error("Aucun produit defini. Selectionnez un produit avant d'enregistrer la perte.")
        elif valeur_unitaire<=0:
            st.error("La valeur unitaire doit etre superieure a 0 pour valoriser correctement la perte.")
        else:
            result=create_perte(date_perte,produit_id,qte_perte,motif,valeur_unitaire,utilisateur)
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 6. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier une perte")
    if pertes_df.empty:
        empty_data_message("Aucune perte disponible.")
    else:
        options={f"{row['perte_id']} - {row.get('nom_produit','Produit')} - {row['date_perte']}":int(row["perte_id"]) for _,row in pertes_df.iterrows()}
        selected=st.selectbox("Perte",list(options.keys()))
        perte_id=options[selected]
        current=pertes_df[pertes_df["perte_id"]==perte_id].iloc[0].to_dict()
        with st.form("form_update_perte"):
            col1,col2=st.columns(2)
            with col1:
                date_perte=st.date_input("Date perte",value=current.get("date_perte") or date.today())
                produit_label=st.selectbox("Produit",list(produits_options.keys()) or ["Aucun produit"])
                qte_perte=st.number_input("Quantite perdue",min_value=1,value=int(current.get("qte_perte") or 1),step=1)
            with col2:
                motif=st.selectbox("Motif",motifs,index=motifs.index(current.get("motif_perte")) if current.get("motif_perte") in motifs else 0)
                valeur_unitaire=st.number_input("Valeur unitaire",min_value=0.0,value=float(current.get("valeur_unitaire") or 0),step=100.0)
                utilisateur=st.text_input("Utilisateur",value=str(current.get("utilisateur") or "SYSTEM"))
            submitted=st.form_submit_button("Enregistrer les modifications",type="primary")
        col_a,col_b=st.columns(2)
        if submitted:
            result=update_perte(perte_id,date_perte,produits_options.get(produit_label),qte_perte,motif,valeur_unitaire,utilisateur)
            st.success(result["message"]) if result["success"] else st.error(result["message"])
        with col_b:
            if st.button("Supprimer cette perte"):
                result=delete_perte(perte_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 7. ANALYSE DES PERTES
# ============================================================

with tab_analyse:
    st.subheader("Analyse des pertes")
    by_motif=add_pertes_display_columns(get_pertes_by_motif())
    if by_motif.empty:
        empty_data_message("Aucune analyse disponible.")
    else:
        display_dataframe(by_motif,use_container_width=True,hide_index=True)
    col1,col2=st.columns(2)
    start=col1.date_input("Date debut",value=date.today(),key="perte_start")
    end=col2.date_input("Date fin",value=date.today(),key="perte_end")
    # L'analyse par periode facilite le suivi des pertes recurrentes.
    if st.button("Afficher la periode"):
        result=add_pertes_display_columns(list_pertes_by_date(start,end))
        display_dataframe(result,use_container_width=True,hide_index=True) if not result.empty else empty_data_message("Aucune perte sur cette periode.")

# ============================================================
# 8. EXPORT DES PERTES
# ============================================================

with tab_export:
    st.subheader("Exporter les pertes")
    result_df=add_pertes_display_columns(search_pertes())
    if result_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_period_export("pertes",result_df,"pertes_export","date_perte")
