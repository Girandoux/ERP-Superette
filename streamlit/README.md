# 🚀 Streamlit ERP-Anwendung

## Ziel

Der Ordner **`streamlit/`** enthält die Benutzeroberfläche des Projekts **ERP Superette**.

Die Streamlit-Anwendung bildet den operativen Teil des Systems und ermöglicht die tägliche Verwaltung einer Superette.

Über die Anwendung können Produkte, Kategorien, Einkäufe, Verkäufe, Lagerbestände, Inventuren, Verluste, Ausgaben und Kassenbewegungen verwaltet werden.

Alle Daten werden direkt in der PostgreSQL-Datenbank gespeichert und stehen anschließend sowohl der Anwendung als auch dem Power-BI-Dashboard zur Verfügung.

---

# Projektstruktur

```text
streamlit/
│
├── README.md
│
├── pages/
│   ├── 01_Accueil.py
│   ├── 02_Produits.py
│   ├── 03_Categories.py
│   ├── 04_Achats.py
│   ├── 05_Lignes_Achat.py
│   ├── 06_Ventes.py
│   ├── 07_Lignes_Vente.py
│   ├── 08_Depenses.py
│   ├── 09_Pertes.py
│   ├── 10_Tresorerie.py
│   ├── 11_Inventaire.py
│   ├── 12_Rapports.py
│   ├── 13_Dashboard.py
│   ├── 14_Administration.py
│   └── 15_A_Propos.py
│
└── ui_state.json (lokal)
```

---

# Anwendung starten

Die Anwendung kann mit folgendem Befehl gestartet werden.

```powershell
streamlit run app.py
```

Nach dem Start öffnet sich die Anwendung automatisch im Webbrowser.

---

# Systemarchitektur

Die Streamlit-Anwendung kommuniziert direkt mit der PostgreSQL-Datenbank.

```text
Benutzer
      │
      ▼
Streamlit ERP
      │
      ▼
Python-Module
(database/ & utils/)
      │
      ▼
PostgreSQL
(Zentrale Datenbasis)
      │
      └────────────► Power BI
```

---

# Navigation

Alle Seiten befinden sich im Ordner

```text
streamlit/pages/
```

Die Navigation wird zentral in **app.py** verwaltet.

---

# Seitenübersicht

| Seite | Beschreibung |
|--------|--------------|
| `01_Accueil.py` | Startseite mit KPIs und Schnellübersicht |
| `02_Produits.py` | Verwaltung der Produkte |
| `03_Categories.py` | Verwaltung der Kategorien |
| `04_Achats.py` | Verwaltung der Einkäufe |
| `05_Lignes_Achat.py` | Verwaltung der Einkaufspositionen |
| `06_Ventes.py` | Verwaltung der Verkäufe |
| `07_Lignes_Vente.py` | Verwaltung der Verkaufspositionen |
| `08_Depenses.py` | Verwaltung der Ausgaben |
| `09_Pertes.py` | Erfassung von Verlusten |
| `10_Tresorerie.py` | Verwaltung der Kassenbewegungen |
| `11_Inventaire.py` | Inventur und Lagerkontrolle |
| `12_Rapports.py` | Berichte und Datenexport |
| `13_Dashboard.py` | Internes Dashboard |
| `14_Administration.py` | Administration und Datenimport |
| `15_A_Propos.py` | Projektinformationen |

---

# Screenshots

## Startseite

![Accueil](../images/streamlit/streamlit_accueil.png)

---

## Produkte

![Produits](../images/streamlit/streamlit_produits.png)

---

## Kategorien

![Categories](../images/streamlit/streamlit_categories.png)

---

## Einkäufe

![Achats](../images/streamlit/streamlit_achats.png)

---

## Einkaufspositionen

![Lignes Achat](../images/streamlit/streamlit_ligne_achat.png)

---

## Verkäufe

![Ventes](../images/streamlit/streamlit_ventes.png)

---

## Verkaufspositionen

![Lignes Vente](../images/streamlit/streamlit_lignes_vente.png)

---

## Ausgaben

![Depenses](../images/streamlit/streamlit_depenses.png)

---

## Verluste

![Pertes](../images/streamlit/streamlit_perte.png)

---

## Kassenverwaltung

![Tresorerie](../images/streamlit/streamlit_tresorie.png)

---

## Inventur

![Inventaire](../images/streamlit/streamlit_inventaire.png)

---

## Berichte

![Rapports](../images/streamlit/streamlit_raport.png)

---

## Dashboard

![Dashboard](../images/streamlit/streamlit_dashboard.png)

---

## Administration

![Administration](../images/streamlit/streamlit_administration.png)

---

## Projektinformationen

![A propos](../images/streamlit/streamlit_a_propos.png)

---

# Hauptfunktionen

Die Anwendung bietet unter anderem folgende Funktionen.

## Produktverwaltung

- Produkte anlegen
- Produkte bearbeiten
- Produkte deaktivieren
- Automatische Produktcodes
- Verwaltung des Mindestbestands

---

## Einkaufsverwaltung

- Einkaufsrechnungen erstellen
- Automatische Rechnungsnummern
- Einkaufspositionen verwalten
- Automatische Preisberechnung
- Berechnung der Einkaufssumme

---

## Verkaufsverwaltung

- Verkäufe erfassen
- Verkaufspositionen verwalten
- Produktsuche
- Automatische Preisvorschläge
- Lagerbestandsprüfung
- Warnung bei negativer Marge

---

## Inventur

- Inventuren durchführen
- Lagerbestände vergleichen
- Inventurdifferenzen berechnen
- Lagerbestand synchronisieren

---

## Berichte

- Excel-Export
- CSV-Export
- PDF-Export
- Individuelle Filter
- Zusammenfassungen nach Produkt oder Kategorie

---

# Datenvalidierung

Die Anwendung überprüft unter anderem:

- Pflichtfelder
- Zahlenformate
- Lagerbestand
- Negative Margen
- Doppelte Produkte
- Fehlende Produktauswahl
- Inventurdifferenzen

Dadurch wird eine hohe Datenqualität sichergestellt.

---

# Benutzeroberfläche

Das Design wurde für eine einfache und übersichtliche Bedienung entwickelt.

Merkmale:

- moderne KPI-Karten
- einheitliches Farbschema
- übersichtliche Formulare
- responsive Tabellen
- kompakte Navigation
- konsistente Informationsboxen

---

# Wichtige Dateien

```text
app.py

config/
├── database.py
├── settings.py
└── styles.py

database/
utils/
streamlit/pages/
```

Diese Dateien enthalten die Konfiguration, Datenbankanbindung, Geschäftslogik und Benutzeroberfläche der Anwendung.

---
# Datenfluss

Die Streamlit-Anwendung ist Bestandteil des gesamten ERP-Superette-Systems und arbeitet direkt mit der zentralen PostgreSQL-Datenbank.

Die Daten werden im Projekt nach folgendem Prozess verarbeitet:

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

## Prozessbeschreibung

1. Die Stammdaten und Geschäftsdaten werden einmalig aus **Excel- und CSV-Dateien** übernommen.
2. Der **Python-ETL-Prozess** importiert, bereinigt und validiert die Daten.
3. Alle Daten werden zentral in der **PostgreSQL-Datenbank** gespeichert.
4. Die **Streamlit-ERP-Anwendung** liest Daten aus der Datenbank und speichert neue oder geänderte Informationen direkt zurück.
5. **Power BI** greift ausschließlich lesend auf dieselbe Datenbank zu und erstellt Dashboards sowie Berichte.
6. Die Benutzer arbeiten ausschließlich über die Streamlit-ERP-Anwendung.
---

# Verwandte Ordner

```text
database/
sql/
data/
powerbi/
images/
docs/
config/
utils/
```

Diese Ordner bilden gemeinsam die technische Grundlage des ERP-Systems.

---

# Hinweise

Die Datei **`ui_state.json`** dient ausschließlich zur lokalen Speicherung von Benutzereinstellungen und zuletzt verwendeten Eingaben.

Sie wird nicht in das öffentliche GitHub-Repository aufgenommen.

---

# Lizenz

Dieser Ordner ist Bestandteil des Projekts **ERP Superette**.

© 2026 Girandoux Fandio Nganwajop