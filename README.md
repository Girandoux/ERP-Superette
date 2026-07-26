# 🛒 Gestion de Superette

## Datenanalyse- und Verwaltungssystem für eine kleine Superette

> [!NOTE]
> **Projektkontext**
>
> Dieses Projekt basiert auf einem realen Anwendungsfall einer kleinen Superette in Kamerun.
>
> Ziel war es, eine vollständige Datenlösung mit PostgreSQL, Python, Streamlit und Power BI zu entwickeln, um die täglichen Geschäftsprozesse digital zu verwalten und gleichzeitig aussagekräftige Analysen bereitzustellen.

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

Bei der Entwicklung standen folgende Ziele im Vordergrund:

- Digitalisierung der täglichen Geschäftsprozesse
- Zentrale Verwaltung aller Geschäftsdaten
- Hohe Datenqualität durch relationale Datenbank
- Benutzerfreundliche Oberfläche mit Streamlit
- Interaktive Dashboards mit Power BI
- Einfache Erweiterbarkeit des Projekts

---

## 🏗️ Projektarchitektur

```text
                 CSV-Dateien
                      │
                      ▼
             PostgreSQL-Datenbank
                      │
        ┌─────────────┼─────────────┐
        ▼                           ▼
   Python / Streamlit         Power BI
        │                           │
        └─────────────┬─────────────┘
                      ▼
          Verwaltung & Datenanalyse
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

✔ Entwicklung einer relationalen PostgreSQL-Datenbank

✔ Erstellung einer modularen Streamlit-Anwendung

✔ Entwicklung interaktiver Power BI Dashboards

✔ Automatisierung von Geschäftsprozessen mit SQL-Triggern und SQL-Funktionen

✔ Verwendung eines Star-Schema-Datenmodells für Analysen

✔ Verbindung von Datenbank, Anwendung und Dashboard in einer gemeinsamen Lösung

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

![Dashboard](images/streamlit_dashboard.png)

## Power BI

![Power BI Dashboard](images/powerbi_dashboard.png)

> Die verwendeten Bilder dienen als Beispiele. Weitere Screenshots befinden sich im Ordner **images/**.

---

# 🔄 Datenfluss

Die Anwendung arbeitet mit einer zentralen PostgreSQL-Datenbank.

```text
CSV-Dateien
      │
      ▼
PostgreSQL
      │
      ├────────► Streamlit
      │
      └────────► Power BI
```

Dadurch greifen alle Anwendungen auf dieselben Daten zu und es entsteht eine einheitliche Datenbasis.

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