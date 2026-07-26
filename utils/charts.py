# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/charts.py
# ROLE : Graphiques Plotly pour Streamlit
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

from typing import Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. CONFIGURATION VISUELLE
# ============================================================

DEFAULT_TEMPLATE="plotly_white"
COLOR_PRIMARY="#047857"
COLOR_SECONDARY="#2563EB"
COLOR_SUCCESS="#047857"
COLOR_WARNING="#D97706"
COLOR_DANGER="#DC2626"
COLOR_MUTED="#64748B"
COLOR_GRID="#E2E8F0"
COLOR_TEXT="#1E293B"
COLOR_BG="#FFFFFF"
COLOR_SEQUENCE=[COLOR_PRIMARY,COLOR_SECONDARY,COLOR_WARNING,COLOR_DANGER,"#0EA5E9","#14B8A6","#8B5CF6","#64748B"]

LABELS={
    "mois":"Mois",
    "date_mouvement":"Date",
    "chiffre_affaires":"Chiffre d'affaires",
    "total_achats":"Achats",
    "total_depenses":"Depenses",
    "valeur_perdue":"Pertes",
    "nom_produit":"Produit",
    "nom_categorie":"Categorie",
    "stock_total":"Stock total",
    "montant":"Montant",
    "categorie_depense":"Categorie",
    "motif_perte":"Motif",
    "type_mouvement":"Type",
    "marge":"Marge",
    "resultat_net":"Resultat net",
    "taux_rotation":"Taux de rotation"
}

def apply_layout(fig:go.Figure,title:str|None=None,height:int=380)->go.Figure:
    """Applique un style commun plus professionnel aux graphiques."""
    fig.update_layout(
        template=DEFAULT_TEMPLATE,
        title=dict(text=title or "",x=0.02,xanchor="left",font=dict(size=17,color=COLOR_TEXT,family="Arial")),
        height=height,
        margin=dict(l=18,r=18,t=62,b=28),
        legend_title_text="",
        font=dict(size=12,color=COLOR_TEXT,family="Arial"),
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        colorway=COLOR_SEQUENCE,
        hoverlabel=dict(bgcolor="#0F172A",font_size=12,font_color="#FFFFFF")
    )
    fig.update_xaxes(showgrid=False,zeroline=False,title_font=dict(size=12,color=COLOR_MUTED),tickfont=dict(color=COLOR_MUTED))
    fig.update_yaxes(gridcolor=COLOR_GRID,zeroline=False,title_font=dict(size=12,color=COLOR_MUTED),tickfont=dict(color=COLOR_MUTED))
    return fig

def empty_chart(message:str="Aucune donnee disponible")->go.Figure:
    """Retourne un graphique vide."""
    fig=go.Figure()
    fig.add_annotation(text=message,x=0.5,y=0.52,showarrow=False,font=dict(size=15,color=COLOR_MUTED))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return apply_layout(fig,height=300)

def _has_columns(df:pd.DataFrame|None,columns:list[str])->bool:
    return df is not None and not df.empty and all(col in df.columns for col in columns)

def _money_axis(fig:go.Figure,axis:str="y")->go.Figure:
    """Formate un axe monetaire compact."""
    if axis=="y":
        fig.update_yaxes(tickformat=",.0f",ticksuffix=" FCFA")
    else:
        fig.update_xaxes(tickformat=",.0f",ticksuffix=" FCFA")
    return fig

# ============================================================
# 2. GRAPHIQUES GENERIQUES
# ============================================================


def line_chart(df:pd.DataFrame,x:str,y:str,title:str="",color:str|None=None)->go.Figure:
    """Cree un graphique en ligne."""
    if not _has_columns(df,[x,y]):
        return empty_chart()
    fig=px.line(df,x=x,y=y,color=color,markers=True,labels=LABELS,color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_traces(line=dict(width=3,color=COLOR_PRIMARY),marker=dict(size=8,line=dict(width=2,color="#FFFFFF")))
    return apply_layout(fig,title)

def bar_chart(df:pd.DataFrame,x:str,y:str,title:str="",color:str|None=None,orientation:str="v")->go.Figure:
    """Cree un graphique en barres."""
    if not _has_columns(df,[x,y]):
        return empty_chart()
    fig=px.bar(df,x=x,y=y,color=color,orientation=orientation,labels=LABELS,color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_traces(marker_line_width=0,opacity=0.92)
    return apply_layout(fig,title)

def pie_chart(df:pd.DataFrame,names:str,values:str,title:str="")->go.Figure:
    """Cree un graphique circulaire."""
    if not _has_columns(df,[names,values]):
        return empty_chart()
    fig=px.pie(df,names=names,values=values,hole=0.55,labels=LABELS,color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_traces(textposition="inside",textinfo="percent+label",marker=dict(line=dict(color="#FFFFFF",width=2)))
    return apply_layout(fig,title,height=380)

def area_chart(df:pd.DataFrame,x:str,y:str,title:str="",color:str|None=None)->go.Figure:
    """Cree un graphique en aire."""
    if not _has_columns(df,[x,y]):
        return empty_chart()
    fig=px.area(df,x=x,y=y,color=color,labels=LABELS,color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_traces(line=dict(width=2))
    return apply_layout(fig,title)

def indicator_card(value:Any,title:str,delta:Any=None,prefix:str="",suffix:str="")->go.Figure:
    """Cree un indicateur Plotly."""
    fig=go.Figure(go.Indicator(mode="number+delta" if delta is not None else "number",value=float(value or 0),delta={"reference":float(delta or 0)} if delta is not None else None,number={"prefix":prefix,"suffix":suffix},title={"text":title}))
    return apply_layout(fig,height=210)

# ============================================================
# 3. GRAPHIQUES DASHBOARD
# ============================================================


def chart_ventes_mensuelles(df:pd.DataFrame)->go.Figure:
    """Graphique du chiffre d'affaires mensuel."""
    fig=line_chart(df,"mois","chiffre_affaires","Evolution mensuelle du chiffre d'affaires")
    return _money_axis(fig,"y")

def chart_achats_mensuels(df:pd.DataFrame)->go.Figure:
    """Graphique des achats mensuels."""
    fig=bar_chart(df,"mois","total_achats","Achats mensuels")
    fig.update_traces(marker_color=COLOR_SECONDARY)
    return _money_axis(fig,"y")

def chart_depenses_mensuelles(df:pd.DataFrame)->go.Figure:
    """Graphique des depenses mensuelles par categorie."""
    fig=bar_chart(df,"mois","total_depenses","Depenses par categorie","categorie_depense")
    return _money_axis(fig,"y")

def chart_pertes_mensuelles(df:pd.DataFrame)->go.Figure:
    """Graphique des pertes mensuelles."""
    fig=bar_chart(df,"mois","valeur_perdue","Pertes par motif","motif_perte")
    return _money_axis(fig,"y")

def chart_top_produits_vendus(df:pd.DataFrame)->go.Figure:
    """Graphique top produits vendus."""
    if not _has_columns(df,["nom_produit","chiffre_affaires"]):
        return empty_chart()
    data=df.sort_values("chiffre_affaires",ascending=True).tail(12)
    fig=bar_chart(data,"chiffre_affaires","nom_produit","Meilleurs produits par chiffre d'affaires",orientation="h")
    fig.update_traces(marker_color=COLOR_PRIMARY)
    return _money_axis(fig,"x")

def chart_top_produits_achetes(df:pd.DataFrame)->go.Figure:
    """Graphique top produits achetes."""
    if not _has_columns(df,["nom_produit","total_achats"]):
        return empty_chart()
    data=df.sort_values("total_achats",ascending=True).tail(12)
    fig=bar_chart(data,"total_achats","nom_produit","Produits les plus achetes",orientation="h")
    fig.update_traces(marker_color=COLOR_SECONDARY)
    return _money_axis(fig,"x")

def chart_stock_par_categorie(df:pd.DataFrame)->go.Figure:
    """Graphique stock par categorie."""
    return pie_chart(df,"nom_categorie","stock_total","Repartition du stock par categorie")

def chart_statut_stock(df:pd.DataFrame)->go.Figure:
    """Graphique repartition des statuts stock."""
    if df is None or df.empty or "statut_stock" not in df.columns:
        return empty_chart()
    data=df["statut_stock"].value_counts().reset_index()
    data.columns=["statut_stock","total"]
    fig=px.pie(data,names="statut_stock",values="total",hole=0.55,color="statut_stock",color_discrete_map={"NORMAL":COLOR_SUCCESS,"ALERTE":COLOR_WARNING,"RUPTURE":COLOR_DANGER})
    return apply_layout(fig,"Statut du stock")

def chart_tresorerie(df:pd.DataFrame)->go.Figure:
    """Graphique des mouvements de tresorerie avec couleurs metier."""
    if not _has_columns(df,["date_mouvement","montant"]):
        return empty_chart()
    color="type_mouvement" if "type_mouvement" in df.columns else None
    color_map={
        "Vente":COLOR_SUCCESS,
        "Apport":COLOR_PRIMARY,
        "Achat":COLOR_DANGER,
        "Depense":COLOR_WARNING,
        "DÃ©pense":COLOR_WARNING,
        "Retrait":COLOR_DANGER,
        "Depot banque":COLOR_SECONDARY,
        "DÃ©pÃ´t banque":COLOR_SECONDARY,
        "Retrait banque":COLOR_DANGER,
        "Correction":COLOR_MUTED,
    }
    fig=px.bar(
        df,
        x="date_mouvement",
        y="montant",
        color=color,
        labels=LABELS,
        color_discrete_map=color_map if color else None,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_traces(marker_line_width=0,opacity=0.92)
    return _money_axis(apply_layout(fig,"Flux de tresorerie"),"y")

# ============================================================
# 4. GRAPHIQUES ANALYTIQUES
# ============================================================


def chart_marge(df:pd.DataFrame)->go.Figure:
    """Graphique de marge."""
    if not _has_columns(df,["periode","marge"]):
        return empty_chart()
    fig=px.line(df,x="periode",y=["chiffre_affaires","cout_total","marge"] if {"chiffre_affaires","cout_total"}.issubset(df.columns) else "marge",markers=True,labels=LABELS,color_discrete_sequence=COLOR_SEQUENCE)
    return _money_axis(apply_layout(fig,"Analyse de marge"),"y")

def chart_resultat(df:pd.DataFrame)->go.Figure:
    """Graphique du resultat net."""
    fig=line_chart(df,"periode","resultat_net","Evolution du resultat net")
    return _money_axis(fig,"y")

def chart_performance_categories(df:pd.DataFrame)->go.Figure:
    """Graphique performance categories."""
    fig=bar_chart(df,"nom_categorie","chiffre_affaires","Performance par categorie")
    return _money_axis(fig,"y")

def chart_rotation_stock(df:pd.DataFrame)->go.Figure:
    """Graphique rotation stock."""
    if not _has_columns(df,["nom_produit","taux_rotation"]):
        return empty_chart()
    data=df.sort_values("taux_rotation",ascending=True).tail(20)
    return bar_chart(data,"taux_rotation","nom_produit","Rotation du stock",orientation="h")

__all__ = [
    "apply_layout",
    "empty_chart",
    "line_chart",
    "bar_chart",
    "pie_chart",
    "area_chart",
    "indicator_card",
    "chart_ventes_mensuelles",
    "chart_achats_mensuels",
    "chart_depenses_mensuelles",
    "chart_pertes_mensuelles",
    "chart_top_produits_vendus",
    "chart_top_produits_achetes",
    "chart_stock_par_categorie",
    "chart_statut_stock",
    "chart_tresorerie",
    "chart_marge",
    "chart_resultat",
    "chart_performance_categories",
    "chart_rotation_stock",
]
