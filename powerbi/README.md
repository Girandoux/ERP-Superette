# 📊 Power BI Dashboard

## Datenanalyse des Projekts „Gestion de Superette“

> [!NOTE]
> **Projektkontext**
>
> Dieses Projekt basiert auf einem realen Anwendungsfall einer kleinen Superette in Kamerun.
>
> Nach der Analyse der Geschäftsprozesse entwickelte ich eine vollständige Datenlösung bestehend aus einer PostgreSQL-Datenbank, einer Streamlit-Anwendung und interaktiven Power BI-Dashboards.
>
> Die Power BI-Dashboards greifen auf die zentrale PostgreSQL-Datenbank zu und visualisieren die im täglichen Geschäftsbetrieb erfassten Daten. Sie unterstützen die Auswertung von Einkäufen, Verkäufen, Lagerbeständen, Inventuren, Betriebsausgaben und der Kassenführung sowie die Bereitstellung wichtiger KPIs für fundierte betriebliche Entscheidungen.
>
> Ziel war es, aus den operativen Geschäftsdaten aussagekräftige Analysen und Berichte zu erstellen, die den Ladenbesitzer bei der Überwachung und Steuerung seines Unternehmens unterstützen.

---

# 📖 Inhaltsverzeichnis

- Projektübersicht
- Ziele des Dashboards
- Systemarchitektur
- Aufbau des Power BI-Ordners
- Datenquelle
- Datenmodell
- Dashboard-Seiten
- KPIs
- DAX-Measures
- Interaktive Funktionen
- Installation
- Weiterführende Dokumentation

---

# 🎯 Projektübersicht

Dieses Power BI Dashboard wurde entwickelt, um die wichtigsten Geschäftsdaten der Superette übersichtlich zu visualisieren.

Während die Streamlit-Anwendung hauptsächlich für die Verwaltung der täglichen Geschäftsprozesse genutzt wird, unterstützt Power BI die Analyse der Daten und hilft dabei, Entwicklungen und Kennzahlen schnell zu erkennen.

Die Daten stammen direkt aus der PostgreSQL-Datenbank und werden über vorbereitete SQL-Views geladen. Dadurch arbeiten Streamlit und Power BI immer mit derselben Datenbasis.

Das Dashboard unterstützt unter anderem folgende Auswertungen:

- Umsatzentwicklung
- Verkaufsanalyse
- Einkaufsanalyse
- Lagerbestand
- Inventurergebnisse
- Betriebsausgaben
- Verluste
- Kassenübersicht
- Produktperformance

---

# 🚀 Ziele des Dashboards

Bei der Entwicklung des Dashboards standen folgende Ziele im Vordergrund:

- übersichtliche Darstellung der wichtigsten Kennzahlen
- interaktive Analyse der Geschäftsdaten
- Unterstützung bei betrieblichen Entscheidungen
- direkte Anbindung an die PostgreSQL-Datenbank
- einheitliche Datenbasis für alle Berichte
- einfache Erweiterbarkeit um neue Auswertungen

Das Dashboard soll dabei helfen, Entwicklungen frühzeitig zu erkennen und die wichtigsten Informationen schnell verfügbar zu machen.

---

# 🏛️ Systemarchitektur

Das Power BI Dashboard ist Teil der gesamten ERP-Systemarchitektur und greift auf dieselbe PostgreSQL-Datenbank zu wie die Streamlit-Anwendung.

```text
              Streamlit ERP
          (Produktivbetrieb)
                   │
                   ▼
        PostgreSQL-Datenbank
                   │
        Tabellen • Views • Funktionen
                   │
                   ▼
               SQL-Views
                   │
                   ▼
               Power BI
                   │
                   ▼
      Dashboards, KPIs und Analysen
```

Die Streamlit-Anwendung dient der täglichen Erfassung und Verwaltung der Geschäftsdaten. Alle Daten werden direkt in der PostgreSQL-Datenbank gespeichert.

Für Analysen und Berichte greift Power BI hauptsächlich auf vorbereitete SQL-Views zu. Dadurch bleibt das Datenmodell übersichtlich, wiederverwendbar und performant. Berechnungen und Datenaufbereitungen werden bereits in der Datenbank durchgeführt, sodass Power BI sich auf die Visualisierung und Analyse konzentrieren kann.

---

# 📂 Aufbau des Power BI-Ordners

```text
powerbi/
│
├── Gestion_Superette.pbix
├── images/
├── docs/
└── README.md
```

Der Ordner enthält das vollständige Power BI-Projekt sowie Screenshots und ergänzende Dokumentationen.

---

# 🗄️ Datenquelle

Die Daten werden direkt aus der PostgreSQL-Datenbank geladen.

Für die meisten Berichte werden vorbereitete SQL-Views verwendet. Dadurch können komplexe SQL-Abfragen zentral verwaltet werden und müssen nicht mehrfach in Power BI erstellt werden.

Nach einer Aktualisierung des Berichts stehen alle Änderungen aus der Datenbank unmittelbar im Dashboard zur Verfügung.

---
# ⭐ Datenmodell

Für das Dashboard wurde ein übersichtliches Datenmodell erstellt.

Die Daten stammen aus der PostgreSQL-Datenbank und werden überwiegend über vorbereitete SQL-Views geladen.

Dadurch bleibt das Power BI Modell übersichtlich und viele Berechnungen können bereits in der Datenbank durchgeführt werden.

Das Datenmodell basiert auf einem Sternschema (Star Schema) mit Dimensionstabellen und Faktentabellen.

---

# 🗂️ Dimensionstabellen

Die Dimensionstabellen enthalten die Stammdaten und werden für Filter, Slicer und Beziehungen verwendet.

Die wichtigsten Dimensionstabellen sind:

| Tabelle | Beschreibung |
|----------|--------------|
| **dim_date** | Kalenderdimension für Zeitanalysen |
| **dim_produits** | Produktstammdaten |
| **dim_categories** | Produktkategorien |
| **dim_acheteurs** | Einkäufer |
| **dim_vendeurs** | Verkäufer |

Diese Tabellen ermöglichen Analysen nach Zeitraum, Produkt oder Kategorie.

---

# 📈 Faktentabellen

Die Faktentabellen enthalten die eigentlichen Geschäftsdaten.

Für das Dashboard werden hauptsächlich folgende Tabellen bzw. Views verwendet:

| Tabelle / View | Beschreibung |
|----------------|--------------|
| **fact_achats** | Einkaufsdaten |
| **fact_ventes** | Verkaufsdaten |
| **fact_depenses** | Betriebsausgaben |
| **fact_inventaire** | Inventurergebnisse |
| **fact_tresorerie** | Kassenbewegungen |
| **dim_pertes** | Verluste |
| **vue_dashboard_global** | Zusammenfassung wichtiger Kennzahlen |
| **vue_performance_produits** | Produktanalysen |
| **vue_produits_stock** | Lagerbestand |
| **vue_tresorerie** | Kassenübersicht |

---

# 📊 Dashboard-Seiten

Das Dashboard besteht aus mehreren Berichtsseiten.

Jede Seite zeigt einen bestimmten Bereich der Superette.

Die wichtigsten Seiten sind:

- Dashboard
- Verkäufe
- Einkäufe
- Lagerbestand
- Inventur
- Betriebsausgaben
- Verluste
- Kassenübersicht
- Produktanalyse

Dadurch können Informationen schnell gefunden und ausgewertet werden.

---

# 📌 Wichtige KPIs

Im Dashboard werden verschiedene Kennzahlen berechnet und visualisiert.

Zum Beispiel:

- Gesamtumsatz
- Anzahl der Verkäufe
- Anzahl der Einkäufe
- Durchschnittlicher Einkaufswert
- Durchschnittlicher Verkaufswert
- Aktueller Lagerbestand
- Lagerwert
- Inventurdifferenzen
- Betriebsausgaben
- Gesamtverluste
- Kassenbestand

Diese Kennzahlen helfen dabei, die aktuelle Situation der Superette schnell zu beurteilen.

---

# 🧮 DAX-Measures

Für verschiedene Berichte wurden DAX-Measures erstellt.

Sie dienen dazu, Kennzahlen dynamisch zu berechnen.

Beispiele sind:

- Gesamtumsatz
- Gesamtverkäufe
- Gesamteinkäufe
- Durchschnittlicher Umsatz
- Lagerwert
- Gewinn
- Anzahl der Produkte
- Anzahl der Verkäufe
- Anzahl der Einkäufe

Durch DAX können Berechnungen automatisch an die ausgewählten Filter angepasst werden.

---

# 🎛️ Interaktive Funktionen

Das Dashboard bietet verschiedene Möglichkeiten zur interaktiven Analyse.

Dazu gehören unter anderem:

- Datumsfilter
- Produktauswahl
- Kategorien
- Drill-down
- Slicer
- Sortierungen
- Kreuzfilter
- Detailansichten

Dadurch kann der Benutzer die Daten flexibel aus verschiedenen Blickwinkeln analysieren.

---

# 💡 Business Insights

Das Dashboard unterstützt dabei, wichtige Entwicklungen frühzeitig zu erkennen.

Zum Beispiel können folgende Fragen beantwortet werden:

- Welche Produkte verkaufen sich am besten?
- Welche Kategorien erzielen den höchsten Umsatz?
- Welche Produkte liegen lange im Lager?
- Wie entwickeln sich die Verkäufe im Zeitverlauf?
- Wie hoch sind die monatlichen Betriebsausgaben?
- Welche Inventurdifferenzen treten regelmäßig auf?
- Wie entwickelt sich der Kassenbestand?

Diese Auswertungen unterstützen die tägliche Planung und betriebliche Entscheidungen.

---
# 📊 Visualisierungen

Für die Berichte wurden verschiedene Visualisierungstypen verwendet.

Je nach Auswertung kommen unterschiedliche Diagramme zum Einsatz.

Unter anderem wurden folgende Visualisierungen verwendet:

- KPI-Karten
- Balkendiagramme
- Säulendiagramme
- Kreisdiagramme
- Liniendiagramme
- Tabellen
- Matrix
- Slicer
- Filter
- Karten mit Kennzahlen

Dadurch können die Daten schnell analysiert und einfach interpretiert werden.

---

# 🔄 Datenaktualisierung

Das Dashboard basiert auf den Daten der PostgreSQL-Datenbank.

Nach einer Aktualisierung des Datensatzes werden alle Berichte automatisch mit den aktuellen Daten neu berechnet.

Dadurch stehen jederzeit aktuelle Kennzahlen zur Verfügung.

---

# 💻 Installation

Zum Öffnen des Dashboards wird Microsoft Power BI Desktop benötigt.

Nach dem Öffnen der **.pbix**-Datei muss lediglich die Verbindung zur PostgreSQL-Datenbank angepasst werden.

Anschließend können die Daten aktualisiert werden.

---

# ▶️ Verwendung

Nach der Aktualisierung der Daten stehen alle Berichte sofort zur Verfügung.

Über die verschiedenen Seiten und Slicer können die Daten interaktiv analysiert werden.

Je nach Fragestellung können unterschiedliche Zeiträume, Produkte oder Kategorien ausgewählt werden.

---

# 📚 Verwendete Technologien

Für dieses Dashboard wurden folgende Technologien verwendet:

- Microsoft Power BI Desktop
- PostgreSQL
- SQL
- Power Query
- DAX
- Star Schema
- SQL Views

Diese Kombination ermöglicht eine schnelle und flexible Analyse der Geschäftsdaten.

---

# 🚀 Mögliche Erweiterungen

Das Dashboard kann später problemlos erweitert werden.

Geplant sind unter anderem:

- Prognosen für zukünftige Verkäufe
- ABC-Analyse der Produkte
- Analyse der Lagerumschlagshäufigkeit
- Saisonale Verkaufsanalysen
- Vergleich verschiedener Filialen
- Erweiterte Finanzanalysen
- Automatische Berichte

Durch die modulare Struktur können neue Seiten und Kennzahlen einfach ergänzt werden.

---

# 📚 Weiterführende Dokumentation

Weitere Informationen zu diesem Projekt befinden sich in den folgenden Dokumentationen:

- **README.md** – Projektübersicht
- **sql/README.md** – PostgreSQL-Datenbank
- **streamlit/README.md** – Streamlit-Anwendung
- **docs/** – Bilder und weitere Projektdokumentation

---

# 👨‍💻 Autor

**Girandoux Fandio**

Dipl.-Ing. (FH) Maschinenbau

Weiterbildung:

**Daten- und Prozessanalyse mit Python (Data Science Kompakt)**

GitHub:

https://github.com/Girandoux

---

# 📝 Abschluss

Dieses Dashboard ist Bestandteil des Projekts **Gestion de Superette** und ergänzt die PostgreSQL-Datenbank sowie die Streamlit-Anwendung.

Ziel war es, Geschäftsdaten übersichtlich darzustellen und wichtige Kennzahlen für die tägliche Arbeit bereitzustellen.

Während der Entwicklung wurde besonderer Wert auf eine einfache Bedienung, eine übersichtliche Darstellung und eine gute Erweiterbarkeit gelegt.

Ich freue mich über Feedback oder einen fachlichen Austausch zu den Themen Power BI, Data Analytics und Business Intelligence.