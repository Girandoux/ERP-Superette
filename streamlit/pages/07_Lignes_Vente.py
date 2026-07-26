# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 07_Lignes_Vente.py
# ROLE : Gestion des lignes de vente
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,kpi_card,page_title
from utils.calculs import calcul_ligne_vente
from utils.exports import render_export_buttons, render_period_export
from utils.helpers import format_money,format_quantity,get_ui_state,normalize_text,set_ui_state
from utils.produits import get_produits_options,list_produits
from utils.ventes import add_ventes_display_columns,create_ligne_vente,delete_ligne_vente,get_last_purchase_cost_before_sale,get_last_sale_price_before_sale,get_lignes_vente_kpis,list_lignes_vente,list_ventes,search_lignes_vente,update_ligne_vente

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

page_title("Lignes de vente","Ajout et suivi des produits vendus par vente")
# Une ligne de vente relie une vente a un produit. Son enregistrement
# recalcule le montant, la marge et diminue le stock selon la logique metier.
lignes_df=add_ventes_display_columns(list_lignes_vente())
ventes_df=list_ventes()
produits_options=get_produits_options(active_only=True)
produits_labels=list(produits_options.keys())
produits_stock_df=list_produits(active_only=False)
stock_by_product={
    int(row["produit_id"]):int(float(row.get("stock_actuel") or 0))
    for _,row in produits_stock_df.iterrows()
} if not produits_stock_df.empty else {}
last_ligne_vente_produit_id=int(get_ui_state("last_ligne_vente_produit_id",0) or 0)
ventes_options={f"Vente {row['vente_id']} - {row['date_vente']}":int(row["vente_id"]) for _,row in ventes_df.iterrows()} if not ventes_df.empty else {}
kpis=get_lignes_vente_kpis()
TYPE_VENTE_OPTIONS=["Normale","Declassee - produit abime","Promotion","Don"]

# ============================================================
# 2. FONCTIONS D'AIDE POUR LES FORMULAIRES ET COMMANDES
# ============================================================

__all__ = [
    "get_default_product_index",
    "get_filtered_product_labels",
    "product_selectbox",
    "render_line_summary",
    "add_to_order_list",
    "get_order_dataframe",
]

def get_default_product_index(labels:list[str],selected_id:int|None=None)->int:
    """Retourne l'index du produit demande ou du dernier produit utilise."""
    if not labels:
        return 0
    target_id=selected_id or last_ligne_vente_produit_id
    for index,label in enumerate(labels):
        if produits_options.get(label)==target_id:
            return index
    return 0

def get_filtered_product_labels(filter_text:str="")->list[str]:
    """Filtre les produits par code ou nom saisi."""
    keyword=normalize_text(filter_text)
    if not keyword:
        return produits_labels
    return [label for label in produits_labels if keyword in normalize_text(label)]

def product_selectbox(label:str,key:str,filter_text:str="",selected_id:int|None=None)->str:
    """Affiche une liste Produit filtree avec memorisation du dernier choix."""
    choices=get_filtered_product_labels(filter_text) or ["Aucun produit"]
    if selected_id and all(produits_options.get(item)!=selected_id for item in choices):
        current_label=next((item for item in produits_labels if produits_options.get(item)==selected_id),None)
        if current_label:
            choices=[current_label]+choices
    return st.selectbox(label,choices,index=get_default_product_index(choices,selected_id),key=key,help="Tapez dans Filtrer produit pour reduire cette liste.")


def render_line_summary(items:list[tuple[str,str]])->None:
    """Affiche les valeurs calculees sur une meme ligne compacte."""
    cols=st.columns(len(items))
    for col,(label,value) in zip(cols,items):
        with col:
            st.markdown(
                f"""
                <div style="border:1px solid #dfe7ef;border-radius:8px;padding:10px 12px;background:#fff;min-height:72px;">
                    <div style="font-size:0.76rem;color:#53657d;font-weight:700;text-transform:uppercase;letter-spacing:.02em;margin-bottom:6px;">{label}</div>
                    <div style="font-size:1.35rem;line-height:1.1;font-weight:800;color:#08776f;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )



def add_to_order_list(produit_id:int,produit_label:str,qte_demandee:int,stock_disponible:int,date_vente)->None:
    """Ajoute le manque de stock dans la liste des produits a commander."""
    if not produit_id:
        return
    qte_a_commander=max(int(qte_demandee)-max(int(stock_disponible),0),0)
    if qte_a_commander<=0:
        return
    if "produits_a_commander" not in st.session_state:
        st.session_state["produits_a_commander"]=[]
    existing=next((item for item in st.session_state["produits_a_commander"] if item["produit_id"]==produit_id),None)
    if existing:
        existing["qte_a_commander"]+=qte_a_commander
        existing["qte_demandee"]+=int(qte_demandee)
        existing["stock_disponible"]=int(stock_disponible)
        existing["date_vente"]=str(date_vente)
    else:
        st.session_state["produits_a_commander"].append({
            "produit_id":int(produit_id),
            "produit":produit_label,
            "qte_demandee":int(qte_demandee),
            "stock_disponible":int(stock_disponible),
            "qte_a_commander":int(qte_a_commander),
            "date_vente":str(date_vente)
        })

def get_order_dataframe():
    """Retourne les produits a commander : stock sous minimum + ventes manquees."""
    import pandas as pd
    rows=[]
    if produits_stock_df is not None and not produits_stock_df.empty:
        for _,row in produits_stock_df.iterrows():
            actif=bool(row.get("actif",True))
            stock=int(float(row.get("stock_actuel") or 0))
            stock_min=int(float(row.get("stock_min") or 0))
            if actif and stock<stock_min:
                rows.append({
                    "produit_id":int(row.get("produit_id") or 0),
                    "produit":f"{row.get('code_produit','')} - {row.get('nom_produit','')}",
                    "stock_disponible":stock,
                    "stock_minimum":stock_min,
                    "qte_demandee":0,
                    "qte_a_commander":max(stock_min-stock,0),
                    "source":"Stock sous minimum",
                    "date_vente":""
                })
    for item in st.session_state.get("produits_a_commander",[]):
        copied=dict(item)
        copied.setdefault("stock_minimum","")
        copied.setdefault("source","Vente stock insuffisant")
        rows.append(copied)
    if not rows:
        return pd.DataFrame()
    df=pd.DataFrame(rows)
    numeric_cols=["qte_demandee","stock_disponible","stock_minimum","qte_a_commander"]
    for col in numeric_cols:
        if col in df.columns:
            df[col]=pd.to_numeric(df[col],errors="coerce").fillna(0).astype(int)
    # Les besoins issus du stock minimum et des ventes manquees sont regroupes
    # par produit pour eviter les doublons dans la liste de commande.
    grouped=df.groupby("produit_id",as_index=False).agg({
        "produit":"first",
        "stock_disponible":"min",
        "stock_minimum":"max",
        "qte_demandee":"sum",
        "qte_a_commander":"sum",
        "source":lambda values:", ".join(sorted(set(str(v) for v in values if str(v).strip()))),
        "date_vente":lambda values:", ".join(sorted(set(str(v) for v in values if str(v).strip())))
    })
    columns=["produit_id","produit","stock_disponible","stock_minimum","qte_demandee","qte_a_commander","source","date_vente"]
    return grouped[columns].sort_values(["source","produit"]).reset_index(drop=True)

# ============================================================
# 3. INDICATEURS DES LIGNES DE VENTE
# ============================================================

c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Lignes",kpis.get("total_lignes",0))
with c2:
    kpi_card("Quantite vendue",format_quantity(kpis.get("total_quantite",0)))
with c3:
    kpi_card("Chiffre d'affaires",format_money(kpis.get("chiffre_affaires",0)))
with c4:
    kpi_card("Marge brute",format_money(kpis.get("marge_brute",0)))

# ============================================================
# 4. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_rechercher,tab_commander,tab_export=st.tabs(["Liste","Ajouter","Modifier","Rechercher","A commander","Export"])

# ============================================================
# 5. CONSULTATION DES LIGNES DE VENTE
# ============================================================

with tab_liste:
    st.subheader("Toutes les lignes de vente")
    if lignes_df.empty:
        empty_data_message("Aucune ligne de vente disponible.")
    else:
        display_dataframe(lignes_df,use_container_width=True,hide_index=True)

# ============================================================
# 6. CREATION D'UNE LIGNE DE VENTE
# ============================================================

with tab_ajouter:
    st.subheader("Ajouter un produit a une vente")
    if not ventes_options:
        st.warning("Aucune vente disponible. Creez d'abord une vente.")
    if not produits_options:
        st.warning("Aucun produit actif disponible.")
    create_product_filter=st.text_input("Filtrer produit",key="create_ligne_vente_filtre_produit",placeholder="Exemple : NES, EAU, BRI...")
    with st.container(border=True):
        col1,col2=st.columns(2)
        with col1:
            vente_label=st.selectbox("Vente",list(ventes_options.keys()) or ["Aucune vente"],key="create_ligne_vente_vente")
            produit_label=product_selectbox("Produit","create_ligne_vente_produit",create_product_filter)
            st.caption("La liste Produit est filtree avec le champ au-dessus.")
            qte_vente=st.number_input("Quantite vendue",min_value=1,value=1,step=1,key="create_ligne_vente_qte")
            type_vente=st.selectbox("Type de vente",TYPE_VENTE_OPTIONS,key="create_ligne_vente_type",help="Utilisez Declassee si le produit est abime mais vendable.")
            if type_vente=="Declassee - produit abime":
                st.info("Produit abime vendu a prix reduit : la vente reste tracee separement.")
            vente_id_selected=ventes_options.get(vente_label)
            produit_id_selected=produits_options.get(produit_label)
            # Le dernier prix de vente et le dernier cout d'achat sont proposes
            # pour accelerer la saisie sans imposer leur utilisation.
            prix_auto=get_last_sale_price_before_sale(produit_id_selected,vente_id=vente_id_selected) if vente_id_selected and produit_id_selected else 0.0
            cout_auto=get_last_purchase_cost_before_sale(produit_id_selected,vente_id=vente_id_selected) if vente_id_selected and produit_id_selected else 0.0
        with col2:
            pu_vente=st.number_input("Prix de vente",min_value=0.0,value=float(prix_auto or 0),step=100.0,key=f"create_ligne_vente_pu_{vente_id_selected or 0}_{produit_id_selected or 0}",help="Prix propose automatiquement avec le dernier prix vendu de ce produit.")
            st.caption(f"Dernier prix propose : {format_money(prix_auto)}")
            utiliser_cout_auto=st.checkbox("Utiliser le cout automatique",value=True,key="create_ligne_vente_cout_auto",help="Le cout sera recalcule au moment de l'enregistrement avec le dernier achat avant la vente.")
            if utiliser_cout_auto:
                cout_unitaire=cout_auto
                st.caption("Cout automatique selon le dernier achat avant la date de vente.")
            else:
                cout_unitaire=st.number_input("Cout unitaire",min_value=0.0,value=float(cout_auto or 0),step=100.0,key="create_ligne_vente_cout_unitaire",help="Propose automatiquement le dernier prix d'achat du produit avant la date de vente.")
                st.caption(f"Cout propose : {format_money(cout_auto)}")
            cout_preview=cout_unitaire
            preview=calcul_ligne_vente(qte_vente,pu_vente,cout_preview)
            render_line_summary([
                ("Cout unitaire",format_money(cout_unitaire)),
                ("Montant ligne",format_money(preview["montant_ligne"])),
                ("Marge",format_money(preview["marge"]))
            ])
        submitted=st.button("Ajouter la ligne",type="primary",key="btn_create_ligne_vente")
    pending_key="pending_negative_ligne_vente"
    if submitted:
        if not vente_id_selected:
            st.error("Aucune vente definie. Creez ou selectionnez une vente.")
        elif not produit_id_selected:
            st.error("Aucun produit defini. Selectionnez un produit avant d'ajouter la ligne.")
        else:
            stock_disponible=stock_by_product.get(int(produit_id_selected or 0),0)
            qte_a_enregistrer=int(qte_vente)
            if stock_disponible<=0:
                add_to_order_list(produit_id_selected,produit_label,qte_vente,stock_disponible,vente_label)
                st.error("Stock zero : ajout refuse. Verifiez le stock avant de vendre ce produit.")
            else:
                # En cas de stock insuffisant, seule la quantite disponible est vendue
                # et le manque est ajoute a la liste des produits a commander.
                if int(qte_vente)>stock_disponible:
                    add_to_order_list(produit_id_selected,produit_label,qte_vente,stock_disponible,vente_label)
                    qte_a_enregistrer=stock_disponible
                    st.warning(f"Stock insuffisant : {stock_disponible} ajoute(s) a la vente, {int(qte_vente)-stock_disponible} ajoute(s) a la liste des produits a commander.")
                preview_save=calcul_ligne_vente(qte_a_enregistrer,pu_vente,cout_unitaire)
                sale_data={"vente_id":vente_id_selected,"produit_id":produit_id_selected,"qte_vente":qte_a_enregistrer,"pu_vente":pu_vente,"cout_unitaire":cout_unitaire,"utiliser_cout_auto":utiliser_cout_auto,"produit_label":produit_label,"marge":preview_save["marge"],"montant_ligne":preview_save["montant_ligne"],"type_vente":type_vente}
                # Une marge negative exige une confirmation explicite avant enregistrement.
                if preview_save["marge"]<0:
                    st.session_state[pending_key]=sale_data
                    st.warning(f"Marge negative detectee : {format_money(preview_save['marge'])}. Confirmez pour enregistrer cette vente a perte.")
                else:
                    result=create_ligne_vente(vente_id_selected,produit_id_selected,qte_a_enregistrer,pu_vente,None if utiliser_cout_auto else cout_unitaire,type_vente)
                    if result["success"]:
                        set_ui_state("last_ligne_vente_produit_id",produit_id_selected)
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
    pending_sale=st.session_state.get(pending_key)
    if pending_sale:
        st.warning(f"Confirmation requise : {pending_sale['produit_label']} aura une marge negative de {format_money(pending_sale['marge'])}.")
        col_confirm,col_cancel=st.columns(2)
        if col_confirm.button("Confirmer et enregistrer",type="primary",key="confirm_negative_ligne_vente"):
            result=create_ligne_vente(pending_sale["vente_id"],pending_sale["produit_id"],pending_sale["qte_vente"],pending_sale["pu_vente"],None if pending_sale["utiliser_cout_auto"] else pending_sale["cout_unitaire"],pending_sale.get("type_vente","Normale"))
            st.session_state.pop(pending_key,None)
            if result["success"]:
                set_ui_state("last_ligne_vente_produit_id",pending_sale["produit_id"])
                st.success(result["message"])
            else:
                st.error(result["message"])
        if col_cancel.button("Annuler",key="cancel_negative_ligne_vente"):
            st.session_state.pop(pending_key,None)
            st.info("Enregistrement annule.")

# ============================================================
# 7. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier une ligne de vente")
    if lignes_df.empty:
        empty_data_message("Aucune ligne disponible.")
    else:
        vente_labels=list(ventes_options.keys()) or ["Aucune vente"]
        vente_label=st.selectbox("Vente",vente_labels,key="update_ligne_vente_vente")
        vente_id_selected=ventes_options.get(vente_label)
        lignes_vente_df=lignes_df[lignes_df["vente_id"]==vente_id_selected].copy() if vente_id_selected and "vente_id" in lignes_df.columns else lignes_df.iloc[0:0].copy()
        if lignes_vente_df.empty:
            empty_data_message("Aucun produit trouve pour cette vente.")
        else:
            line_options={f"{row.get('code_produit','')} - {row.get('nom_produit','Produit')} | Ligne {int(row['ligne_vente_id'])}":int(row["ligne_vente_id"]) for _,row in lignes_vente_df.iterrows()}
            selected_line=st.selectbox("Produit de cette vente",list(line_options.keys()),key="update_ligne_vente_ligne")
            ligne_id=line_options[selected_line]
            current=lignes_vente_df[lignes_vente_df["ligne_vente_id"]==ligne_id].iloc[0].to_dict()
            current_produit_id=int(current.get("produit_id") or 0)
            produit_id_selected=current_produit_id
            produit_label=selected_line
            current_type=current.get("type_vente","Normale") or "Normale"
            with st.container(border=True):
                col1,col2=st.columns(2)
                with col1:
                    update_product_filter=st.text_input("Filtrer nouveau produit",key=f"update_ligne_vente_filtre_produit_{ligne_id}",placeholder="Exemple : JUS, EAU, BIS...")
                    produit_label=product_selectbox("Produit",f"update_ligne_vente_produit_{ligne_id}",update_product_filter,current_produit_id)
                    produit_id_selected=produits_options.get(produit_label) or current_produit_id
                    if produit_id_selected!=current_produit_id:
                        st.caption("Le produit de cette ligne sera remplace par le produit choisi ci-dessus.")
                    cout_auto=get_last_purchase_cost_before_sale(produit_id_selected,vente_id=vente_id_selected) if vente_id_selected and produit_id_selected else 0.0
                    prix_auto=get_last_sale_price_before_sale(produit_id_selected,vente_id=vente_id_selected,exclude_ligne_id=ligne_id) if vente_id_selected and produit_id_selected else 0.0
                    qte_vente=st.number_input("Quantite vendue",min_value=1,value=int(current.get("qte_vente") or 1),step=1,key=f"update_ligne_vente_qte_{ligne_id}")
                    type_vente=st.selectbox("Type de vente",TYPE_VENTE_OPTIONS,index=TYPE_VENTE_OPTIONS.index(current_type) if current_type in TYPE_VENTE_OPTIONS else 0,key=f"update_ligne_vente_type_{ligne_id}")
                with col2:
                    pu_default=float(current.get("pu_vente") or prix_auto or 0) if produit_id_selected==current_produit_id else float(prix_auto or current.get("pu_vente") or 0)
                    pu_vente=st.number_input("Prix de vente",min_value=0.0,value=pu_default,step=100.0,key=f"update_ligne_vente_pu_{ligne_id}_{produit_id_selected}",help="Prix actuel modifiable. Le dernier prix vendu est affiche juste dessous.")
                    st.caption(f"Dernier prix propose : {format_money(prix_auto)}")
                    recalculer_cout_auto=st.checkbox("Utiliser le cout automatique",value=True,key=f"update_ligne_vente_cout_auto_{ligne_id}",help="Le cout est recalcule avec le dernier achat avant la date de vente.")
                    if recalculer_cout_auto:
                        cout_unitaire=cout_auto
                        st.metric("Cout unitaire",format_money(cout_auto))
                        st.caption("Cout automatique selon le dernier achat avant la date de vente.")
                    else:
                        cout_default=float(current.get("cout_unitaire") or cout_auto or 0) if produit_id_selected==current_produit_id else float(cout_auto or current.get("cout_unitaire") or 0)
                        cout_unitaire=st.number_input("Cout unitaire",min_value=0.0,value=cout_default,step=100.0,key=f"update_ligne_vente_cout_{ligne_id}",help="Cout manuel pour cette ligne.")
                        st.caption(f"Cout propose : {format_money(cout_auto)}")
                    preview=calcul_ligne_vente(qte_vente,pu_vente,cout_unitaire)
                    render_line_summary([
                        ("Cout unitaire",format_money(cout_unitaire)),
                        ("Montant ligne",format_money(preview["montant_ligne"])),
                        ("Marge",format_money(preview["marge"]))
                    ])
                submitted=st.button("Enregistrer les modifications",type="primary",key=f"btn_update_ligne_vente_{ligne_id}")
            pending_update_key="pending_negative_update_ligne_vente"
            if submitted:
                update_data={"ligne_id":ligne_id,"vente_id":vente_id_selected,"produit_id":produit_id_selected,"qte_vente":qte_vente,"pu_vente":pu_vente,"cout_unitaire":cout_unitaire,"recalculer_cout_auto":recalculer_cout_auto,"produit_label":produit_label,"marge":preview["marge"],"type_vente":type_vente}
                if preview["marge"]<0:
                    st.session_state[pending_update_key]=update_data
                    st.warning(f"Marge negative detectee : {format_money(preview['marge'])}. Confirmez pour enregistrer cette modification.")
                else:
                    result=update_ligne_vente(ligne_id,vente_id_selected,produit_id_selected,qte_vente,pu_vente,None if recalculer_cout_auto else cout_unitaire,type_vente)
                    if result["success"]:
                        set_ui_state("last_ligne_vente_produit_id",produit_id_selected)
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
            pending_update=st.session_state.get(pending_update_key)
            if pending_update:
                st.warning(f"Confirmation requise : {pending_update['produit_label']} aura une marge negative de {format_money(pending_update['marge'])}.")
                col_confirm,col_cancel=st.columns(2)
                if col_confirm.button("Confirmer et modifier",type="primary",key="confirm_negative_update_ligne_vente"):
                    result=update_ligne_vente(pending_update["ligne_id"],pending_update["vente_id"],pending_update["produit_id"],pending_update["qte_vente"],pending_update["pu_vente"],None if pending_update["recalculer_cout_auto"] else pending_update["cout_unitaire"],pending_update.get("type_vente","Normale"))
                    st.session_state.pop(pending_update_key,None)
                    if result["success"]:
                        set_ui_state("last_ligne_vente_produit_id",pending_update["produit_id"])
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                if col_cancel.button("Annuler",key="cancel_negative_update_ligne_vente"):
                    st.session_state.pop(pending_update_key,None)
                    st.info("Modification annulee.")
            if st.button("Supprimer cette ligne",key=f"delete_ligne_vente_{ligne_id}"):
                result=delete_ligne_vente(ligne_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 8. RECHERCHE DES LIGNES
# ============================================================
with tab_rechercher:
    st.subheader("Recherche des lignes")
    col1,col2,col3=st.columns(3)
    keyword=col1.text_input("Produit ou code")
    start=col2.date_input("Date debut",value=date.today(),key="ligne_vente_start")
    end=col3.date_input("Date fin",value=date.today(),key="ligne_vente_end")
    if "lignes_vente_search_result" not in st.session_state:
        st.session_state["lignes_vente_search_result"]=None
    if st.button("Rechercher par periode",key="search_lignes_vente_period"):
        if start>end:
            st.error("La date debut ne peut pas etre apres la date fin.")
            st.session_state["lignes_vente_search_result"]=None
        else:
            search_keyword=keyword.strip() if keyword else None
            st.session_state["lignes_vente_search_result"]=add_ventes_display_columns(search_lignes_vente(keyword=search_keyword,start_date=start,end_date=end))
    result=st.session_state["lignes_vente_search_result"]
    if result is not None:
        if result.empty:
            empty_data_message("Aucune ligne trouvee.")
        else:
            display_dataframe(result,use_container_width=True,hide_index=True)
            render_export_buttons("recherche_lignes_vente",result,"recherche_lignes_vente")

# ============================================================
# 9. PRODUITS A COMMANDER
# ============================================================

with tab_commander:
    st.subheader("Produits a commander")
    order_df=get_order_dataframe()
    if order_df.empty:
        empty_data_message("Aucun produit a commander pour le moment.")
    else:
        display_dataframe(order_df,use_container_width=True,hide_index=True)
        render_export_buttons("produits_a_commander",order_df,"produits_a_commander")
        if st.button("Vider la liste",key="clear_produits_a_commander"):
            st.session_state["produits_a_commander"]=[]
            st.success("Liste des produits a commander videe.")

# ============================================================
# 10. EXPORT DES LIGNES DE VENTE
# ============================================================

with tab_export:
    st.subheader("Exporter les lignes de vente")
    if lignes_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_period_export("lignes_vente",lignes_df,"lignes_vente_export","date_vente")

