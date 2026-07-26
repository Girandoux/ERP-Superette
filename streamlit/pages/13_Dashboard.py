# ============================================================
# PROJET : GESTION DE SUPERETTE
# PAGE : 13_Dashboard.py
# ROLE : Dashboard analytique Streamlit
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
import streamlit as st
from config.styles import display_dataframe,empty_data_message,hero_panel,kpi_card
from utils.charts import chart_achats_mensuels,chart_depenses_mensuelles,chart_pertes_mensuelles,chart_stock_par_categorie,chart_top_produits_achetes,chart_top_produits_vendus,chart_tresorerie,chart_ventes_mensuelles
from utils.dashboard import format_dashboard_kpis,load_dashboard_data
from utils.helpers import format_money

# ============================================================
# 1. STYLE ET COMPOSANTS VISUELS
# ============================================================

st.markdown("""
<style>
.dashboard-readout{border:1px solid #dfe7ef;border-radius:8px;background:#ffffff;padding:14px 16px;margin:8px 0 18px 0;}
.dashboard-readout h4{margin:0 0 8px 0;color:#1e293b;font-size:1rem;font-weight:800;}
.dashboard-readout p{margin:0;color:#64748b;font-size:.92rem;line-height:1.45;}
.section-kicker{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:#0f766e;font-weight:800;margin-top:8px;}
.risk-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:10px 0 18px 0;}
.risk-item{border:1px solid #dfe7ef;border-radius:8px;padding:12px 14px;background:#fff;}
.risk-label{font-size:.76rem;color:#64748b;font-weight:700;text-transform:uppercase;}
.risk-value{font-size:1.55rem;font-weight:850;color:#0f766e;line-height:1.25;}
.risk-danger .risk-value{color:#dc2626;}
.risk-warning .risk-value{color:#f59e0b;}
@media (max-width: 900px){.risk-strip{grid-template-columns:1fr;}}
</style>
""",unsafe_allow_html=True)

# ============================================================
# 2. FONCTIONS D'AIDE DU DASHBOARD
# ============================================================

__all__ = [
    "readout",
    "risk_strip",
    "dashboard_comment",
]

def readout(title:str,body:str)->None:
    """Affiche un resume analytique court dans un encart visuel."""
    st.markdown(f'<div class="dashboard-readout"><h4>{title}</h4><p>{body}</p></div>',unsafe_allow_html=True)

def risk_strip(kpis:dict)->None:
    """Affiche les principaux signaux de risque operationnel."""
    alertes=int(kpis.get("alertes_stock",0) or 0)
    ruptures=int(kpis.get("ruptures_stock",0) or 0)
    ventes=int(kpis.get("nombre_ventes",0) or 0)
    st.markdown(
        f"""
        <div class="risk-strip">
            <div class="risk-item"><div class="risk-label">Ventes enregistrees</div><div class="risk-value">{ventes}</div></div>
            <div class="risk-item risk-warning"><div class="risk-label">Alertes stock</div><div class="risk-value">{alertes}</div></div>
            <div class="risk-item risk-danger"><div class="risk-label">Ruptures stock</div><div class="risk-value">{ruptures}</div></div>
        </div>
        """,
        unsafe_allow_html=True
    )

def dashboard_comment(kpis:dict)->str:
    """Construit une lecture metier a partir des indicateurs charges."""
    ca=float(kpis.get("chiffre_affaires",0) or 0)
    benefice=float(kpis.get("benefice_net",0) or 0)
    pertes=float(kpis.get("total_pertes",0) or 0)
    ruptures=int(kpis.get("ruptures_stock",0) or 0)
    if ca<=0:
        return "Aucune activite commerciale significative n'est encore visible sur la periode chargee."
    marge_text="positive" if benefice>=0 else "negative"
    risk_text=" Des ruptures de stock demandent une action rapide." if ruptures>0 else " Le stock ne montre pas de rupture critique."
    return f"Le chiffre d'affaires charge est de {format_money(ca)} avec une rentabilite {marge_text} de {format_money(benefice)}. Les pertes suivies representent {format_money(pertes)}.{risk_text}"

# ============================================================
# 3. TITRE ET CHARGEMENT DES DONNEES
# ============================================================

hero_panel(
    "Dashboard analytique",
    "Pilotage commercial de la superette : ventes, achats, stock, depenses, pertes et tresorerie dans une vue claire et exploitable.",
    ["Performance", "Stock", "Finance", "Decision"]
)
# Le dashboard centralise les donnees commerciales, le stock et la finance
# avant de calculer les indicateurs et les commentaires de synthese.
data=load_dashboard_data()
kpis=format_dashboard_kpis(data.get("kpis",{}))

# La lecture rapide transforme les principaux KPI en un commentaire
# directement exploitable pour la prise de decision.
readout("Lecture rapide",dashboard_comment(kpis))

# ============================================================
# 4. INDICATEURS DE PERFORMANCE
# ============================================================

st.markdown('<div class="section-kicker">Performance financiere</div>',unsafe_allow_html=True)
c1,c2,c3,c4=st.columns(4)
with c1:
    kpi_card("Chiffre d'affaires",kpis.get("chiffre_affaires_affiche","0 FCFA"))
with c2:
    kpi_card("Benefice net",kpis.get("benefice_net_affiche","0 FCFA"))
with c3:
    kpi_card("Valeur stock",kpis.get("valeur_stock_affiche","0 FCFA"))
with c4:
    kpi_card("Solde reel caisse",kpis.get("solde_tresorerie_affiche","0 FCFA"))

st.markdown('<div class="section-kicker">Activite et risques</div>',unsafe_allow_html=True)
risk_strip(kpis)

# ============================================================
# 5. ANALYSES VISUELLES
# ============================================================

st.markdown('<div class="section-kicker">Analyse visuelle</div>',unsafe_allow_html=True)
tab_evolution,tab_produits,tab_stock,tab_finance=st.tabs(["Evolution","Produits","Stock","Finance"])

# Les onglets separent l'evolution temporelle, les produits, le stock
# et la tresorerie sans modifier les donnees chargees.
with tab_evolution:
    readout("Evolution", "Suivez la relation entre ventes, achats, depenses et pertes pour identifier les periodes fortes et les points de pression.")
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(chart_ventes_mensuelles(data.get("ventes_mensuelles")),use_container_width=True)
    with col2:
        st.plotly_chart(chart_achats_mensuels(data.get("achats_mensuels")),use_container_width=True)
    col3,col4=st.columns(2)
    with col3:
        st.plotly_chart(chart_depenses_mensuelles(data.get("depenses_mensuelles")),use_container_width=True)
    with col4:
        st.plotly_chart(chart_pertes_mensuelles(data.get("pertes_mensuelles")),use_container_width=True)

with tab_produits:
    readout("Produits", "Reperez les produits qui portent le chiffre d'affaires et ceux qui concentrent les achats.")
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(chart_top_produits_vendus(data.get("top_produits_vendus")),use_container_width=True)
    with col2:
        st.plotly_chart(chart_top_produits_achetes(data.get("top_produits_achetes")),use_container_width=True)

with tab_stock:
    readout("Stock", "La priorite est de reduire les ruptures et de maintenir les produits rapides au-dessus du seuil minimum.")
    col1,col2=st.columns([1,2])
    with col1:
        st.plotly_chart(chart_stock_par_categorie(data.get("stock_par_categorie")),use_container_width=True)
    with col2:
        alertes=data.get("alertes_stock")
        if alertes is not None and not alertes.empty:
            display_dataframe(alertes,use_container_width=True,hide_index=True)
        else:
            empty_data_message("Aucune alerte stock.")

with tab_finance:
    readout("Finance", "Controlez les mouvements de caisse et rapprochez les entrees, sorties, retraits et corrections.")
    tresorerie=data.get("flux_tresorerie")
    st.plotly_chart(chart_tresorerie(tresorerie),use_container_width=True)
    if tresorerie is not None and not tresorerie.empty:
        display_dataframe(tresorerie,use_container_width=True,hide_index=True)
    else:
        empty_data_message("Aucun mouvement de tresorerie disponible.")
