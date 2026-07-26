# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 02_Produits.py
# ROLE : Gestion du catalogue produits
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
import streamlit as st

# Cette page Streamlit est executee directement et n'expose pas d'API publique.
__all__: list[str] = []
from config.styles import display_dataframe,empty_data_message,info_box,kpi_card,page_title
from utils.categories import get_categories_options
from utils.exports import export_rapport,render_export_buttons,render_period_export
from utils.helpers import format_quantity
from utils.produits import add_display_columns,create_produit,can_delete_produit,deactivate_produit,delete_produit,filter_produits_dataframe,get_next_code_produit,get_produits_kpis,get_produits_options,list_produits,search_produits,update_produit

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

page_title("Produits","Creation, modification, recherche et suivi du stock des produits")
categories_options=get_categories_options()
produits_df=add_display_columns(list_produits(active_only=False))
kpis=get_produits_kpis(active_only=False)

# ============================================================
# 2. INDICATEURS PRODUITS
# ============================================================

c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Total produits",kpis.get("total_produits",0))
with c2:
    kpi_card("Produits actifs",kpis.get("produits_actifs",0))
with c3:
    kpi_card("Stock total",format_quantity(kpis.get("stock_total",0)))
with c4:
    kpi_card("Alertes stock",kpis.get("alertes_stock",0))

# ============================================================
# 3. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_rechercher,tab_export=st.tabs(["Liste","Ajouter","Modifier","Rechercher","Export"])

# ============================================================
# 4. CONSULTATION DES PRODUITS
# ============================================================

with tab_liste:
    st.subheader("Liste des produits")
    info_box("Le catalogue produit pilote les achats, les ventes, le stock minimum et les rapports Power BI.")
    col1,col2,col3=st.columns([2,1,1])
    keyword=col1.text_input("Filtrer par mot cle",key="produits_filtre")
    active_only=col2.checkbox("Actifs seulement",value=False)
    categorie_label=col3.selectbox("Categorie",["Toutes"]+list(categories_options.keys()))
    categorie_id=categories_options.get(categorie_label) if categorie_label!="Toutes" else None
    filtered=filter_produits_dataframe(produits_df,keyword=keyword,categorie_id=categorie_id,active_only=active_only)
    if filtered.empty:
        empty_data_message("Aucun produit trouve.")
    else:
        display_dataframe(filtered,use_container_width=True,hide_index=True)

# ============================================================
# 5. CREATION D'UN PRODUIT
# ============================================================

with tab_ajouter:
    st.subheader("Ajouter un produit")
    info_box("Le code produit est propose automatiquement selon la categorie. Vous pouvez le modifier seulement si vous avez une logique de codification precise.")
    with st.container(border=True):
        col1,col2=st.columns(2)
        with col1:
            categorie_label=st.selectbox("Categorie",list(categories_options.keys()) or ["Aucune categorie"],key="create_produit_categorie")
            categorie_id_selected=categories_options.get(categorie_label)
            next_code_produit=get_next_code_produit(categorie_id_selected)
            code=st.text_input("Code produit",value=next_code_produit,help="Code propose automatiquement selon la categorie selectionnee.",key="create_produit_code")
            st.caption(f"Code propose : {next_code_produit}")
            nom=st.text_input("Nom produit",key="create_produit_nom")
            unite=st.selectbox("Unite",["Piece","Carton","Paquet","Bouteille","Canette","Kg","Litre"],key="create_produit_unite")
        with col2:
            qte_par_carton=st.number_input("Quantite par carton",min_value=1,value=1,step=1,key="create_produit_qte_carton")
            stock_min=st.number_input("Stock minimum",min_value=0,value=0,step=1,key="create_produit_stock_min")
            actif=st.checkbox("Produit actif",value=True,key="create_produit_actif")
        st.markdown("##### Resume avant creation")
        r1,r2,r3=st.columns(3)
        with r1:
            kpi_card("Code",code or "A definir")
        with r2:
            kpi_card("Categorie",categorie_label)
        with r3:
            kpi_card("Seuil stock",format_quantity(stock_min))
        submitted=st.button("Valider et creer le produit",type="primary",key="btn_create_produit")
    if submitted:
        if not str(nom or "").strip():
            st.error("Le nom du produit est obligatoire.")
        elif not categorie_id_selected:
            st.error("Veuillez selectionner une categorie valide avant de creer le produit.")
        else:
            result=create_produit(code,nom,categorie_id_selected,unite,qte_par_carton,stock_min,actif)
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 6. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier ou desactiver un produit")
    produits_options=get_produits_options(active_only=False)
    selected=st.selectbox("Produit a modifier",list(produits_options.keys()) or ["Aucun produit"])
    produit_id=produits_options.get(selected)
    if produit_id:
        current=produits_df[produits_df["produit_id"]==produit_id].iloc[0].to_dict()
        with st.form("form_update_produit"):
            col1,col2=st.columns(2)
            with col1:
                code=st.text_input("Code produit",value=str(current.get("code_produit","")))
                nom=st.text_input("Nom produit",value=str(current.get("nom_produit","")))
                current_cat=next((label for label,cid in categories_options.items() if cid==current.get("categorie_id")),None)
                categorie_label=st.selectbox("Categorie",list(categories_options.keys()) or ["Aucune categorie"],index=list(categories_options.keys()).index(current_cat) if current_cat in categories_options else 0)
                unite=st.text_input("Unite",value=str(current.get("unite","Piece")))
            with col2:
                qte_par_carton=st.number_input("Quantite par carton",min_value=1,value=int(current.get("qte_par_carton") or 1),step=1)
                stock_min=st.number_input("Stock minimum",min_value=0,value=int(current.get("stock_min") or 0),step=1)
                actif=st.checkbox("Produit actif",value=bool(current.get("actif",True)))
            save=st.form_submit_button("Enregistrer les modifications",type="primary")
        col_a,col_b=st.columns(2)
        if save:
            result=update_produit(produit_id,code,nom,categories_options.get(categorie_label),unite,qte_par_carton,stock_min,actif)
            st.success(result["message"]) if result["success"] else st.error(result["message"])
        with col_b:
            if st.button("Desactiver le produit",disabled=not bool(current.get("actif",True))):
                result=deactivate_produit(produit_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])
        st.divider()
        delete_check=can_delete_produit(produit_id)
        if delete_check["success"]:
            st.info("Ce produit n'est utilise dans aucune vente, aucun achat, aucune perte et aucun inventaire. La suppression definitive est possible.")
            st.warning("Conseil metier : desactiver reste souvent preferable a supprimer, car cela garde un catalogue historisable.")
            if st.button("Supprimer definitivement le produit",type="primary",key=f"delete_product_{produit_id}"):
                result=delete_produit(produit_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])
        else:
            st.warning(delete_check["message"])

# ============================================================
# 7. RECHERCHE DE PRODUITS
# ============================================================

with tab_rechercher:
    st.subheader("Recherche produit")
    keyword=st.text_input("Code, nom, unite ou categorie",key="produits_search")
    if keyword:
        result=add_display_columns(search_produits(keyword,active_only=False))
        if result.empty:
            empty_data_message("Aucun produit ne correspond a la recherche.")
        else:
            display_dataframe(result,use_container_width=True,hide_index=True)
            render_export_buttons("recherche_produits",result,"recherche_produits")

# ============================================================
# 8. EXPORT DES DONNEES
# ============================================================

with tab_export:
    st.subheader("Exporter les produits")
    if produits_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_export_buttons("produits",produits_df,"produits_export")






