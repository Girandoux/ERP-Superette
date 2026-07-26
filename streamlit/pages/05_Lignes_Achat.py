# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 05_Lignes_Achat.py
# ROLE : Gestion des lignes de factures d'achat
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,info_box,kpi_card,page_title
from utils.achats import add_achats_display_columns,create_ligne_achat,delete_ligne_achat,list_achats,list_lignes_achat,list_lignes_achat_incoherentes,search_lignes_achat,update_ligne_achat
from utils.calculs import calcul_ligne_achat
from utils.exports import render_export_buttons, render_period_export
from utils.helpers import date_to_str,format_money,format_quantity,get_ui_state,normalize_text,parse_date,set_ui_state,to_float,to_int
from utils.produits import get_produits_options

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

page_title("Lignes d'achat","Ajout et suivi des produits achetes par facture")
# Une ligne d'achat relie une facture a un produit. Son enregistrement
# met a jour les quantites, le cout unitaire et le stock selon la logique metier.
lignes_df=add_achats_display_columns(list_lignes_achat())
incoherences_df=list_lignes_achat_incoherentes()
achats_df=list_achats()
produits_options=get_produits_options(active_only=True)
achats_options={f"{row['numero_facture']} - {row['date_achat']}":int(row["achat_id"]) for _,row in achats_df.iterrows()} if not achats_df.empty else {}
produits_labels=list(produits_options.keys())
achats_labels=list(achats_options.keys())
last_form=get_ui_state("last_ligne_achat_form",{}) or {}

# ============================================================
# 2. FONCTIONS D'AIDE POUR LES FORMULAIRES
# ============================================================

__all__ = [
    "get_default_index",
    "get_filtered_product_labels",
    "product_selectbox",
    "get_last_ligne_achat_values",
    "save_last_ligne_achat_form",
    "render_line_summary",
]

def get_default_index(options:dict[str,int],saved_id:int|None)->int:
    """Retourne l'index correspondant au dernier identifiant memorise."""
    labels=list(options.keys())
    if not labels:
        return 0
    for index,label in enumerate(labels):
        if options.get(label)==saved_id:
            return index
    return 0

def get_filtered_product_labels(filter_text:str="")->list[str]:
    """Filtre les produits par code ou nom saisi."""
    keyword=normalize_text(filter_text)
    if not keyword:
        return produits_labels
    return [label for label in produits_labels if keyword in normalize_text(label)]

def product_selectbox(label:str,key:str,filter_text:str="",selected_id:int|None=None)->str:
    """Affiche une liste Produit filtree; le filtre choisit directement le premier resultat."""
    keyword=normalize_text(filter_text)
    choices=get_filtered_product_labels(filter_text) or ["Aucun produit"]
    if not keyword and selected_id and all(produits_options.get(item)!=selected_id for item in choices):
        current_label=next((item for item in produits_labels if produits_options.get(item)==selected_id),None)
        if current_label:
            choices=[current_label]+choices
    valid_options={item:produits_options.get(item) for item in choices if item in produits_options}
    index=get_default_index(valid_options,selected_id) if valid_options and not keyword else 0
    widget_key=f"{key}_{keyword}" if keyword else key
    return st.selectbox(label,choices,index=index,key=widget_key,help="Tapez dans Filtrer produit pour reduire cette liste.")
def get_last_ligne_achat_values(produit_id:int|None)->dict:
    """Retourne les valeurs de la derniere ligne d'achat d'un produit."""
    if not produit_id or lignes_df.empty or "produit_id" not in lignes_df.columns:
        return {}
    history=lignes_df[lignes_df["produit_id"].apply(to_int)==to_int(produit_id)].copy()
    if history.empty:
        return {}
    sort_cols=[col for col in ["date_achat","ligne_achat_id"] if col in history.columns]
    if sort_cols:
        history=history.sort_values(sort_cols,ascending=[False for _ in sort_cols])
    return history.iloc[0].to_dict()
# La memorisation concerne uniquement le confort de saisie de l'interface.
def save_last_ligne_achat_form(achat_id:int|None,produit_id:int|None,qte_cartons:float,qte_par_carton:int,pu_carton:float,fabrication:date,peremption:date)->None:
    """Memorise le dernier formulaire d'achat utilise."""
    set_ui_state("last_ligne_achat_form",{
        "achat_id":achat_id,"produit_id":produit_id,"qte_cartons":qte_cartons,"qte_par_carton":qte_par_carton,
        "pu_achat_carton":pu_carton,"date_fabrication":date_to_str(fabrication),"date_peremption":date_to_str(peremption)
    })


def render_line_summary(items:list[tuple[str,str]])->None:
    """Affiche les valeurs calculees sur une meme ligne compacte."""
    cols=st.columns(len(items))
    for col,(label,value) in zip(cols,items):
        with col:
            st.markdown(
                f"""
                <div style="border:1px solid #dfe7ef;border-radius:8px;padding:10px 12px;background:#fff;min-height:76px;">
                    <div style="font-size:0.78rem;color:#53657d;font-weight:700;text-transform:uppercase;letter-spacing:.02em;margin-bottom:6px;">{label}</div>
                    <div style="font-size:1.45rem;line-height:1.1;font-weight:800;color:#08776f;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ============================================================
# 3. INDICATEURS DES LIGNES D'ACHAT
# ============================================================

total_lignes=len(lignes_df)
quantite_totale=float(lignes_df["quantite_achat"].sum()) if "quantite_achat" in lignes_df.columns and not lignes_df.empty else 0
montant_total=float(lignes_df["total_achat"].sum()) if "total_achat" in lignes_df.columns and not lignes_df.empty else 0
prix_moyen=float(lignes_df["pu_achat_piece"].mean()) if "pu_achat_piece" in lignes_df.columns and not lignes_df.empty else 0
c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Lignes",total_lignes)
with c2:
    kpi_card("Quantite totale",format_quantity(quantite_totale))
with c3:
    kpi_card("Montant produits",format_money(montant_total))
with c4:
    kpi_card("Prix moyen",format_money(prix_moyen))

# ============================================================
# 4. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_rechercher,tab_export=st.tabs(["Liste","Ajouter","Modifier","Rechercher","Export"])

# ============================================================
# 5. CONSULTATION ET CONTROLE
# ============================================================

with tab_liste:
    st.subheader("Toutes les lignes d'achat")
    info_box("Chaque ligne d'achat alimente le stock et le cout de revient. Les formules controlees sont : prix piece = prix carton / quantite par carton, montant ligne = prix carton x cartons.")
    if not incoherences_df.empty:
        st.warning(f"Attention : {len(incoherences_df)} ligne(s) d'achat ne respectent pas les formules pu_achat_piece=pu_achat_carton/qte_par_carton ou total_achat=pu_achat_carton*qte_cartons.")
        with st.expander("Voir les lignes a corriger"):
            display_dataframe(incoherences_df,use_container_width=True,hide_index=True)
    if lignes_df.empty:
        empty_data_message("Aucune ligne d'achat disponible.")
    else:
        display_dataframe(lignes_df,use_container_width=True,hide_index=True)

# ============================================================
# 6. CREATION D'UNE LIGNE D'ACHAT
# ============================================================

with tab_ajouter:
    st.subheader("Ajouter un produit a une facture")
    info_box("La previsualisation calcule automatiquement la quantite totale, le prix piece et le montant ligne avant l'enregistrement.")
    if not achats_options:
        st.warning("Aucune facture disponible. Creez d'abord une facture d'achat.")
    if not produits_options:
        st.warning("Aucun produit actif disponible.")
    create_product_filter=st.text_input("Filtrer produit",key="create_ligne_achat_filtre_produit",placeholder="Exemple : BRB, biscuit, eau...")
    with st.container(border=True):
        col1,col2=st.columns(2)
        with col1:
            achat_label=st.selectbox("Facture",achats_labels or ["Aucune facture"],index=get_default_index(achats_options,to_int(last_form.get("achat_id"),0)),key="create_ligne_achat_facture")
            produit_label=product_selectbox("Produit","create_ligne_achat_produit",create_product_filter,to_int(last_form.get("produit_id"),0))
            st.caption("La liste Produit est filtree avec le champ au-dessus.")
            produit_id_preview=produits_options.get(produit_label)
            # Les dernieres valeurs du produit sont proposees pour accelerer la saisie,
            # sans modifier automatiquement les donnees deja enregistrees.
            last_achat_values=get_last_ligne_achat_values(produit_id_preview)
            default_qte_par_carton=max(to_int(last_achat_values.get("qte_par_carton",last_form.get("qte_par_carton",1)),1),1)
            default_pu_carton=float(max(to_float(last_achat_values.get("pu_achat_carton",last_form.get("pu_achat_carton",0.0))),0.0))
            if last_achat_values:
                st.caption(f"Dernier achat propose : {format_quantity(default_qte_par_carton)} par carton, {format_money(default_pu_carton)} par carton.")
            qte_cartons=st.number_input("Quantite de cartons",min_value=1.0,value=float(max(to_float(last_form.get("qte_cartons"),1.0),1.0)),step=1.0,key="create_ligne_achat_qte_cartons")
            qte_par_carton=st.number_input("Quantite par carton",min_value=1,value=default_qte_par_carton,step=1,key=f"create_ligne_achat_qte_par_carton_{to_int(produit_id_preview,0)}")
        with col2:
            pu_carton=st.number_input("Prix achat carton",min_value=0.0,value=default_pu_carton,step=100.0,key=f"create_ligne_achat_pu_carton_{to_int(produit_id_preview,0)}")
            fabrication=st.date_input("Date fabrication",value=parse_date(last_form.get("date_fabrication"),date.today()) or date.today(),key="create_ligne_achat_fabrication")
            peremption=st.date_input("Date peremption",value=parse_date(last_form.get("date_peremption"),date.today()) or date.today(),key="create_ligne_achat_peremption")
            # La previsualisation controle les calculs avant l'enregistrement en base.
            preview=calcul_ligne_achat(qte_cartons,qte_par_carton,pu_carton)
            render_line_summary([
                ("Quantite totale",format_quantity(preview["quantite_achat"])),
                ("Prix piece",format_money(preview["pu_achat_piece"])),
                ("Montant ligne",format_money(preview["total_achat"]))
            ])
        submitted=st.button("Ajouter la ligne",type="primary",key="btn_create_ligne_achat")
    if submitted:
        achat_id=achats_options.get(achat_label)
        produit_id=produits_options.get(produit_label)
        result=create_ligne_achat(achat_id,produit_id,qte_cartons,qte_par_carton,pu_carton,fabrication,peremption)
        if result["success"]:
            save_last_ligne_achat_form(achat_id,produit_id,qte_cartons,qte_par_carton,pu_carton,fabrication,peremption)
            st.success(result["message"])
        else:
            st.error(result["message"])

# ============================================================
# 7. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier une ligne d'achat")
    if lignes_df.empty:
        empty_data_message("Aucune ligne disponible.")
    elif not achats_options:
        empty_data_message("Aucune facture disponible.")
    else:
        info_box("Choisissez d'abord une facture. La liste propose ensuite uniquement les produits deja enregistres dans cette facture.")
        default_achat_id=to_int(get_ui_state("last_ligne_achat_update_achat_id",0),0)
        facture_label=st.selectbox("Facture a modifier",achats_labels,index=get_default_index(achats_options,default_achat_id),key="update_ligne_achat_facture_filter")
        facture_id=achats_options.get(facture_label)
        lignes_facture=lignes_df[lignes_df["achat_id"].apply(to_int)==to_int(facture_id)] if facture_id else lignes_df.iloc[0:0]
        if lignes_facture.empty:
            empty_data_message("Aucun produit enregistre dans cette facture.")
        else:
            options={f"{row['ligne_achat_id']} - {row.get('code_produit','')} - {row.get('nom_produit','Produit')}":int(row["ligne_achat_id"]) for _,row in lignes_facture.iterrows()}
            selected=st.selectbox("Produit / ligne de cette facture",list(options.keys()),key=f"ligne_achat_update_select_{facture_id}")
            ligne_id=options[selected]
            current=lignes_facture[lignes_facture["ligne_achat_id"]==ligne_id].iloc[0].to_dict()
            with st.container(border=True):
                col1,col2=st.columns(2)
                with col1:
                    facture_destination_index=get_default_index(achats_options,to_int(current.get("achat_id"),0)) if achats_labels else 0
                    facture_destination_label=st.selectbox("Nouvelle facture",achats_labels or ["Aucune facture"],index=facture_destination_index,key=f"update_ligne_achat_facture_destination_{ligne_id}",help="Choisissez ici la facture finale de cette ligne.")
                    produit_index=get_default_index(produits_options,to_int(current.get("produit_id"),0)) if produits_labels else 0
                    produit_label=st.selectbox("Produit",produits_labels or ["Aucun produit"],index=produit_index,key=f"update_ligne_achat_produit_{ligne_id}")
                    qte_cartons=st.number_input("Quantite de cartons",min_value=1.0,value=float(max(to_float(current.get("qte_cartons"),1.0),1.0)),step=1.0,key=f"update_ligne_achat_qte_cartons_{ligne_id}")
                    qte_par_carton=st.number_input("Quantite par carton",min_value=1,value=max(to_int(current.get("qte_par_carton"),1),1),step=1,key=f"update_ligne_achat_qte_par_carton_{ligne_id}")
                with col2:
                    pu_carton=st.number_input("Prix achat carton",min_value=0.0,value=float(max(to_float(current.get("pu_achat_carton"),0.0),0.0)),step=100.0,key=f"update_ligne_achat_pu_carton_{ligne_id}")
                    fabrication=st.date_input("Date fabrication",value=parse_date(current.get("date_fabrication"),date.today()) or date.today(),key=f"update_ligne_achat_fabrication_{ligne_id}")
                    peremption=st.date_input("Date peremption",value=parse_date(current.get("date_peremption"),date.today()) or date.today(),key=f"update_ligne_achat_peremption_{ligne_id}")
                    preview=calcul_ligne_achat(qte_cartons,qte_par_carton,pu_carton)
                    render_line_summary([
                        ("Quantite totale",format_quantity(preview["quantite_achat"])),
                        ("Prix piece",format_money(preview["pu_achat_piece"])),
                        ("Montant ligne",format_money(preview["total_achat"]))
                    ])
                submitted=st.button("Enregistrer les modifications",type="primary",key=f"btn_update_ligne_achat_{ligne_id}")
            col_a,col_b=st.columns(2)
            if submitted:
                facture_destination_id=achats_options.get(facture_destination_label)
                produit_id_selected=produits_options.get(produit_label)
                if not facture_id:
                    st.error("Aucune facture source definie.")
                elif not facture_destination_id:
                    st.error("Aucune nouvelle facture definie.")
                elif not produit_id_selected:
                    st.error("Aucun produit defini.")
                else:
                    result=update_ligne_achat(ligne_id,facture_destination_id,produit_id_selected,qte_cartons,qte_par_carton,pu_carton,fabrication,peremption)
                    if result["success"]:
                        set_ui_state("last_ligne_achat_update_achat_id",facture_destination_id)
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
            with col_b:
                if st.button("Supprimer cette ligne",key=f"delete_ligne_achat_{ligne_id}"):
                    result=delete_ligne_achat(ligne_id)
                    st.success(result["message"]) if result["success"] else st.error(result["message"])
# ============================================================
# 8. RECHERCHE DES LIGNES
# ============================================================

with tab_rechercher:
    st.subheader("Recherche des lignes")
    col1,col2,col3=st.columns(3)
    keyword=col1.text_input("Produit, code ou facture")
    start=col2.date_input("Date debut",value=date.today(),key="ligne_achat_start")
    end=col3.date_input("Date fin",value=date.today(),key="ligne_achat_end")
    if "lignes_achat_search_result" not in st.session_state:
        st.session_state["lignes_achat_search_result"]=None
    if st.button("Rechercher par periode",key="search_lignes_achat_period"):
        st.session_state["lignes_achat_search_result"]=add_achats_display_columns(search_lignes_achat(keyword=keyword,start_date=start,end_date=end))
    elif keyword:
        st.session_state["lignes_achat_search_result"]=add_achats_display_columns(search_lignes_achat(keyword=keyword))
    result=st.session_state["lignes_achat_search_result"]
    if result is not None:
        if result.empty:
            empty_data_message("Aucune ligne trouvee.")
        else:
            display_dataframe(result,use_container_width=True,hide_index=True)
            render_export_buttons("recherche_lignes_achat",result,"recherche_lignes_achat")

# ============================================================
# 9. EXPORT DES LIGNES D'ACHAT
# ============================================================

with tab_export:
    st.subheader("Exporter les lignes d'achat")
    if lignes_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_period_export("lignes_achat",lignes_df,"lignes_achat_export","date_achat")




