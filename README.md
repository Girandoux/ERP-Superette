# 🛒 Gestion de Superette

## Datenanalyse- und Verwaltungssystem für eine kleine Superette

> [!NOTE]
> **Projektkontext**
>
> Dieses Projekt basiert auf einem realen Anwendungsfall einer kleinen Superette in Kamerun.
>
> Nach einer Analyse der Geschäftsprozesse entwickelte ich eine vollständige Datenlösung bestehend aus einer PostgreSQL-Datenbank, einer ERP-Anwendung mit Python und Streamlit sowie interaktiven Power BI-Dashboards.
>
> Ziel war es, die täglichen Geschäftsprozesse – darunter Einkauf, Verkauf, Lagerverwaltung, Inventur, Betriebsausgaben und Kassenführung – zu digitalisieren, zentral zu verwalten und durch aussagekräftige Analysen sowie KPIs fundierte betriebliche Entscheidungen zu unterstützen.
---

## 📖 Projektübersicht

**Gestion de Superette** ist eine vollständige Datenanwendung zur Verwaltung einer kleinen Superette.

Das Projekt verbindet **PostgreSQL**, **Python**, **Streamlit** und **Power BI** zu einer gemeinsamen Lösung.

Mit der Anwendung können unter anderem folgende Geschäftsprozesse verwaltet werden:

- 📦 Produkte
- 🛍️ Einkäufe
- 💰 Verkäufe
- 📊 Lagerbestand
- 📋 Inventur
- 📉 Verluste
- 💳 Betriebsausgaben
- 💵 Kassenverwaltung
- 📈 Berichte und Dashboards

Alle Daten werden zentral in PostgreSQL gespeichert und anschließend in Streamlit und Power BI genutzt.

---

## 🚀 Projektziele

Bei der Entwicklung des ERP-Systems standen folgende Ziele im Vordergrund:

- Analyse und Digitalisierung der Geschäftsprozesse einer kleinen Superette
- Entwicklung eines flexiblen und erweiterbaren ERP-Systems für den täglichen Geschäftsbetrieb
- Entwurf eines relationalen Datenmodells (ERD) als Grundlage der PostgreSQL-Datenbank
- Zentrale und konsistente Verwaltung aller Geschäftsdaten in einer gemeinsamen Datenbank
- Einmalige Migration bestehender Excel- und CSV-Daten in das neue System
- Entwicklung einer benutzerfreundlichen Streamlit-Anwendung für die tägliche Datenerfassung
- Bereitstellung aktueller Kennzahlen und Managementberichte mit Power BI
- Modulare Softwarearchitektur für eine einfache Wartung und kontinuierliche Erweiterung entsprechend den Anforderungen des Ladenbesitzers

---

## 🏗️ Projektarchitektur

```text
        Anforderungen des Ladenbesitzers
                      │
                      ▼
             Geschäftsprozessanalyse
                      │
                      ▼
          ERD und relationales Datenmodell
                selbst entwickelt
                      │
                      ▼
             PostgreSQL-Datenbank
                selbst aufgebaut
                      │
       ┌──────────────┴──────────────┐
       │                             │
       ▼                             ▼
Einmaliger Datenimport        Streamlit-Anwendung
  aus Excel / CSV             für den täglichen Betrieb
       │                             │
       └──────────────┬──────────────┘
                      ▼
             Python-Anwendungslogik
        database/ + utils/ + SQLAlchemy
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       Reports              Power BI
                                  │
                                  ▼
                    Analyse und Management-KPIs
```

---

## 🛠️ Verwendete Technologien

| Bereich | Technologien |
|----------|--------------|
| Programmiersprache | Python |
| Datenbank | PostgreSQL |
| SQL | PostgreSQL SQL |
| Benutzeroberfläche | Streamlit |
| Business Intelligence | Power BI |
| Datenverarbeitung | Pandas, NumPy |
| Datenbankzugriff | SQLAlchemy, Psycopg2 |
| Visualisierung | Plotly |
| Versionsverwaltung | Git & GitHub |

---

## ⭐ Projekt-Highlights

✔ Analyse der Geschäftsprozesse und Entwicklung der Systemanforderungen

✔ Entwurf des Entity-Relationship-Diagramms (ERD) und des relationalen Datenmodells

✔ Entwicklung einer vollständigen PostgreSQL-Datenbank mit Tabellen, Beziehungen, Views, Triggern, Funktionen und Indizes

✔ Entwicklung einer modularen ERP-Anwendung mit Python, SQLAlchemy und Streamlit

✔ Implementierung eines ETL-Prozesses zur Migration bestehender Excel- und CSV-Daten

✔ Digitalisierung der täglichen Geschäftsprozesse (Einkauf, Verkauf, Lager, Inventur, Ausgaben und Kassenführung)

✔ Entwicklung interaktiver Power BI-Dashboards für Analysen und Management-KPIs

✔ Kontinuierliche Weiterentwicklung des Systems entsprechend den Anforderungen des Ladenbesitzers
---
## 📂 Projektstruktur

```text
Gestion_Superette/
│
├── data/                 # CSV-Dateien
├── database/             # PostgreSQL-Datenbank
├── sql/                  # SQL-Skripte
├── streamlit/            # Streamlit-Anwendung
├── powerbi/              # Power BI Dashboard
├── images/               # Screenshots
├── docs/                 # Projektdokumentation
├── requirements.txt
├── LICENSE
└── README.md
```

---

# ⚙️ Hauptfunktionen

Die Anwendung unterstützt die wichtigsten Geschäftsprozesse einer kleinen Superette.

### 📦 Produktverwaltung

- Produkte anlegen und bearbeiten
- Produktkategorien verwalten
- Lagerbestand überwachen

### 🛒 Einkaufsverwaltung

- Einkäufe erfassen
- Einkaufspositionen verwalten
- Einkaufskosten berechnen

### 💰 Verkaufsverwaltung

- Verkäufe erfassen
- Verkaufspositionen verwalten
- Umsatz berechnen

### 📋 Inventur

- Theoretischen und tatsächlichen Bestand vergleichen
- Inventurdifferenzen berechnen
- Lagerkorrekturen dokumentieren

### 📉 Verlustverwaltung

- Beschädigte oder verlorene Produkte erfassen
- Ursachen dokumentieren
- Auswirkungen auf den Lagerbestand verfolgen

### 💳 Betriebsausgaben

- Betriebsausgaben verwalten
- Auswertungen nach Kategorien erstellen

### 📊 Dashboard und Berichte

- Interaktive Dashboards
- Verkaufsanalysen
- Einkaufsanalysen
- Lageranalysen
- Finanzübersichten

---

# 🖼️ Screenshots

Einige Ansichten der Anwendung.

## Streamlit

![Dashboard](images/streamlit/streamlit_accueil.png)

## Power BI

![Power BI Dashboard](images/powerbi/dashboard_overview.png)

> Die verwendeten Bilder dienen als Beispiele. Weitere Screenshots befinden sich im Ordner **images/**.

---
# 🔄 Datenfluss

Die PostgreSQL-Datenbank bildet die zentrale Datenbasis des ERP-Systems.

Zu Beginn wurden vorhandene Geschäftsdaten einmalig aus Excel- und CSV-Dateien in die Datenbank übernommen. Im täglichen Betrieb werden alle neuen Daten direkt über die Streamlit-Anwendung erfasst und in der Datenbank gespeichert. Power BI greift auf dieselbe Datenbasis zu und erstellt aktuelle Analysen und Berichte.

```text
            Einmaliger Import
           Excel- / CSV-Dateien
                    │
                    ▼
        PostgreSQL-Datenbank
                    ▲
                    │
      Streamlit-Anwendung (ERP)
      Produktivbetrieb
      • Produkte
      • Einkäufe
      • Verkäufe
      • Inventur
      • Ausgaben
      • Kassenführung
                    │
                    ▼
      Reports & Power BI Dashboards
```

Dadurch arbeiten alle Komponenten mit derselben zentralen Datenbasis. Änderungen, die in der Streamlit-Anwendung vorgenommen werden, stehen unmittelbar für Berichte, Auswertungen und Power BI-Dashboards zur Verfügung.
---

# 📚 Dokumentation

Weitere Informationen zu den einzelnen Projektbereichen befinden sich in den folgenden Dokumentationen.

| Dokument | Inhalt |
|----------|--------|
| **sql/README.md** | PostgreSQL-Datenbank, Tabellen, Views, Trigger und Funktionen |
| **streamlit/README.md** | Aufbau und Funktionen der Streamlit-Anwendung |
| **powerbi/README.md** | Dashboard, Datenmodell, KPIs und DAX-Measures |

---
# 🚀 Installation

## Projekt herunterladen

```bash
git clone https://github.com/Girandoux/Gestion_Superette.git

cd Gestion_Superette
```

---

## Python-Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

---

## PostgreSQL-Datenbank einrichten

Vor dem Start der Anwendung muss die PostgreSQL-Datenbank erstellt werden.

Alle benötigten SQL-Skripte befinden sich im Ordner:

```text
sql/
```

Eine ausführliche Beschreibung der Datenbankinstallation befindet sich in:

```text
sql/README.md
```

---

## Streamlit starten

Nach der Installation kann die Anwendung mit folgendem Befehl gestartet werden:

```bash
streamlit run app.py
```

Standardmäßig öffnet sich die Anwendung unter:

```text
http://localhost:8501
```

---

# 📌 Projektstatus

Dieses Projekt wird kontinuierlich weiterentwickelt.

Geplante Erweiterungen sind unter anderem:

- Benutzer- und Rollenverwaltung
- Lieferantenverwaltung
- Kundenverwaltung
- Barcode-Unterstützung
- Erweiterte Power BI Dashboards
- Weitere Berichte und KPIs
- Optimierung der Benutzeroberfläche

---

# 🎓 Was ich mit diesem Projekt umgesetzt habe

Mit diesem Projekt konnte ich praktische Erfahrungen in verschiedenen Bereichen der Datenanalyse und des Data Engineerings sammeln.

Dabei kamen unter anderem folgende Technologien und Konzepte zum Einsatz:

- PostgreSQL
- SQL
- Python
- Streamlit
- Power BI
- SQLAlchemy
- Pandas
- Datenmodellierung
- ETL-Prozesse
- Star Schema
- Datenvisualisierung
- Dashboard-Entwicklung
- Git und GitHub

---

# 📚 Dokumentation

Weitere Informationen zu den einzelnen Projektbereichen befinden sich in den jeweiligen Unterordnern.

| Dokument | Beschreibung |
|----------|--------------|
| **sql/README.md** | PostgreSQL-Datenbank, Tabellen, Views, Trigger und SQL-Funktionen |
| **streamlit/README.md** | Aufbau und Funktionen der Streamlit-Anwendung |
| **powerbi/README.md** | Datenmodell, KPIs, DAX-Measures und Dashboard |

---

# 👨‍💻 Autor

**Girandoux Fandio**

Dipl.-Ing. (FH) Maschinenbau

Weiterbildung:

**Daten- und Prozessanalyse mit Python (Data Science Kompakt)**

📍 Wolfsburg, Deutschland

🔗 GitHub

https://github.com/Girandoux

---

# ⭐ Feedback

Vielen Dank für dein Interesse an diesem Projekt.

Ich freue mich über Feedback, Verbesserungsvorschläge oder einen fachlichen Austausch zu den Themen:

- Data Analytics
- Data Engineering
- PostgreSQL
- Python
- Streamlit
- Power BI
- Business Intelligence

Wenn dir das Projekt gefällt, freue ich mich über einen ⭐ auf GitHub.