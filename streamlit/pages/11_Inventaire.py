# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 11_Inventaire.py
# ROLE : Controle et suivi de l'inventaire
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,kpi_card,page_title
from utils.exports import render_export_buttons, render_period_export
from utils.helpers import format_money,format_quantity
from utils.inventaire import add_controle_stock_display_columns,add_inventaire_display_columns,cloturer_inventaire,cloturer_inventaires_by_date,compare_inventaire_with_previous,corriger_inventaire_cloture,create_inventaire,delete_inventaire,filter_controle_stock_dataframe,filter_inventaire_dataframe,get_inventaire_history_for_product,get_inventaire_resume,list_controle_stock,synchroniser_stock_controle,list_ecarts_inventaire,list_inventaires,list_inventaires_by_date,search_inventaires,update_inventaire
from utils.produits import get_produits_options

# ============================================================
# 1. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

# Le processus suit le comptage physique, le calcul de l'ecart,
# la cloture puis, si necessaire, la correction du stock.
page_title("Inventaire","Controle du stock physique et suivi des ecarts")
inventaire_df=add_inventaire_display_columns(list_inventaires())
resume=get_inventaire_resume()
produits_options=get_produits_options(active_only=True)

# ============================================================
# 2. INDICATEURS D'INVENTAIRE
# ============================================================

c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Controles",resume.get("total_controles",0))
with c2:
    kpi_card("Clotures",resume.get("clotures",0))
with c3:
    kpi_card("Ecarts",format_quantity(resume.get("total_ecarts",0)))
with c4:
    kpi_card("Valeur ecarts",format_money(resume.get("valeur_ecarts",0)))

# ============================================================
# 3. ORGANISATION DES ONGLETS
# ============================================================

tab_liste,tab_ajouter,tab_modifier,tab_cloturer,tab_correction,tab_ecarts,tab_comparer,tab_controle_stock,tab_export=st.tabs(["Liste","Ajouter","Modifier","Cloturer","Correction","Ecarts","Comparer","Controle stock","Export"])

# ============================================================
# 4. CONSULTATION DES CONTROLES
# ============================================================

with tab_liste:
    st.subheader("Historique des controles")
    col1,col2=st.columns([2,1])
    keyword=col1.text_input("Filtrer",key="inventaire_filtre")
    statut=col2.selectbox("Statut",["Tous","CONFORME","SURPLUS","MANQUANT"])
    filtered=filter_inventaire_dataframe(inventaire_df,keyword,statut if statut!="Tous" else None)
    display_dataframe(filtered,use_container_width=True,hide_index=True) if not filtered.empty else empty_data_message("Aucun inventaire trouve.")

# ============================================================
# 5. CREATION D'UN CONTROLE
# ============================================================

with tab_ajouter:
    st.subheader("Nouveau controle inventaire")
    if not produits_options:
        st.warning("Aucun produit actif disponible.")
    # Le stock theorique, l'ecart et sa valeur restent calcules
    # par la logique SQL existante.
    with st.form("form_create_inventaire",clear_on_submit=True):
        col1,col2=st.columns(2)
        with col1:
            date_inventaire=st.date_input("Date inventaire",value=date.today())
            produit_label=st.selectbox("Produit",list(produits_options.keys()) or ["Aucun produit"])
            stock_physique=st.number_input("Stock physique",min_value=0,value=0,step=1)
        with col2:
            commentaire=st.text_area("Commentaire")
            utilisateur=st.text_input("Utilisateur",value="SYSTEM")
            st.info("Le stock theorique, l'ecart et la valeur ecart sont calcules par les triggers SQL.")
        submitted=st.form_submit_button("Enregistrer le controle",type="primary")
    if submitted:
        result=create_inventaire(date_inventaire,produits_options.get(produit_label),stock_physique,commentaire,utilisateur)
        st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 6. MODIFICATION ET SUPPRESSION
# ============================================================

with tab_modifier:
    st.subheader("Modifier un controle")
    if inventaire_df.empty:
        empty_data_message("Aucun controle disponible.")
    else:
        options={f"{row['inventaire_id']} - {row.get('nom_produit','Produit')} - {row['date_inventaire']}":int(row["inventaire_id"]) for _,row in inventaire_df.iterrows()}
        selected=st.selectbox("Controle",list(options.keys()))
        inventaire_id=options[selected]
        current=inventaire_df[inventaire_df["inventaire_id"]==inventaire_id].iloc[0].to_dict()
        with st.form("form_update_inventaire"):
            col1,col2=st.columns(2)
            with col1:
                date_inventaire=st.date_input("Date inventaire",value=current.get("date_inventaire") or date.today())
                produit_label=st.selectbox("Produit",list(produits_options.keys()) or ["Aucun produit"])
                stock_physique=st.number_input("Stock physique",min_value=0,value=int(current.get("stock_physique") or 0),step=1)
            with col2:
                commentaire=st.text_area("Commentaire",value=str(current.get("commentaire") or ""))
                utilisateur=st.text_input("Utilisateur",value=str(current.get("utilisateur") or "SYSTEM"))
            submitted=st.form_submit_button("Enregistrer les modifications",type="primary")
        col_a,col_b=st.columns(2)
        if submitted:
            result=update_inventaire(inventaire_id,date_inventaire,produits_options.get(produit_label),stock_physique,commentaire,utilisateur)
            st.success(result["message"]) if result["success"] else st.error(result["message"])
        with col_b:
            if st.button("Supprimer ce controle"):
                result=delete_inventaire(inventaire_id)
                st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 7. CLOTURE DES INVENTAIRES
# ============================================================

# La cloture conserve l'historique et aligne le stock courant
# sur le comptage physique valide.
with tab_cloturer:
    st.subheader("Cloturer un inventaire")
    st.info("La cloture garde l'historique, cree une perte si l'ecart est negatif et aligne le stock actuel sur le stock physique.")
    if inventaire_df.empty:
        empty_data_message("Aucun inventaire disponible.")
    else:
        pending_df=inventaire_df.copy()
        if "cloture" in pending_df.columns:
            pending_df=pending_df[pending_df["cloture"].fillna(False)==False]
        if pending_df.empty:
            empty_data_message("Aucun inventaire ouvert a cloturer.")
        else:
            mode=st.radio("Mode de cloture",["Une ligne","Tous les inventaires d'une date"],horizontal=True)
            utilisateur=st.text_input("Utilisateur",value="SYSTEM",key="inventaire_cloture_user")
            if mode=="Une ligne":
                options={f"{row['inventaire_id']} - {row.get('nom_produit','Produit')} - {row['date_inventaire']} - ecart {row.get('ecart',0)}":int(row["inventaire_id"]) for _,row in pending_df.iterrows()}
                selected=st.selectbox("Inventaire a cloturer",list(options.keys()),key="inventaire_cloture_select")
                current=pending_df[pending_df["inventaire_id"]==options[selected]].iloc[0]
                col1,col2,col3=st.columns(3)
                with col1:
                    kpi_card("Stock theorique",format_quantity(current.get("stock_theorique",0)))
                with col2:
                    kpi_card("Stock physique",format_quantity(current.get("stock_physique",0)))
                with col3:
                    kpi_card("Ecart",format_quantity(current.get("ecart",0)))
                if st.button("Cloturer l'inventaire",type="primary"):
                    result=cloturer_inventaire(options[selected],utilisateur)
                    st.success(result["message"]) if result["success"] else st.error(result["message"])
                    if result["success"]:
                        st.caption(result["data"])
            else:
                dates=sorted(pending_df["date_inventaire"].dropna().unique(),reverse=True)
                selected_date=st.selectbox("Date d'inventaire a cloturer",dates,key="inventaire_cloture_date")
                selected_rows=pending_df[pending_df["date_inventaire"]==selected_date]
                kpi_card("Lignes ouvertes pour cette date",len(selected_rows))
                display_dataframe(selected_rows,use_container_width=True,hide_index=True)
                if st.button("Cloturer tous les inventaires de cette date",type="primary"):
                    result=cloturer_inventaires_by_date(selected_date,utilisateur)
                    st.success(result["message"]) if result["success"] else st.error(result["message"])
                    st.caption(result["data"])

# ============================================================
# 8. CORRECTION APRES CLOTURE
# ============================================================

# La correction conserve l'inventaire d'origine, ajoute une trace
# et ajuste le stock courant selon la logique metier existante.
with tab_correction:
    st.subheader("Correction d'un inventaire cloture")
    st.markdown("""
    <div style="border:1px solid #dbeafe;border-left:4px solid #0f766e;border-radius:8px;background:#f8fbff;padding:14px 16px;margin:8px 0 18px 0;">
        <strong>Principe de controle</strong><br>
        La correction conserve l'inventaire d'origine, cree une nouvelle trace de correction et actualise le stock courant.
    </div>
    """,unsafe_allow_html=True)
    if inventaire_df.empty or "cloture" not in inventaire_df.columns:
        empty_data_message("Aucun inventaire cloture disponible.")
    else:
        closed_df=inventaire_df[inventaire_df["cloture"].fillna(False)==True]
        if closed_df.empty:
            empty_data_message("Aucun inventaire cloture disponible pour correction.")
        else:
            options={f"{row['inventaire_id']} - {row.get('nom_produit','Produit')} - {row['date_inventaire']} - stock {row.get('stock_physique',0)}":int(row["inventaire_id"]) for _,row in closed_df.iterrows()}
            selected=st.selectbox("Inventaire cloture a corriger",list(options.keys()),key="inventaire_correction_select")
            current=closed_df[closed_df["inventaire_id"]==options[selected]].iloc[0]
            stock_cloture=int(current.get("stock_physique") or 0)
            ecart_cloture=int(current.get("ecart") or 0)
            produit=current.get("nom_produit","Produit")
            code=current.get("code_produit","")
            date_inventaire=current.get("date_inventaire","")
            st.markdown(f"**Produit selectionne :** {code} - {produit}  |  **Inventaire du :** {date_inventaire}")
            nouveau_stock=st.number_input("Nouveau stock physique corrige",min_value=0,value=stock_cloture,step=1,key="inventaire_correction_nouveau_stock")
            impact=nouveau_stock-stock_cloture
            col1,col2,col3,col4=st.columns(4)
            with col1:
                kpi_card("Stock cloture",format_quantity(stock_cloture))
            with col2:
                kpi_card("Stock corrige",format_quantity(nouveau_stock))
            with col3:
                kpi_card("Impact stock",format_quantity(impact))
            with col4:
                kpi_card("Ecart cloture",format_quantity(ecart_cloture))
            if impact>0:
                st.info(f"Cette correction ajoutera {format_quantity(impact)} unite(s) au stock courant.")
            elif impact<0:
                st.warning(f"Cette correction retirera {format_quantity(abs(impact))} unite(s) du stock courant.")
            else:
                st.info("Aucun changement de quantite par rapport au stock cloture.")
            col_motif,col_user=st.columns([3,1])
            with col_motif:
                commentaire=st.text_area("Motif de correction",value="Erreur de comptage constatee apres cloture",height=110,key="inventaire_correction_motif")
            with col_user:
                utilisateur=st.text_input("Utilisateur",value="SYSTEM",key="inventaire_correction_user")
                st.caption("Ce nom sera conserve dans l'historique.")
            if st.button("Valider la correction et actualiser le stock",type="primary",key="btn_corriger_inventaire_cloture"):
                result=corriger_inventaire_cloture(options[selected],nouveau_stock,commentaire,utilisateur)
                st.success(result["message"]) if result["success"] else st.error(result["message"])
                if result.get("data"):
                    with st.expander("Details de la correction"):
                        st.write(result["data"])

# ============================================================
# 9. ANALYSE DES ECARTS ET PERIODES
# ============================================================

with tab_ecarts:
    st.subheader("Analyse des ecarts")
    include_closed=st.checkbox("Inclure les inventaires clotures",value=False)
    ecarts=add_inventaire_display_columns(list_ecarts_inventaire(include_closed=include_closed))
    display_dataframe(ecarts,use_container_width=True,hide_index=True) if not ecarts.empty else empty_data_message("Aucun ecart d'inventaire ouvert.")
    col1,col2=st.columns(2)
    start=col1.date_input("Date debut",value=date.today(),key="inv_start")
    end=col2.date_input("Date fin",value=date.today(),key="inv_end")
    if "inventaire_period_result" not in st.session_state:
        st.session_state["inventaire_period_result"]=None
    if st.button("Afficher la periode",key="search_inventaire_period"):
        st.session_state["inventaire_period_result"]=add_inventaire_display_columns(list_inventaires_by_date(start,end))
    result=st.session_state["inventaire_period_result"]
    if result is not None:
        if result.empty:
            empty_data_message("Aucun controle sur cette periode.")
        else:
            display_dataframe(result,use_container_width=True,hide_index=True)
            render_export_buttons("recherche_inventaire_periode",result,"recherche_inventaire_periode")

# ============================================================
# 10. COMPARAISON DES INVENTAIRES
# ============================================================

with tab_comparer:
    st.subheader("Comparer les inventaires")
    if inventaire_df.empty:
        empty_data_message("Aucun inventaire a comparer.")
    else:
        options={f"{row['inventaire_id']} - {row.get('nom_produit','Produit')} - {row['date_inventaire']}":int(row["inventaire_id"]) for _,row in inventaire_df.iterrows()}
        selected=st.selectbox("Inventaire de reference",list(options.keys()),key="inventaire_compare_select")
        comparison=compare_inventaire_with_previous(options[selected])
        if not comparison or not comparison.get("current"):
            empty_data_message("Comparaison impossible.")
        else:
            current=comparison["current"]
            previous=comparison.get("previous")
            col1,col2,col3=st.columns(3)
            with col1:
                kpi_card("Stock physique actuel",format_quantity(current.get("stock_physique",0)))
            with col2:
                kpi_card("Delta stock",format_quantity(comparison.get("delta_stock_physique") or 0))
            with col3:
                kpi_card("Delta ecart",format_quantity(comparison.get("delta_ecart") or 0))
            if previous:
                st.caption(f"Compare avec inventaire {previous['inventaire_id']} du {previous['date_inventaire']}.")
            else:
                st.caption("Aucun ancien inventaire pour ce produit.")
            history=add_inventaire_display_columns(get_inventaire_history_for_product(current["produit_id"],exclude_id=current["inventaire_id"],limit=10))
            display_dataframe(history,use_container_width=True,hide_index=True) if not history.empty else empty_data_message("Aucun historique precedent.")


# ============================================================
# 11. CONTROLE ET SYNCHRONISATION DU STOCK
# ============================================================

# Le controle reconstruit le stock attendu depuis le dernier inventaire
# cloture, les achats, les ventes et les pertes.
with tab_controle_stock:
    st.subheader("Controle de coherence du stock")
    st.info("Ce tableau part du dernier inventaire cloture. Les pertes Inventaire sont informatives. Si les ventes depassent le stock disponible, la colonne Vente excedentaire signale le manque au lieu de masquer le probleme.")
    col1,col2=st.columns(2)
    date_debut=col1.date_input("Date debut",value=date.today(),key="controle_stock_date_debut")
    date_fin=col2.date_input("Date fin",value=date.today(),key="controle_stock_date_fin")
    if date_debut>date_fin:
        st.error("La date debut ne peut pas etre apres la date fin.")
    else:
        controle_df=add_controle_stock_display_columns(list_controle_stock(date_debut,date_fin))
        if controle_df.empty:
            empty_data_message("Aucune donnee disponible pour le controle stock.")
        else:
            categories=["Toutes"]+sorted([str(v) for v in controle_df.get("nom_categorie",[]).dropna().unique()])
            produits_df=controle_df[["code_produit","nom_produit"]].fillna("").drop_duplicates().sort_values(["nom_produit","code_produit"]) if {"code_produit","nom_produit"}.issubset(controle_df.columns) else controle_df
            c1,c2,c3=st.columns([2,1,1])
            recherche_produit=c1.text_input("Filtrer produit ou code",placeholder="Exemple : BRB, export, biscuit...",key="controle_stock_produit_search")
            produit_labels=["Tous les produits"]
            if not produits_df.empty and {"code_produit","nom_produit"}.issubset(produits_df.columns):
                temp=produits_df.copy()
                search_value=recherche_produit.strip().lower()
                if search_value:
                    temp=temp[temp.apply(lambda r:search_value in f"{r['code_produit']} {r['nom_produit']}".lower(),axis=1)]
                produit_labels+=temp.apply(lambda r:f"{r['code_produit']} - {r['nom_produit']}",axis=1).tolist()
            produit_filtre=c1.selectbox("Produit trouve",produit_labels,key="controle_stock_produit_select")
            keyword="" if produit_filtre=="Tous les produits" else produit_filtre.split(" - ",1)[0]
            categorie=c2.selectbox("Categorie",categories,key="controle_stock_categorie")
            statut=c3.selectbox("Statut",["Tous","CONFORME","SURPLUS","MANQUANT"],key="controle_stock_statut")
            filtered=filter_controle_stock_dataframe(controle_df,keyword,categorie,statut)
            total_produits=len(filtered)
            total_manquants=len(filtered[filtered["statut_controle"]=="MANQUANT"]) if "statut_controle" in filtered.columns else 0
            total_surplus=len(filtered[filtered["statut_controle"]=="SURPLUS"]) if "statut_controle" in filtered.columns else 0
            total_ecart=float(filtered["ecart_controle"].abs().sum()) if "ecart_controle" in filtered.columns and not filtered.empty else 0
            total_vente_excedentaire=float(filtered["vente_excedentaire"].sum()) if "vente_excedentaire" in filtered.columns and not filtered.empty else 0
            k1,k2,k3,k4=st.columns(4)
            with k1:
                kpi_card("Produits controles",format_quantity(total_produits))
            with k2:
                kpi_card("Manquants",format_quantity(total_manquants))
            with k3:
                kpi_card("Surplus",format_quantity(total_surplus))
            with k4:
                kpi_card("Ecart total",format_quantity(total_ecart))
            display_cols=[
                "code_produit","nom_produit","nom_categorie","date_dernier_inventaire","date_debut_mouvements",
                "stock_dernier_inventaire_affiche","quantite_achetee_affiche","quantite_vendue_affiche","quantite_perdue_signalee_affiche","quantite_perdue_inventaire_affiche","vente_excedentaire_affiche",
                "stock_theorique_attendu_affiche","stock_actuel_affiche","ecart_controle_affiche","statut_controle"
            ]
            existing_cols=[col for col in display_cols if col in filtered.columns]
            display_df=filtered[existing_cols].rename(columns={
                "code_produit":"Code",
                "nom_produit":"Produit",
                "nom_categorie":"Categorie",
                "date_dernier_inventaire":"Dernier inventaire",
                "date_debut_mouvements":"Debut mouvements",
                "stock_dernier_inventaire_affiche":"Stock dernier inventaire",
                "quantite_achetee_affiche":"Quantite achetee",
                "quantite_vendue_affiche":"Quantite vendue",
                "quantite_perdue_signalee_affiche":"Pertes signalees",
                "quantite_perdue_inventaire_affiche":"Pertes inventaire",
                "vente_excedentaire_affiche":"Vente excedentaire",
                "stock_theorique_attendu_affiche":"Stock theorique attendu",
                "stock_actuel_affiche":"Stock actuel",
                "ecart_controle_affiche":"Ecart",
                "statut_controle":"Statut"
            })
            if display_df.empty:
                empty_data_message("Aucun produit ne correspond aux filtres.")
            else:
                def color_statut(row):
                    statut_value=str(row.get("Statut","")).upper()
                    if statut_value=="MANQUANT":
                        return ["background-color:#fee2e2;color:#991b1b" if col=="Statut" else "" for col in row.index]
                    if statut_value=="SURPLUS":
                        return ["background-color:#dbeafe;color:#1d4ed8" if col=="Statut" else "" for col in row.index]
                    if statut_value=="CONFORME":
                        return ["background-color:#dcfce7;color:#166534" if col=="Statut" else "" for col in row.index]
                    return ["" for _ in row.index]
                st.dataframe(display_df.style.apply(color_statut,axis=1),use_container_width=True,hide_index=True)
                if total_vente_excedentaire>0:
                    st.error("Synchronisation impossible : certaines ventes depassent le stock disponible. Corrigez les lignes de vente concernees ou ajoutez les achats manquants avant de synchroniser.")
                    anomaly_cols=[col for col in ["Code","Produit","Stock dernier inventaire","Quantite achetee","Quantite vendue","Pertes signalees","Vente excedentaire","Stock actuel","Statut"] if col in display_df.columns]
                    anomalies=display_df[display_df["Statut"].astype(str).str.upper()=="MANQUANT"][anomaly_cols] if "Statut" in display_df.columns else display_df[anomaly_cols]
                    with st.expander("Voir les ventes excedentaires a corriger"):
                        display_dataframe(anomalies,use_container_width=True,hide_index=True)
                elif total_ecart>0:
                    st.warning("Des differences existent entre le stock actuel enregistre et le stock theorique attendu. Ici la synchronisation est possible car il n'y a pas de vente excedentaire.")
                    if st.button("Synchroniser le stock actuel avec le controle",key="sync_stock_controle"):
                        result=synchroniser_stock_controle(date_debut,date_fin)
                        if result["success"]:
                            st.success(result["message"])
                            st.rerun()
                        else:
                            st.error(result["message"])
                render_export_buttons("controle_stock",display_df,"controle_stock")

# ============================================================
# 12. EXPORT DE L'INVENTAIRE
# ============================================================

with tab_export:
    st.subheader("Exporter l'inventaire")
    keyword=st.text_input("Recherche avant export",key="inventaire_export_keyword")
    result_df=add_inventaire_display_columns(search_inventaires(keyword=keyword if keyword else None))
    if result_df.empty:
        empty_data_message("Aucune donnee a exporter.")
    else:
        render_period_export("inventaire",result_df,"inventaire_export","date_inventaire")
