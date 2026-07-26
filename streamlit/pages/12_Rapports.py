# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 12_Rapports.py
# ROLE : Consultation et export des rapports
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from datetime import date
import streamlit as st
from config.styles import display_dataframe,empty_data_message,info_box,kpi_card,page_title
from database import rapports_db
from utils.exports import export_all_rapports,render_export_buttons
from utils.helpers import format_money

# ============================================================
# 1. TITRE DE LA PAGE
# ============================================================

# Le parcours suit la selection, le filtrage, l'affichage
# puis l'export des donnees du rapport.
page_title("Rapports","Rapports operationnels et financiers de la superette")


# ============================================================
# 2. CONFIGURATION DU FORMATAGE
# ============================================================

__all__ = [
    "is_money_column",
    "format_report_display",
]

MONEY_COLUMNS={
    "montant","montant_ligne","montant_total","montant_moyen","montant_max","montant_min",
    "total","total_achat","total_facture","total_vente","total_depenses","total_pertes",
    "frais_enlevement","prix","prix_moyen","pu_vente","pu_achat_carton","pu_achat_piece",
    "cout_unitaire","cout_total","cout_achat","cout_stock","valeur_stock","valeur_unitaire",
    "valeur_totale","valeur_ecart","chiffre_affaires","benefice","benefice_net",
    "marge","marge_brute","solde","entrees","sorties"
}
MONEY_PREFIXES=("pu_","prix_","cout_","montant_","valeur_","total_","marge_")
NON_MONEY_COLUMNS={
    "nom_categorie","categorie_depense","motif_perte","type_mouvement","type_vente",
    "qte_cartons","qte_par_carton","qte_vente","qte_perte","quantite_achat","quantite_vendue",
    "stock_actuel","stock_min","stock_minimum","stock_theorique","stock_physique",
    "ecart","produit_id","achat_id","vente_id","depense_id","perte_id","inventaire_id","date_id"
}

def is_money_column(column_name):
    """Indique si une colonne doit etre affichee comme valeur monetaire."""
    col=str(column_name).lower()
    if col in NON_MONEY_COLUMNS or col.endswith("_id") or col.startswith("date_"):
        return False
    return col in MONEY_COLUMNS or any(col.startswith(prefix) for prefix in MONEY_PREFIXES)

def format_report_display(df):
    """Formate les colonnes monetaires sans modifier les donnees exportees."""
    if df.empty:
        return df
    result=df.copy()
    for col in result.columns:
        if is_money_column(col):
            result[col]=result[col].apply(lambda value: format_money(value) if value not in (None,"") else "")
    return result

# ============================================================
# 3. CATALOGUE DES RAPPORTS
# ============================================================

# Chaque libelle pointe vers la fonction de chargement correspondante.
RAPPORTS={
    "Ventes":rapports_db.get_rapport_ventes,
    "Achats":rapports_db.get_rapport_achats,
    "Stock":rapports_db.get_rapport_stock,
    "Depenses":rapports_db.get_rapport_depenses,
    "Pertes":rapports_db.get_rapport_pertes,
    "Inventaire":rapports_db.get_rapport_inventaire,
    "Tresorerie":rapports_db.get_rapport_tresorerie,
    "Profitabilite":rapports_db.get_rapport_profitabilite,
    "Controle prix":rapports_db.get_rapport_controle_prix
}
# Les descriptions presentent le contenu attendu dans l'interface.
RAPPORT_DESCRIPTIONS={
    "Ventes":"Detail des ventes, produits, vendeurs, chiffre d'affaires et marges.",
    "Achats":"Controle des factures, lignes d'achat, couts et volumes achetes.",
    "Stock":"Etat du stock actuel, seuils minimums, valeur et alertes.",
    "Depenses":"Suivi des charges par categorie et par periode.",
    "Pertes":"Controle des pertes, motifs, quantites et valeurs perdues.",
    "Inventaire":"Suivi des inventaires, ecarts, clotures et corrections.",
    "Tresorerie":"Lecture des mouvements de caisse et du solde financier.",
    "Profitabilite":"Classement des produits selon chiffre d'affaires, couts et marges.",
    "Controle prix":"Compare le dernier cout d'achat avec le dernier prix de vente pour detecter les produits non rentables."
}

# ============================================================
# 4. FILTRES DU RAPPORT
# ============================================================

with st.container(border=True):
    st.markdown("##### Selection du rapport")
    col1,col2,col3=st.columns([1.2,1,1])
    rapport_name=col1.selectbox("Rapport",list(RAPPORTS.keys()))
    date_debut=col2.date_input("Date debut",value=date.today())
    date_fin=col3.date_input("Date fin",value=date.today())
    use_dates=st.checkbox("Appliquer le filtre de dates",value=False)
    info_box(RAPPORT_DESCRIPTIONS.get(rapport_name,"Rapport operationnel de la superette."))

# ============================================================
# 5. CHARGEMENT ET AFFICHAGE
# ============================================================

st.subheader(f"Rapport {rapport_name}")
# Les donnees sont chargees selon le rapport et la periode choisis.
rapport_func=RAPPORTS[rapport_name]
if rapport_name=="Stock":
    df=rapport_func()
elif use_dates:
    df=rapport_func(str(date_debut),str(date_fin))
else:
    df=rapport_func()

periode_label=f"{date_debut} au {date_fin}" if use_dates and rapport_name!="Stock" else "Toutes les donnees"
s1,s2,s3,s4=st.columns(4)
with s1:
    kpi_card("Rapport",rapport_name)
with s2:
    kpi_card("Lignes",len(df))
with s3:
    kpi_card("Periode",periode_label)
with s4:
    kpi_card("Export",("Disponible" if not df.empty else "Aucune donnee"))
if df.empty:
    empty_data_message("Aucune donnee disponible pour ce rapport.")
else:
    display_dataframe(format_report_display(df),use_container_width=True,hide_index=True)
    st.caption(f"{len(df)} ligne(s) affichee(s).")

# ============================================================
# 6. EXPORT DES RAPPORTS
# ============================================================

st.subheader("Export")
# Les exports conservent les valeurs brutes, independamment
# du formatage applique uniquement a l'affichage.
with st.container(border=True):
    info_box("Les exports utilisent les donnees brutes du rapport pour conserver des fichiers Excel, CSV et PDF propres.")
    if not df.empty:
        render_export_buttons(rapport_name.lower(),df,f"rapport_{rapport_name.lower()}")
    if st.button("Exporter tous les rapports Excel"):
        if use_dates:
            result=export_all_rapports(str(date_debut),str(date_fin))
        else:
            result=export_all_rapports()
        st.success(result["message"]) if result["success"] else st.error(result["message"])

# ============================================================
# 7. AIDE SUR LE CONTENU
# ============================================================

with st.expander("Contenu des rapports"):
    st.write("Ventes : detail des ventes, produits, vendeurs, marges.")
    st.write("Controle prix : dernier prix d'achat, dernier prix de vente, marge unitaire et statut rentable.")
    st.write("Achats : factures, fournisseurs, lignes et couts d'achat.")
    st.write("Stock : stock actuel, seuils, valeur et statut.")
    st.write("Depenses, pertes, inventaire et tresorerie : suivi financier et controle.")


