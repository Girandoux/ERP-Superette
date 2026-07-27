# 🗄️ PostgreSQL-Datenbank

## SQL-Struktur des Projekts „Gestion de Superette“

> [!NOTE]
> **Projektkontext**
>
> Dieses Projekt basiert auf einem realen Anwendungsfall einer kleinen Superette in Kamerun.
>
> Nach einer Analyse der Geschäftsprozesse wurde ein relationales Datenmodell (ERD) entwickelt und darauf aufbauend eine PostgreSQL-Datenbank konzipiert und implementiert.
>
> Die Datenbank bildet das zentrale Fundament des ERP-Systems und verwaltet sämtliche Geschäftsdaten – von Produkten, Einkäufen und Verkäufen über Lagerbewegungen und Inventuren bis hin zu Betriebsausgaben und der Kassenführung.
>
> Sie stellt eine gemeinsame Datenbasis für die Streamlit-Anwendung und die Power BI-Dashboards bereit und gewährleistet eine konsistente, strukturierte und zuverlässige Speicherung aller Geschäftsdaten.
>
> Ziel war es, eine leistungsfähige relationale Datenbank mit Tabellen, Beziehungen, Views, Funktionen, Triggern und Indizes zu entwickeln, die sowohl den täglichen Geschäftsbetrieb als auch umfangreiche Analysen und Berichte unterstützt.
---

# 📖 Inhaltsverzeichnis

- Projektübersicht
- Ziele der Datenbank
- Architektur
- Aufbau des SQL-Ordners
- Beschreibung der SQL-Dateien
- Empfohlene Ausführungsreihenfolge
- Datenmodell
- Tabellenübersicht
- SQL-Views
- SQL-Funktionen
- SQL-Trigger
- Indizes
- CSV-Import
- Verwendung mit Streamlit
- Verwendung mit Power BI
- Installation
- Hinweise
- Weiterführende Dokumentation

---

# 🎯 Projektübersicht

Dieses Verzeichnis enthält alle SQL-Skripte, die für den Aufbau und den Betrieb der PostgreSQL-Datenbank benötigt werden.

Die Datenbank wurde speziell für dieses Projekt entwickelt und bildet sämtliche Geschäftsprozesse einer kleinen Superette ab.

Dazu gehören unter anderem:

- Verwaltung der Produktstammdaten
- Verwaltung der Kategorien
- Einkaufsverwaltung
- Verkaufsverwaltung
- Lagerverwaltung
- Inventur
- Verlustverwaltung
- Betriebsausgaben
- Kassenverwaltung
- Bereitstellung von Daten für Auswertungen

Neben der Speicherung der operativen Daten stellt die Datenbank auch analytische Views bereit, die in Streamlit und Power BI verwendet werden.

---

# 🏗️ Ziele der Datenbank

Bei der Entwicklung der Datenbank standen folgende Ziele im Vordergrund:

- Zentrale Speicherung aller Geschäftsdaten
- Hohe Datenqualität durch relationale Tabellen
- Automatisierung wiederkehrender Berechnungen
- Unterstützung der täglichen Geschäftsprozesse
- Schnelle Auswertungen für Berichte und Dashboards
- Gute Performance auch bei größeren Datenmengen
- Einfache Erweiterbarkeit für zukünftige Funktionen

Die PostgreSQL-Datenbank bildet damit die Grundlage für alle Module des Projekts.

---

# 🏛️ Systemarchitektur

Die PostgreSQL-Datenbank bildet das zentrale Fundament des ERP-Systems. Sie verwaltet sämtliche Geschäftsdaten und stellt diese der Streamlit-Anwendung sowie Power BI zur Verfügung.

```text
      Geschäftsprozessanalyse
               │
               ▼
     ERD & relationales Datenmodell
               │
               ▼
      PostgreSQL-Datenbank
 ┌─────────────────────────────────────┐
 │ Tabellen                            │
 │ Beziehungen (PK/FK)                 │
 │ Views                               │
 │ Funktionen                          │
 │ Trigger                             │
 │ Indizes                             │
 └─────────────────────────────────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
Python / Streamlit    Power BI
 (Schreiben & Lesen)   (Lesen)
```

Die Datenbank wurde auf Grundlage eines selbst entwickelten Entity-Relationship-Diagramms (ERD) aufgebaut.

Die Streamlit-Anwendung nutzt Tabellen, Views und Funktionen zur täglichen Verwaltung der Geschäftsprozesse. Power BI greift auf dieselbe Datenbasis – insbesondere auf vorbereitete SQL-Views – zu, um Dashboards, KPIs und Berichte bereitzustellen.

Vorhandene Excel- und CSV-Dateien wurden ausschließlich einmalig zur Migration historischer Daten in die PostgreSQL-Datenbank verwendet.
---

# 📂 Aufbau des SQL-Ordners

```text
sql/
│
├── 01_Create_Database.sql
├── 02_Import_CSV.sql
├── 03_SQL_Analytics.sql
├── 04_Views.sql
├── 05_Functions.sql
├── 06_Triggers.sql
├── 07_Indexes.sql
├── 08_Migration_Vente_Declassee.sql
└── README.md
```

Jede SQL-Datei übernimmt eine klar definierte Aufgabe. Durch diese Struktur können einzelne Komponenten unabhängig voneinander gepflegt und bei Bedarf erweitert werden.

---

# 📄 Beschreibung der SQL-Dateien

| Datei | Beschreibung |
|--------|--------------|
| **01_Create_Database.sql** | Erstellt die Datenbankstruktur mit Tabellen, Primär- und Fremdschlüsseln sowie den notwendigen Integritätsregeln. |
| **02_Import_CSV.sql** | Importiert die Stammdaten und Beispieldaten aus den CSV-Dateien. |
| **03_SQL_Analytics.sql** | Enthält verschiedene Analyseabfragen und SQL-Auswertungen. |
| **04_Views.sql** | Erstellt alle SQL-Views für Streamlit und Power BI. |
| **05_Functions.sql** | Definiert wiederverwendbare SQL-Funktionen für Berechnungen und Geschäftslogik. |
| **06_Triggers.sql** | Automatisiert verschiedene Abläufe innerhalb der Datenbank. |
| **07_Indexes.sql** | Erstellt Indizes zur Optimierung der Abfragegeschwindigkeit. |
| **08_Migration_Vente_Declassee.sql** | Erweitert die Datenbank um die Verwaltung deklassierter oder beschädigter Produkte. |

---

# ▶️ Empfohlene Ausführungsreihenfolge

Für eine Neuinstallation sollten die SQL-Dateien in folgender Reihenfolge ausgeführt werden:

```text
01_Create_Database.sql
02_Import_CSV.sql
05_Functions.sql
06_Triggers.sql
08_Migration_Vente_Declassee.sql
04_Views.sql
07_Indexes.sql
03_SQL_Analytics.sql
```

Diese Reihenfolge stellt sicher, dass alle Abhängigkeiten korrekt erstellt werden und die Datenbank anschließend vollständig einsatzbereit ist.

---
# 🗃️ Datenmodell

Die Datenbank basiert auf einem relationalen Datenmodell.

Dabei werden die Stammdaten in Dimensionstabellen gespeichert, während die täglichen Geschäftsprozesse in Faktentabellen erfasst werden.

Durch diese Struktur bleiben die Daten übersichtlich und können später einfach für Analysen in Streamlit oder Power BI verwendet werden.

---

# 📊 Tabellenübersicht

Die Datenbank besteht aus mehreren Dimensionstabellen und Faktentabellen.

## Dimensionstabellen

Diese Tabellen enthalten hauptsächlich Stammdaten.

| Tabelle | Beschreibung |
|----------|--------------|
| **dim_date** | Kalenderdimension für Datumsanalysen |
| **dim_categories** | Verwaltung der Produktkategorien |
| **dim_produits** | Produktstammdaten |
| **dim_acheteurs** | Einkäufer |
| **dim_vendeurs** | Verkäufer |

---

## Faktentabellen

Diese Tabellen speichern die täglichen Geschäftsvorgänge.

| Tabelle | Beschreibung |
|----------|--------------|
| **fact_achats** | Einkaufsrechnungen |
| **dim_lignes_achat** | Positionen der Einkaufsrechnungen |
| **fact_ventes** | Verkaufsbelege |
| **dim_lignes_vente** | Positionen der Verkäufe |
| **fact_depenses** | Betriebsausgaben |
| **dim_pertes** | Verwaltung der Verluste |
| **fact_tresorerie** | Kassenbewegungen |
| **fact_inventaire** | Ergebnisse der Inventur |

---

# 🔄 Geschäftslogik

Die Datenbank übernimmt nicht nur die Speicherung der Daten.

Viele Berechnungen werden direkt in PostgreSQL durchgeführt.

Dadurch bleiben die Daten immer aktuell und müssen nicht jedes Mal neu berechnet werden.

Zum Beispiel:

- Lagerbestand wird automatisch aktualisiert.
- Verkaufssummen werden automatisch berechnet.
- Einkaufsbeträge werden zusammengefasst.
- Inventurdifferenzen werden berechnet.
- Kassenbewegungen werden automatisch gespeichert.

Dadurch wird auch der Python-Code einfacher und übersichtlicher.

---

# 👁️ SQL-Views

Für Streamlit und Power BI werden hauptsächlich SQL-Views verwendet.

Dadurch müssen keine komplizierten SQL-Abfragen mehrfach geschrieben werden.

Die wichtigsten Views sind:

- **vue_dashboard_global**
- **vue_ventes_detail**
- **vue_achats_detail**
- **vue_produits_stock**
- **vue_stock_alertes**
- **vue_performance_produits**
- **vue_performance_categories**
- **vue_pertes**
- **vue_inventaire**
- **vue_tresorerie**
- **vue_caisse_reelle**

Diese Views bilden die Grundlage für Berichte und Dashboards.

---

# ⚙️ SQL-Funktionen

In der Datei **05_Functions.sql** befinden sich verschiedene SQL-Funktionen.

Sie werden verwendet, um wiederkehrende Berechnungen zu vereinfachen.

Dazu gehören unter anderem:

- Berechnung des Lagerbestands
- Berechnung der Einkaufskosten
- Berechnung von Verkaufssummen
- Berechnung von Margen
- Hilfsfunktionen für Auswertungen

Dadurch bleibt der SQL-Code übersichtlich und viele Berechnungen können mehrfach verwendet werden.

---

# 🔁 SQL-Trigger

Die Trigger sorgen dafür, dass bestimmte Abläufe automatisch ausgeführt werden.

Dadurch müssen viele Berechnungen nicht manuell gestartet werden.

Beispiele:

- Lagerbestand nach einem Einkauf erhöhen
- Lagerbestand nach einem Verkauf reduzieren
- Gesamtsumme einer Rechnung aktualisieren
- Inventurdifferenzen berechnen
- Kassenbewegungen erzeugen

Durch diese Automatisierung bleiben die Daten konsistent.

---

# 🚀 Indizes

Zur Verbesserung der Performance werden mehrere Indizes erstellt.

Sie beschleunigen besonders häufig verwendete SQL-Abfragen.

Unter anderem werden Indizes erstellt für:

- Primärschlüssel
- Fremdschlüssel
- Produktcodes
- Datumsfelder
- häufig verwendete Suchspalten

Dadurch bleiben auch größere Datenmengen schnell auswertbar.

---
# 📥 CSV-Import

Die Datei **02_Import_CSV.sql** wird verwendet, um die Stammdaten und Beispieldaten in die Datenbank zu importieren.

Die CSV-Dateien befinden sich im Ordner:

```text
data/csv/
```

Vor dem Import müssen alle Tabellen bereits erstellt worden sein.

Der Import kann jederzeit erneut durchgeführt werden, wenn die Daten aktualisiert oder eine neue Testdatenbank erstellt werden soll.

---

# 📈 Verwendung mit Streamlit

Die Streamlit-Anwendung greift direkt auf die PostgreSQL-Datenbank zu.

Je nach Modul werden entweder Tabellen oder SQL-Views verwendet.

Dadurch werden die Daten immer aktuell angezeigt und Änderungen in der Datenbank sind sofort in der Anwendung sichtbar.

Zu den wichtigsten Funktionen gehören:

- Verwaltung der Produkte
- Verwaltung der Einkäufe
- Verwaltung der Verkäufe
- Lagerübersicht
- Inventur
- Verlustverwaltung
- Kassenübersicht
- Berichte und Kennzahlen

---

# 📊 Verwendung mit Power BI

Für das Power BI Dashboard werden überwiegend SQL-Views verwendet.

Dadurch bleibt das Datenmodell in Power BI übersichtlich und viele Berechnungen können bereits in PostgreSQL durchgeführt werden.

Zu den wichtigsten Auswertungen gehören:

- Umsatzentwicklung
- Verkäufe nach Zeitraum
- Produktperformance
- Lagerbestand
- Inventurdifferenzen
- Betriebsausgaben
- Verluste
- Kassenübersicht

Diese Struktur erleichtert auch zukünftige Erweiterungen des Dashboards.

---

# 💻 Installation

Nach der Installation von PostgreSQL können die SQL-Dateien nacheinander ausgeführt werden.

Beispiel mit **psql**:

```powershell
psql -U postgres -d Superette -f sql/01_Create_Database.sql

psql -U postgres -d Superette -f sql/02_Import_CSV.sql

psql -U postgres -d Superette -f sql/05_Functions.sql

psql -U postgres -d Superette -f sql/06_Triggers.sql

psql -U postgres -d Superette -f sql/08_Migration_Vente_Declassee.sql

psql -U postgres -d Superette -f sql/04_Views.sql

psql -U postgres -d Superette -f sql/07_Indexes.sql

psql -U postgres -d Superette -f sql/03_SQL_Analytics.sql
```

Nach der erfolgreichen Installation steht die Datenbank für Streamlit und Power BI zur Verfügung.

---

# 💡 Hinweise

Für dieses Projekt wurden einige Geschäftsregeln direkt in PostgreSQL umgesetzt.

Dadurch bleiben viele Berechnungen zentral in der Datenbank und müssen nicht zusätzlich in Python oder Power BI erstellt werden.

Bei Änderungen an Tabellen oder Views sollte anschließend auch das Power BI Modell aktualisiert werden.

Lokale Backups oder produktive Daten sollten nicht in dieses Repository hochgeladen werden.

---

# 🚀 Mögliche Erweiterungen

Die Datenbank kann später problemlos erweitert werden.

Zum Beispiel um:

- mehrere Filialen
- Lieferantenverwaltung
- Kundenverwaltung
- Benutzer- und Rollenverwaltung
- automatische Bestellungen
- Barcode-Unterstützung
- weitere Berichte und Kennzahlen

Durch die modulare Struktur können neue Funktionen einfach ergänzt werden.

---

# 📚 Weiterführende Dokumentation

Weitere Informationen zu diesem Projekt befinden sich in den folgenden Dokumentationen:

- **README.md** – Projektübersicht
- **streamlit/README.md** – Beschreibung der Streamlit-Anwendung
- **powerbi/README.md** – Power BI Dashboard
- **docs/** – Bilder und Projektdokumentation

---

# 👨‍💻 Autor

**Girandoux Fandio**

Dipl.-Ing. (FH) Maschinenbau

Weiterbildung:
**Daten- und Prozessanalyse mit Python (Data Science Kompakt)**

GitHub:
https://github.com/Girandoux

---

Vielen Dank für dein Interesse an diesem Projekt.

Ich freue mich über Feedback, Verbesserungsvorschläge oder einen fachlichen Austausch rund um Data Analytics, Data Engineering, PostgreSQL, Python und Power BI.