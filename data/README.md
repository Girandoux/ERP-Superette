# 📂 Data

## Übersicht

Der Ordner **`data/`** enthält alle Datenquellen des ERP-Superette-Projekts.

Die Daten werden zunächst aus Excel- und CSV-Dateien übernommen, anschließend mit Python verarbeitet und in die PostgreSQL-Datenbank importiert. PostgreSQL dient als zentrale Datenbasis für die Streamlit-ERP-Anwendung und die Power-BI-Dashboards.

---

# Ordnerstruktur

```text
data/
│
├── README.md
│
├── backup/
│   └── Tabelle_boutique_20260626.xlsx
│
├── processed/
│   └── .gitkeep
│
└── raw/
    ├── csv/
    │   ├── dim_acheteurs.csv
    │   ├── dim_categories.csv
    │   ├── dim_date.csv
    │   ├── dim_lignes_achat.csv
    │   ├── dim_lignes_vente.csv
    │   ├── dim_pertes.csv
    │   ├── dim_produits.csv
    │   ├── dim_vendeurs.csv
    │   ├── fact_achats.csv
    │   ├── fact_depenses.csv
    │   ├── fact_inventaire.csv
    │   ├── fact_tresorerie.csv
    │   └── fact_ventes.csv
    │
    └── excel/
        └── Superette_Data.xlsx
```

---

# Datenfluss

Die Daten werden im ERP-Superette-Projekt nach folgendem Prozess verarbeitet:

```text
CSV-/Excel-Dateien
(Einmalige Datenmigration)
          │
          ▼
Python ETL-Prozess
          │
          ▼
PostgreSQL-Datenbank
(Zentrale Datenbasis)
      ▲             │
      │             │
Lesen & Schreiben   │ Lesen
      │             ▼
 Streamlit ERP   Power BI
      ▲
      │
Benutzer / Superette
```

### Prozessbeschreibung

1. Die Stammdaten und Geschäftsdaten werden einmalig aus **Excel- und CSV-Dateien** übernommen.
2. Der **Python-ETL-Prozess** importiert, validiert und transformiert die Daten.
3. Alle Daten werden zentral in der **PostgreSQL-Datenbank** gespeichert.
4. Die **Streamlit-ERP-Anwendung** liest Daten aus PostgreSQL und speichert neue oder geänderte Daten zurück.
5. **Power BI** greift ausschließlich lesend auf PostgreSQL zu und erstellt Dashboards sowie Berichte.
6. Die Benutzer arbeiten ausschließlich über die Streamlit-Anwendung.

---

# Beschreibung der Ordner

## raw/

Der Ordner **raw** enthält die ursprünglichen Quelldaten des Projekts.

Diese Dateien dienen als Grundlage für den Import in PostgreSQL und sollten nicht direkt bearbeitet werden.

---

## raw/csv/

Dieser Ordner enthält alle CSV-Dateien für den Datenimport.

### Dimensionstabellen

- dim_date.csv
- dim_categories.csv
- dim_produits.csv
- dim_acheteurs.csv
- dim_vendeurs.csv
- dim_lignes_achat.csv
- dim_lignes_vente.csv
- dim_pertes.csv

### Faktentabellen

- fact_achats.csv
- fact_ventes.csv
- fact_depenses.csv
- fact_tresorerie.csv
- fact_inventaire.csv

Diese Dateien werden vom ETL-Prozess eingelesen und in PostgreSQL importiert.

---

## raw/excel/

Enthält die ursprüngliche Excel-Arbeitsmappe.

```text
Superette_Data.xlsx
```

Sie dient als Ausgangspunkt für die Datenerfassung und den Export der CSV-Dateien.

---

## processed/

Dieser Ordner ist für bereinigte oder transformierte Daten vorgesehen.

Aktuell enthält er lediglich eine `.gitkeep`-Datei, damit der Ordner in GitHub erhalten bleibt.

Später können hier beispielsweise gespeichert werden:

- bereinigte CSV-Dateien
- transformierte Datensätze
- validierte Daten
- temporäre ETL-Ergebnisse

---

## backup/

Dieser Ordner enthält Sicherungskopien wichtiger Quelldateien.

Aktuell:

```text
Tabelle_boutique_20260626.xlsx
```

Backups dienen ausschließlich der Datensicherung und sollten nicht als aktive Datenquelle verwendet werden.

---

# Datenimport

Die Daten werden mit den Python- und SQL-Komponenten des Projekts verarbeitet.

Verwendete Importskripte:

```text
database/import_csv.py

database/run_import.py

sql/02_Import_CSV.sql
```

Der ETL-Prozess übernimmt:

- Einlesen der CSV-Dateien
- Datenvalidierung
- Datentransformation
- Import nach PostgreSQL

---

# Datenqualität

Vor dem Import werden die Daten überprüft auf:

- Vollständigkeit der Datensätze
- korrekte Datumsformate
- gültige Zahlenformate
- Primärschlüssel
- Fremdschlüssel
- doppelte Datensätze
- fehlende Werte
- konsistente Produkt- und Kategorienamen
- UTF-8-Kodierung

Eine hohe Datenqualität gewährleistet zuverlässige Analysen und Berichte.

---

# Sicherheit

Im öffentlichen GitHub-Repository sollten keine sensiblen Geschäftsdaten veröffentlicht werden.

Dazu gehören insbesondere:

- Kunden- und Verkäuferdaten
- Einkaufs- und Verkaufsdaten
- Finanz- und Kassendaten
- Inventurdaten
- Datenbanksicherungen
- Zugangsdaten

Für GitHub sollten ausschließlich anonymisierte oder Beispieldaten verwendet werden.

---

# Verwendet von

Die Daten im Ordner `data/` werden verwendet von:

- PostgreSQL
- Python ETL
- Streamlit ERP
- Power BI
- SQL-Skripten
- Dashboard
- Reporting
- Analytics

---

# Zugehörige Projektordner

```text
database/
sql/
streamlit/
powerbi/
reports/
```

Diese Komponenten greifen direkt auf die PostgreSQL-Datenbank zu oder nutzen die Daten aus dem ETL-Prozess.

---

# Lizenz

Dieser Ordner ist Bestandteil des Projekts **ERP Superette**.

© 2026 Girandoux Fandio Nganwajop