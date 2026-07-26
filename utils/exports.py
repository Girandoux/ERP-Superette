# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/exports.py
# ROLE : Services utilitaires pour exports CSV/Excel/PDF
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

from pathlib import Path
from typing import Any
import logging
import pandas as pd
from config.settings import REPORTS_DIR
from database import rapports_db
from utils.helpers import clean_text,ensure_parent,error_response,format_money,slugify,success_response,parse_date

logger=logging.getLogger("utils")

# ============================================================
# 1. CHEMINS
# ============================================================


def get_export_path(filename:str,folder:str="excel")->Path:
    """Construit un chemin d'export dans reports."""
    name=clean_text(filename)
    return REPORTS_DIR/folder/name

def build_export_filename(prefix:str,extension:str)->str:
    """Construit un nom de fichier stable."""
    from datetime import datetime
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{slugify(prefix)}_{stamp}.{extension.lstrip('.')}"

# ============================================================
# 2. EXPORT DATAFRAME
# ============================================================

MONEY_EXPORT_COLUMNS={
    "montant","montant_ligne","montant_total","montant_moyen","montant_max","montant_min",
    "total_achat","total_facture","total_vente","frais_enlevement",
    "prix","prix_moyen","pu_vente","pu_achat_carton","pu_achat_piece","cout_unitaire","cout_total",
    "valeur_stock","valeur_unitaire","valeur_totale","valeur_ecart","valeur_perdue",
    "chiffre_affaires","benefice","benefice_net","marge","marge_brute","solde","solde_reel_caisse",
    "entrees","sorties","entrees_reelles","sorties_reelles"
}
MONEY_EXPORT_PREFIXES=("pu_","prix_","cout_","montant_","valeur_","marge_","benefice_","solde_","frais_")
NON_MONEY_EXPORT_COLUMNS={
    "nom_categorie","categorie_depense","motif_perte","type_mouvement","type_vente","unite",
    "qte_cartons","qte_par_carton","qte_vente","qte_perte","quantite_achat","quantite_vendue",
    "stock_actuel","stock_min","stock_minimum","stock_theorique","stock_physique","ecart",
    "total_depenses","total_pertes","total_mouvements","total_categories","total_produits","total_achats","total_ventes","total_lignes"
}

def is_money_export_column(column_name:str)->bool:
    """Detecte les colonnes monetaires pour les exports PDF et apercus Streamlit."""
    col=str(column_name).lower()
    if col in NON_MONEY_EXPORT_COLUMNS or col.endswith("_id") or col.startswith("date_") or col.startswith("code_") or col.startswith("nom_"):
        return False
    return col in MONEY_EXPORT_COLUMNS or any(col.startswith(prefix) for prefix in MONEY_EXPORT_PREFIXES)

def format_money_export_dataframe(df:pd.DataFrame)->pd.DataFrame:
    """Formate une copie du DataFrame pour affichage/PDF sans casser Excel ou CSV."""
    result=df.copy()
    for column in result.columns:
        if is_money_export_column(column) and pd.api.types.is_numeric_dtype(result[column]):
            result[column]=result[column].apply(format_money)
    return result


def export_dataframe_csv(df:pd.DataFrame,path:str|Path,index:bool=False)->dict[str,Any]:
    """Exporte un DataFrame en CSV."""
    try:
        output=ensure_parent(path)
        df.to_csv(output,index=index,encoding="utf-8-sig")
        return success_response("Export CSV termine",str(output))
    except Exception as error:
        logger.exception("Erreur export CSV: %s",error)
        return error_response("Export CSV impossible",str(error))

def clean_excel_sheet_name(name:str)->str:
    """Nettoie un nom d'onglet Excel."""
    cleaned=clean_text(name) or "Donnees"
    for char in ["[","]",":","*","?","/","\\"]:
        cleaned=cleaned.replace(char,"_")
    return cleaned[:31] or "Donnees"

def export_dataframe_excel(df:pd.DataFrame,path:str|Path,sheet_name:str="Donnees",index:bool=False)->dict[str,Any]:
    """Exporte un DataFrame en Excel avec moteur de secours."""
    output=ensure_parent(path)
    sheet=clean_excel_sheet_name(sheet_name)
    errors=[]
    for engine in ("xlsxwriter","openpyxl"):
        try:
            with pd.ExcelWriter(output,engine=engine) as writer:
                df.to_excel(writer,sheet_name=sheet,index=index)
            return success_response("Export Excel termine",str(output))
        except Exception as error:
            errors.append(f"{engine}: {error}")
            logger.exception("Erreur export Excel avec %s: %s",engine,error)
    return error_response("Export Excel impossible : "+" | ".join(errors),str(output))

def export_many_excel(sheets:dict[str,pd.DataFrame],path:str|Path)->dict[str,Any]:
    """Exporte plusieurs DataFrames dans un classeur Excel avec moteur de secours."""
    output=ensure_parent(path)
    errors=[]
    for engine in ("xlsxwriter","openpyxl"):
        try:
            with pd.ExcelWriter(output,engine=engine) as writer:
                used_names=set()
                for name,df in sheets.items():
                    sheet=clean_excel_sheet_name(str(name))
                    base=sheet
                    counter=1
                    while sheet.lower() in used_names:
                        suffix=f"_{counter}"
                        sheet=(base[:31-len(suffix)]+suffix)[:31]
                        counter+=1
                    used_names.add(sheet.lower())
                    df.to_excel(writer,sheet_name=sheet,index=False)
            return success_response("Export Excel termine",str(output))
        except Exception as error:
            errors.append(f"{engine}: {error}")
            logger.exception("Erreur export Excel multi-feuilles avec %s: %s",engine,error)
    return error_response("Export Excel impossible : "+" | ".join(errors),str(output))

def export_dataframe_pdf(df:pd.DataFrame,path:str|Path,title:str="Rapport")->dict[str,Any]:
    """Exporte un DataFrame complet en PDF sans couper les colonnes."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4,landscape
        from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer,PageBreak
        output=ensure_parent(path)
        doc=SimpleDocTemplate(str(output),pagesize=landscape(A4),leftMargin=14,rightMargin=14,topMargin=16,bottomMargin=16)
        styles=getSampleStyleSheet()
        cell_style=ParagraphStyle("Cell",parent=styles["BodyText"],fontName="Helvetica",fontSize=6,leading=7)
        header_style=ParagraphStyle("Header",parent=styles["BodyText"],fontName="Helvetica-Bold",fontSize=6,leading=7,textColor=colors.black)
        data_df=format_money_export_dataframe(df).fillna("").astype(str)
        columns=list(data_df.columns)
        if not columns:
            return error_response("Export PDF impossible","Aucune colonne disponible.")
        max_columns=8
        elements=[Paragraph(clean_text(title),styles["Title"]),Spacer(1,6)]
        elements.append(Paragraph(f"Lignes exportees : {len(data_df)} | Colonnes : {len(columns)}",styles["Normal"]))
        elements.append(Spacer(1,10))
        for start in range(0,len(columns),max_columns):
            chunk=columns[start:start+max_columns]
            if start>0:
                elements.append(PageBreak())
            elements.append(Paragraph(f"{clean_text(title)} - colonnes {start+1} a {start+len(chunk)} / {len(columns)}",styles["Heading2"]))
            table_data=[[Paragraph(clean_text(col),header_style) for col in chunk]]
            for _,row in data_df[chunk].iterrows():
                table_data.append([Paragraph(clean_text(value),cell_style) for value in row.tolist()])
            col_width=doc.width/len(chunk)
            table=Table(table_data,repeatRows=1,colWidths=[col_width]*len(chunk),splitByRow=1)
            table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
                ("TEXTCOLOR",(0,0),(-1,0),colors.black),
                ("GRID",(0,0),(-1,-1),0.25,colors.grey),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.whitesmoke])
            ]))
            elements.append(table)
        doc.build(elements)
        return success_response("Export PDF termine",str(output))
    except ModuleNotFoundError:
        return error_response("Le module reportlab n'est pas installe. Installez-le avec: pip install reportlab")
    except Exception as error:
        logger.exception("Erreur export PDF: %s",error)
        return error_response("Export PDF impossible",str(error))

# ============================================================
# 3. EXPORT RAPPORTS
# ============================================================


def export_rapport(name:str,df:pd.DataFrame,format_export:str="excel")->dict[str,Any]:
    """Exporte un rapport dans le format demande."""
    fmt=clean_text(format_export).lower()
    if fmt=="csv":
        path=get_export_path(build_export_filename(name,"csv"),"csv")
        return export_dataframe_csv(df,path)
    if fmt=="pdf":
        path=get_export_path(build_export_filename(name,"pdf"),"pdf")
        return export_dataframe_pdf(df,path,title=name)
    path=get_export_path(build_export_filename(name,"xlsx"),"excel")
    return export_dataframe_excel(df,path,sheet_name=name)

def is_export_aggregate_column(column_name:str)->bool:
    """Detecte les colonnes numeriques qui ont du sens en regroupement."""
    col=str(column_name).lower()
    if col.endswith("_id") or col.startswith("date_") or col.startswith("code_") or col.startswith("nom_"):
        return False
    if col.startswith(("pu_","prix_")) or col in {"cout_unitaire","valeur_unitaire"}:
        return False
    allowed_exact={
        "montant","montant_ligne","montant_total","total_achat","cout_total",
        "valeur_stock","valeur_totale","valeur_ecart","valeur_perdue",
        "chiffre_affaires","benefice","benefice_net","marge","marge_ligne","marge_brute",
        "entrees","sorties","solde","solde_reel_caisse"
    }
    return col in allowed_exact or col.startswith(("qte_","quantite_","stock_","ecart"))

def group_export_dataframe(df:pd.DataFrame,group_column:str)->pd.DataFrame:
    """Regroupe un export par produit ou categorie avec sommes utiles."""
    if df is None or df.empty or group_column not in df.columns:
        return pd.DataFrame()
    data=df.copy()
    data[group_column]=data[group_column].fillna("Non renseigne").astype(str)
    numeric_columns=[
        column for column in data.columns
        if column!=group_column and pd.api.types.is_numeric_dtype(data[column]) and is_export_aggregate_column(column)
    ]
    grouped=data.groupby(group_column,dropna=False).size().reset_index(name="nombre_lignes")
    if numeric_columns:
        sums=data.groupby(group_column,dropna=False)[numeric_columns].sum().reset_index()
        grouped=grouped.merge(sums,on=group_column,how="left")
    return grouped.sort_values(group_column).reset_index(drop=True)

def prepare_export_dataframe(df:pd.DataFrame,key_prefix:str)->tuple[pd.DataFrame,str]:
    """Prepare l'export detaille ou regroupe."""
    import streamlit as st
    if df is None or df.empty:
        return pd.DataFrame(),"detail"
    group_columns=[column for column in ["nom_produit","nom_categorie"] if column in df.columns]
    if not group_columns:
        return df.copy(),"detail"
    option=st.selectbox(
        "Regrouper l'export par",
        options=["Aucun"]+group_columns,
        key=f"{key_prefix}_export_group_by",
        help="Choisissez nom_produit ou nom_categorie pour exporter une synthese regroupee."
    )
    if option=="Aucun":
        return df.copy(),"detail"
    grouped=group_export_dataframe(df,option)
    st.caption(f"Regroupement actif : {option} | {len(grouped)} ligne(s) de synthese.")
    return grouped,slugify(option)

def select_export_columns(df:pd.DataFrame,key_prefix:str)->pd.DataFrame:
    """Permet de choisir les colonnes a exporter."""
    import streamlit as st
    if df is None or df.empty:
        return pd.DataFrame()
    columns=list(df.columns)
    selected=st.multiselect(
        "Colonnes a exporter",
        options=columns,
        default=columns,
        key=f"{key_prefix}_export_columns",
        help="Decochez les colonnes que vous ne voulez pas exporter."
    )
    if not selected:
        st.warning("Aucune colonne selectionnee. Selectionnez au moins une colonne pour exporter.")
        return pd.DataFrame()
    return df[selected].copy()

def render_export_buttons(name:str,df:pd.DataFrame,key_prefix:str)->None:
    """Affiche regroupement, choix des colonnes puis boutons PDF, Excel et CSV."""
    if df is None or df.empty:
        return
    import streamlit as st
    prepared_df,export_mode=prepare_export_dataframe(df,key_prefix)
    export_df=select_export_columns(prepared_df,f"{key_prefix}_{export_mode}")
    if export_df.empty:
        return
    export_name=f"{name}_{export_mode}" if export_mode!="detail" else name
    st.caption(f"Export prepare : {len(export_df)} ligne(s), {len(export_df.columns)} colonne(s).")
    col1,col2,col3=st.columns(3)
    if col1.button("Exporter PDF",key=f"{key_prefix}_pdf"):
        result=export_rapport(export_name,export_df,"pdf")
        st.success(result["message"]) if result["success"] else st.error(result["message"])
        if result["success"]:
            st.caption(result["data"])
    if col2.button("Exporter Excel",key=f"{key_prefix}_excel"):
        result=export_rapport(export_name,export_df,"excel")
        st.success(result["message"]) if result["success"] else st.error(result["message"])
        if result["success"]:
            st.caption(result["data"])
    if col3.button("Exporter CSV",key=f"{key_prefix}_csv"):
        result=export_rapport(export_name,export_df,"csv")
        st.success(result["message"]) if result["success"] else st.error(result["message"])
        if result["success"]:
            st.caption(result["data"])

def detect_date_column(df:pd.DataFrame,date_column:str|None=None)->str|None:
    """Detecte la meilleure colonne date disponible dans un DataFrame."""
    if df is None or df.empty:
        return date_column
    if date_column and date_column in df.columns:
        return date_column
    candidates=["date_vente","date_achat","date_depense","date_perte","date_mouvement","date_inventaire","date_fabrication","date_peremption","date_id"]
    return next((column for column in candidates if column in df.columns),None)

def filter_dataframe_by_period(df:pd.DataFrame,start_date:Any,end_date:Any,date_column:str|None=None)->pd.DataFrame:
    """Filtre un DataFrame entre deux dates incluses."""
    if df is None or df.empty:
        return pd.DataFrame()
    column=detect_date_column(df,date_column)
    if not column:
        return df.copy()
    start=parse_date(start_date)
    end=parse_date(end_date)
    if not start or not end:
        return df.copy()
    if start>end:
        start,end=end,start
    result=df.copy()
    dates=pd.to_datetime(result[column],errors="coerce").dt.date
    return result[(dates>=start)&(dates<=end)].copy()

def render_period_export(name:str,df:pd.DataFrame,key_prefix:str,date_column:str|None=None,show_preview:bool=True)->pd.DataFrame:
    """Affiche un export PDF/Excel/CSV avec filtre de periode."""
    import streamlit as st
    if df is None or df.empty:
        return pd.DataFrame()
    column=detect_date_column(df,date_column)
    if not column:
        st.info("Aucune colonne date disponible. Export de toutes les donnees.")
        result=df.copy()
    else:
        col1,col2=st.columns(2)
        start_default=parse_date(df[column].min()) or parse_date(None)
        end_default=parse_date(df[column].max()) or parse_date(None)
        start=col1.date_input("Date debut",value=start_default,key=f"{key_prefix}_export_start")
        end=col2.date_input("Date fin",value=end_default,key=f"{key_prefix}_export_end")
        result=filter_dataframe_by_period(df,start,end,column)
        st.caption(f"Periode exportee : {start} au {end} | {len(result)} ligne(s)")
    if result.empty:
        st.warning("Aucune donnee trouvee pour cette periode.")
        return result
    if show_preview:
        from config.styles import display_dataframe
        display_dataframe(result,use_container_width=True,hide_index=True)
    render_export_buttons(name,result,key_prefix)
    return result

def export_all_rapports(date_debut:str|None=None,date_fin:str|None=None)->dict[str,Any]:
    """Exporte tous les rapports dans un fichier Excel."""
    try:
        rapports=rapports_db.get_all_rapports(date_debut,date_fin)
        filename=build_export_filename("rapports_superette","xlsx")
        path=get_export_path(filename,"excel")
        rapports_db.export_rapports_excel(rapports,path)
        return success_response("Tous les rapports ont ete exportes",str(path))
    except Exception as error:
        logger.exception("Erreur export tous rapports: %s",error)
        return error_response("Export des rapports impossible",str(error))

def get_available_export_formats()->list[str]:
    """Retourne les formats supportes."""
    return ["excel","csv","pdf"]

__all__ = [
    "get_export_path",
    "build_export_filename",
    "is_money_export_column",
    "format_money_export_dataframe",
    "export_dataframe_csv",
    "clean_excel_sheet_name",
    "export_dataframe_excel",
    "export_many_excel",
    "export_dataframe_pdf",
    "export_rapport",
    "is_export_aggregate_column",
    "group_export_dataframe",
    "prepare_export_dataframe",
    "select_export_columns",
    "render_export_buttons",
    "detect_date_column",
    "filter_dataframe_by_period",
    "render_period_export",
    "export_all_rapports",
    "get_available_export_formats",
]
