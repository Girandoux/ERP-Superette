# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/imports.py
# ROLE : Services utilitaires pour les imports CSV/Excel
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from pathlib import Path
from typing import Any
import logging
import pandas as pd
from config.settings import CSV_DIR,CSV_FILES,CSV_IMPORT_ORDER
from database import import_csv
from utils.helpers import clean_text,error_response,file_exists,success_response

logger=logging.getLogger("utils")

# ============================================================
# 1. LECTURE ET VALIDATION DES FICHIERS
# ============================================================

def get_import_order()->list[str]:
    """Retourne l'ordre d'import des tables."""
    return list(CSV_IMPORT_ORDER)

def get_expected_csv_files()->dict[str,Path]:
    """Retourne les fichiers CSV attendus."""
    return {table:Path(path) for table,path in CSV_FILES.items()}

# Verifie chaque fichier attendu et compte ses lignes de donnees.
def check_csv_files()->dict[str,Any]:
    """Verifie la presence des CSV attendus."""
    files=get_expected_csv_files()
    status={}
    for table,path in files.items():
        status[table]={"path":str(path),"exists":path.exists(),"rows":count_csv_rows(path) if path.exists() else 0}
    missing=[table for table,item in status.items() if not item["exists"]]
    return {"success":len(missing)==0,"missing":missing,"files":status}

def count_csv_rows(path:str|Path)->int:
    """Compte les lignes utiles d'un CSV."""
    file_path=Path(path)
    if not file_path.exists():
        return 0
    try:
        return max(sum(1 for _ in file_path.open("r",encoding="utf-8-sig"))-1,0)
    except UnicodeDecodeError:
        return max(sum(1 for _ in file_path.open("r",encoding="latin1"))-1,0)

def preview_csv(table_name:str,limit:int=20)->pd.DataFrame:
    """Retourne un apercu d'un CSV."""
    path=import_csv.get_csv_path(clean_text(table_name))
    if not file_exists(path):
        return pd.DataFrame()
    df=import_csv.read_csv_file(path)
    return df.head(limit)

def validate_csv(table_name:str)->dict[str,Any]:
    """Valide un CSV avant import."""
    table=clean_text(table_name)
    if table not in CSV_IMPORT_ORDER:
        return error_response("Table inconnue",table)
    if not import_csv.validate_csv_file(table):
        return error_response("Fichier CSV introuvable",str(import_csv.get_csv_path(table)))
    try:
        schema=import_csv.get_database_schema()
        df=import_csv.read_csv_file(import_csv.get_csv_path(table))
        df=import_csv.prepare_dataframe(df,table,schema)
        ok=import_csv.validate_dataframe(df,table,schema)
        return success_response("CSV valide",{"table":table,"rows":len(df)}) if ok else error_response("CSV invalide",{"table":table})
    except Exception as error:
        logger.exception("Erreur validation CSV %s: %s",table,error)
        return error_response("Erreur validation CSV",str(error))

# ============================================================
# 2. IMPORT DES DONNEES DANS POSTGRESQL
# ============================================================

def import_one_table(table_name:str)->dict[str,Any]:
    """Importe une seule table CSV."""
    table=clean_text(table_name)
    if table not in CSV_IMPORT_ORDER:
        return error_response("Table inconnue",table)
    try:
        ok,rows=import_csv.import_table(table)
        return success_response("Table importee",{"table":table,"rows":rows}) if ok else error_response("Import impossible",{"table":table,"rows":rows})
    except Exception as error:
        logger.exception("Erreur import %s: %s",table,error)
        return error_response("Erreur import",str(error))

def import_all_tables(clean_before:bool=True,reset_after:bool=True)->dict[str,Any]:
    """Importe tous les CSV dans PostgreSQL."""
    try:
        result=import_csv.import_all_tables(clean_before=clean_before,reset_seq=reset_after)
        return success_response("Import termine",result)
    except Exception as error:
        logger.exception("Erreur import complet: %s",error)
        return error_response("Erreur import complet",str(error))

def truncate_import_tables()->dict[str,Any]:
    """Vide les tables d'import."""
    try:
        import_csv.truncate_tables()
        return success_response("Tables videes")
    except Exception as error:
        logger.exception("Erreur truncate tables: %s",error)
        return error_response("Vidage des tables impossible",str(error))

def reset_import_sequences()->dict[str,Any]:
    """Reinitialise les sequences apres import."""
    try:
        import_csv.reset_sequences()
        return success_response("Sequences synchronisees")
    except Exception as error:
        logger.exception("Erreur reset sequences: %s",error)
        return error_response("Synchronisation des sequences impossible",str(error))

# ============================================================
# 3. LECTURE ET CONVERSION DES FICHIERS EXCEL
# ============================================================

def read_excel_sheets(path:str|Path)->dict[str,pd.DataFrame]:
    """Lit toutes les feuilles d'un fichier Excel."""
    file_path=Path(path)
    if not file_path.exists():
        return {}
    return pd.read_excel(file_path,sheet_name=None)

# Chaque feuille Excel est convertie dans un fichier CSV distinct.
def save_excel_sheets_as_csv(path:str|Path,output_dir:str|Path=CSV_DIR)->dict[str,Path]:
    """Convertit les feuilles Excel en CSV."""
    sheets=read_excel_sheets(path)
    output=Path(output_dir)
    output.mkdir(parents=True,exist_ok=True)
    saved={}
    for sheet,df in sheets.items():
        csv_path=output/f"{sheet}.csv"
        df.to_csv(csv_path,index=False,encoding="utf-8-sig")
        saved[sheet]=csv_path
    return saved

def get_import_resume()->dict[str,Any]:
    """Retourne un resume de l'etat des imports."""
    check=check_csv_files()
    return {"csv_dir":str(CSV_DIR),"total_tables":len(CSV_IMPORT_ORDER),"missing_count":len(check["missing"]),"missing":check["missing"],"files":check["files"]}

__all__ = [
    "get_import_order",
    "get_expected_csv_files",
    "check_csv_files",
    "count_csv_rows",
    "preview_csv",
    "validate_csv",
    "import_one_table",
    "import_all_tables",
    "truncate_import_tables",
    "reset_import_sequences",
    "read_excel_sheets",
    "save_excel_sheets_as_csv",
    "get_import_resume",
]
