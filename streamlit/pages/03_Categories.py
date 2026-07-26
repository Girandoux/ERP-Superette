# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 03_Categories.py
# ROLE : Gestion des categories de produits
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
import streamlit as st

# Cette page Streamlit est executee directement et n'expose pas d'API publique.
__all__: list[str] = []
from config.styles import display_dataframe,empty_data_message,info_box,kpi_card,page_title
from utils.categories import create_categorie,delete_categorie,filter_categories_dataframe,get_categories_kpis,list_categories_with_products,search_categories,suggest_code_categorie,update_categorie
from utils.exports import export_rapport,render_export_buttons,render_period_export

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

page_title("Categories","Organisation du catalogue produits par familles")
categories_df=list_categories_with_products()
kpis=get_categories_kpis()

# ============================================================
# 2. INDICATEURS CATEGORIES
# ============================================================

c1,c2,c3=st.columns(3)
with c1:
    kpi_card("Categories",kpis.get("total_categories",0))
with c2:
    kpi_card("Utilisees",kpis.get("categories_utilisees",0))
with c3:
    kpi_card("Vides",kpis.get("categories_vides",0))

# ============================================================
# 3. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_supprimer,tab_export=st.tabs(["Liste","Ajouter","Modifier","Supprimer","Export"])

# ============================================================
# 4. CONSULTATION DES CATEGORIES
# ============================================================

with tab_liste:
    st.subheader("Liste des categories")
    info_box("Les categories structurent le catalogue, simplifient la recherche et rendent les rapports Power BI plus lisibles.")
    keyword=st.text_input("Filtrer",key="categories_filtre")
    filtered=filter_categories_dataframe(categories_df,keyword)
    if filtered.empty:
        empty_data_message("Aucune categorie trouvee.")
    else:
        display_dataframe(filtered,use_container_width=True,hide_index=True)

# ============================================================
# 5. CREATION D'UNE CATEGORIE
# ============================================================

with tab_ajouter:
    st.subheader("Ajouter une categorie")
    info_box("Saisissez le nom de la famille : le code categorie est propose automatiquement pour eviter les doublons et garder une nomenclature claire.")
    nom=st.text_input("Nom categorie",key="new_nom_categorie")
    suggested_code=suggest_code_categorie(nom) if nom else ""
    with st.container(border=True):
        code=st.text_input("Code categorie",value=suggested_code,help="Code propose automatiquement depuis le nom de la categorie.",key="create_categorie_code")
        if suggested_code:
            st.caption(f"Code propose : {suggested_code}")
        description=st.text_area("Description",placeholder="Exemple : boissons gazeuses, produits d'entretien, epicerie...",key="create_categorie_description")
        r1,r2=st.columns(2)
        with r1:
            kpi_card("Code",code or "A definir")
        with r2:
            kpi_card("Nom",nom or "A definir")
        submitted=st.button("Valider et creer la categorie",type="primary",key="btn_create_categorie")
    if submitted:
        if not str(nom or "").strip():
            st.error("Le nom de la categorie est obligatoire.")
        else:
            result=create_categorie(code,nom,description)
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 6. MODIFICATION D'UNE CATEGORIE
# ============================================================

with tab_modifier:
    st.subheader("Modifier une categorie")
    if categories_df.empty:
        empty_data_message("Aucune categorie disponible.")
    else:
        options={f"{row['code_categorie']} - {row['nom_categorie']}":int(row["categorie_id"]) for _,row in categories_df.iterrows()}
        selected=st.selectbox("Categorie",list(options.keys()),key="categorie_update")
        categorie_id=options[selected]
        current=categories_df[categories_df["categorie_id"]==categorie_id].iloc[0].to_dict()
        with st.form("form_update_categorie"):
            code=st.text_input("Code categorie",value=str(current.get("code_categorie","")))
            nom=st.text_input("Nom categorie",value=str(current.get("nom_categorie","")))
            description=st.text_area("Description",value=str(current.get("description") or ""))
            submitted=st.form_submit_button("Enregistrer les modifications",type="primary")
        if submitted:
            result=update_categorie(categorie_id,code,nom,description)
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 7. SUPPRESSION D'UNE CATEGORIE
# ============================================================

with tab_supprimer:
    st.subheader("Supprimer une categorie")
    if categories_df.empty:
        empty_data_message("Aucune categorie disponible.")
    else:
        options={f"{row['code_categorie']} - {row['nom_categorie']}":int(row["categorie_id"]) for _,row in categories_df.iterrows()}
        selected=st.selectbox("Categorie a supprimer",list(options.keys()),key="categorie_delete")
        current=categories_df[categories_df["categorie_id"]==options[selected]].iloc[0].to_dict()
        nb_produits=int(current.get("nb_produits") or current.get("nombre_produits") or 0)
        if nb_produits>0:
            st.warning(f"Suppression bloquee : cette categorie contient encore {nb_produits} produit(s). Deplacez ou desactivez d'abord ces produits.")
        else:
            st.info("Cette categorie semble vide. La suppression est possible si elle n'est liee a aucun produit.")
        if st.button("Supprimer la categorie",type="primary"):
            result=delete_categorie(options[selected])
            st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 8. RECHERCHE ET EXPORT
# ============================================================

with tab_export:
    st.subheader("Recherche et export")
    keyword=st.text_input("Recherche avancee",key="categories_search")
    result=search_categories(keyword) if keyword else categories_df
    if result.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        display_dataframe(result,use_container_width=True,hide_index=True)
        render_export_buttons("categories",result,"categories_search_export")




