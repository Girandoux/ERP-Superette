# 🌐 Streamlit-Anwendung

## Benutzeroberfläche des Projekts „Gestion de Superette“

> [!NOTE]
> **Projektkontext**
>
> Dieses Projekt basiert auf einem realen Anwendungsfall einer kleinen Superette in Kamerun.
>
> Die Streamlit-Anwendung bildet die zentrale Benutzeroberfläche des Projekts und ermöglicht die Verwaltung der täglichen Geschäftsprozesse – von der Produktverwaltung über Einkauf und Verkauf bis hin zur Lagerverwaltung, Inventur und Kassenführung.
>
> Alle Daten werden direkt in einer PostgreSQL-Datenbank gespeichert und stehen anschließend für Analysen und interaktive Dashboards in Power BI zur Verfügung.
>
> Ziel war es, eine moderne, benutzerfreundliche und praxisnahe Anwendung zu entwickeln, die den Arbeitsalltag einer kleinen Superette digital unterstützt.

---

# 📖 Inhaltsverzeichnis

- Projektübersicht
- Ziele der Anwendung
- Systemarchitektur
- Aufbau des Streamlit-Ordners
- Projektstruktur
- Navigation
- Hauptmodule
- Datenfluss
- Verbindung zur Datenbank
- Installation
- Verwendete Bibliotheken
- Weiterführende Dokumentation

---

# 🎯 Projektübersicht

Diese Streamlit-Anwendung bildet die zentrale Benutzeroberfläche des Projekts.

Über die Anwendung können alle wichtigen Daten der Superette verwaltet werden.

Dazu gehören unter anderem:

- Produkte
- Kategorien
- Einkäufe
- Verkäufe
- Lagerbestand
- Inventur
- Verluste
- Betriebsausgaben
- Kassenverwaltung
- Berichte

Alle Änderungen werden direkt in der PostgreSQL-Datenbank gespeichert und stehen anschließend sofort für Auswertungen zur Verfügung.

---

# 🚀 Ziele der Anwendung

Bei der Entwicklung der Anwendung standen folgende Ziele im Vordergrund:

- einfache Bedienung
- übersichtliche Navigation
- schnelle Datenerfassung
- automatische Berechnungen
- direkte Verbindung zur PostgreSQL-Datenbank
- Unterstützung der täglichen Arbeitsabläufe
- Bereitstellung aktueller Daten für Power BI

Die Anwendung soll die tägliche Verwaltung der Superette vereinfachen und gleichzeitig eine zuverlässige Datenbasis für Analysen bereitstellen.

---

# 🏛️ Systemarchitektur

Die Streamlit-Anwendung ist ein Bestandteil der gesamten Projektarchitektur.

```text
                CSV-Dateien
                     │
                     ▼
           PostgreSQL-Datenbank
                     │
         SQL-Tabellen und Views
                     │
                     ▼
          Python / Streamlit-App
                     │
                     ▼
              Power BI Dashboard
```

Alle Daten werden zunächst in PostgreSQL gespeichert.

Die Streamlit-Anwendung liest diese Daten aus, ermöglicht deren Bearbeitung und schreibt Änderungen direkt zurück in die Datenbank.

---

# 📂 Aufbau des Streamlit-Ordners

```text
streamlit/
│
├── app.py
├── pages/
├── components/
├── utils/
├── assets/
├── config/
└── README.md
```

Die Anwendung ist modular aufgebaut.

Dadurch können neue Funktionen später einfach ergänzt werden, ohne die gesamte Anwendung ändern zu müssen.

---

# 📁 Projektstruktur

Die wichtigsten Ordner sind:

| Ordner | Beschreibung |
|---------|--------------|
| **app.py** | Startpunkt der Streamlit-Anwendung |
| **pages/** | Enthält die einzelnen Seiten der Anwendung |
| **components/** | Wiederverwendbare Benutzeroberflächen und Funktionen |
| **utils/** | Hilfsfunktionen für Datenbank, Berechnungen und Formatierungen |
| **assets/** | Bilder, Logos und weitere Ressourcen |
| **config/** | Konfigurationsdateien der Anwendung |

Diese Struktur sorgt dafür, dass der Code übersichtlich bleibt und einzelne Module unabhängig weiterentwickelt werden können.

---

# 🧭 Navigation

Die Anwendung ist in mehrere Bereiche unterteilt.

Je nach Aufgabe kann der Benutzer zwischen den verschiedenen Seiten wechseln.

Die wichtigsten Bereiche sind:

- Dashboard
- Produits
- Achats
- Ventes
- Inventaire
- Pertes
- Dépenses
- Trésorerie
- Rapports
- Administration

Dadurch sind alle Funktionen schnell erreichbar und logisch aufgebaut.

---
# 📦 Hauptmodule

Die Streamlit-Anwendung besteht aus mehreren Modulen.

Jedes Modul übernimmt einen bestimmten Geschäftsprozess der Superette.

Dadurch bleibt die Anwendung übersichtlich und kann später einfach erweitert werden.

Die wichtigsten Module sind:

| Modul | Beschreibung |
|--------|--------------|
| **Dashboard** | Zeigt die wichtigsten Kennzahlen und einen schnellen Überblick über die aktuelle Situation der Superette. |
| **Produits** | Verwaltung der Produkte und Produktinformationen. |
| **Achats** | Erfassung und Verwaltung der Einkäufe. |
| **Ventes** | Verwaltung der Verkäufe und Verkaufspositionen. |
| **Inventaire** | Durchführung der Inventur und Vergleich zwischen theoretischem und tatsächlichem Bestand. |
| **Pertes** | Verwaltung beschädigter oder verlorener Produkte. |
| **Dépenses** | Erfassung der Betriebsausgaben. |
| **Trésorerie** | Übersicht über Einnahmen und Ausgaben der Kasse. |
| **Rapports** | Anzeige verschiedener Berichte und Auswertungen. |

---

# 🔄 Datenfluss

Alle Daten werden direkt in der PostgreSQL-Datenbank gespeichert.

Die Anwendung greift über Python auf die Datenbank zu, liest die benötigten Informationen aus und schreibt Änderungen sofort zurück.

Der Datenfluss sieht vereinfacht wie folgt aus:

```text
Benutzer
    │
    ▼
Streamlit
    │
    ▼
Python
    │
    ▼
PostgreSQL
    │
    ▼
Power BI
```

Dadurch arbeiten alle Module immer mit denselben Daten.

Es gibt keine doppelte Datenspeicherung.

---

# 🗄️ Verbindung zur PostgreSQL-Datenbank

Die Verbindung zur Datenbank erfolgt über Python.

Alle SQL-Abfragen sind so aufgebaut, dass Daten sicher gelesen und gespeichert werden können.

Je nach Funktion werden verwendet:

- SQL-Abfragen
- SQL-Views
- SQL-Funktionen
- SQL-Trigger

Dadurch bleibt ein großer Teil der Geschäftslogik direkt in der Datenbank.

Die Streamlit-Anwendung konzentriert sich hauptsächlich auf die Benutzeroberfläche und die Interaktion mit dem Benutzer.

---

# 📋 Formulare und Tabellen

Für die Datenerfassung werden verschiedene Formulare verwendet.

Der Benutzer kann beispielsweise:

- neue Produkte anlegen
- Einkäufe erfassen
- Verkäufe speichern
- Inventuren durchführen
- Betriebsausgaben erfassen
- Verluste dokumentieren

Viele Eingaben werden automatisch geprüft, bevor sie gespeichert werden.

Dadurch werden fehlerhafte Eingaben reduziert.

---

# 📊 Berichte und Auswertungen

Die Anwendung stellt verschiedene Auswertungen direkt in Streamlit bereit.

Zum Beispiel:

- aktueller Lagerbestand
- Umsätze
- Einkaufsübersicht
- Betriebsausgaben
- Inventurdifferenzen
- Produktstatistiken
- Kassenübersicht

Für umfangreichere Analysen werden dieselben Daten zusätzlich in Power BI verwendet.

---

# 🎨 Benutzeroberfläche

Bei der Entwicklung der Benutzeroberfläche wurde auf eine einfache Bedienung geachtet.

Die wichtigsten Funktionen sind über das Navigationsmenü schnell erreichbar.

Tabellen, Formulare und Diagramme sind übersichtlich aufgebaut und ermöglichen eine schnelle Datenerfassung.

Die Anwendung kann sowohl auf einem Desktop-PC als auch auf einem Notebook genutzt werden.

---

# 🔒 Datenqualität

Eine gute Datenqualität war bei der Entwicklung besonders wichtig.

Deshalb werden verschiedene Prüfungen bereits während der Dateneingabe durchgeführt.

Beispiele:

- Pflichtfelder werden geprüft.
- Ungültige Eingaben werden verhindert.
- Berechnungen erfolgen automatisch.
- Lagerbestände werden aktualisiert.
- Summen werden automatisch berechnet.

Dadurch bleiben die gespeicherten Daten konsistent und zuverlässig.

---
# 💻 Installation

## Voraussetzungen

Für die Ausführung der Anwendung werden folgende Programme benötigt:

- Python 3.11 oder neuer
- PostgreSQL
- Git
- Streamlit

Zusätzlich sollten alle benötigten Python-Bibliotheken installiert sein.

---

## Projekt herunterladen

Repository klonen:

```bash
git clone https://github.com/Girandoux/Gestion_Superette.git

cd Gestion_Superette
```

---

## Benötigte Bibliotheken installieren

```bash
pip install -r requirements.txt
```

---

## PostgreSQL vorbereiten

Vor dem Start der Anwendung muss die PostgreSQL-Datenbank erstellt werden.

Dazu werden die SQL-Dateien im Ordner **sql/** in der empfohlenen Reihenfolge ausgeführt.

Weitere Informationen dazu befinden sich in der Datei:

```text
sql/README.md
```

---

## Anwendung starten

Nach der Installation kann die Anwendung mit folgendem Befehl gestartet werden:

```bash
streamlit run app.py
```

Anschließend öffnet sich die Anwendung automatisch im Browser.

Standardmäßig ist sie unter folgender Adresse erreichbar:

```text
http://localhost:8501
```

---

# 📚 Verwendete Bibliotheken

Für die Entwicklung wurden unter anderem folgende Bibliotheken verwendet:

- Streamlit
- Pandas
- NumPy
- SQLAlchemy
- Psycopg2
- Plotly
- OpenPyXL

Je nach Modul kommen weitere Bibliotheken hinzu.

Alle Abhängigkeiten sind in der Datei **requirements.txt** aufgeführt.

---

# 🔒 Datenintegrität

Ein wichtiger Schwerpunkt dieses Projekts ist die Sicherstellung einer hohen Datenqualität.

Dafür werden mehrere Mechanismen eingesetzt:

- Eingabeprüfungen in der Benutzeroberfläche
- Validierungen in Python
- Fremdschlüssel in PostgreSQL
- SQL-Trigger
- SQL-Funktionen
- automatische Berechnungen

Dadurch bleiben die Daten konsistent und fehlerhafte Eingaben werden weitgehend vermieden.

---

# 🚀 Mögliche Erweiterungen

Die Anwendung wurde bewusst modular aufgebaut und kann später problemlos erweitert werden.

Geplante Erweiterungen sind zum Beispiel:

- Mehrbenutzerverwaltung
- Rollen- und Rechteverwaltung
- Lieferantenverwaltung
- Kundenverwaltung
- Barcode-Scanner
- Automatische Bestellvorschläge
- E-Mail-Benachrichtigungen
- Erweiterte Berichte
- Mobile Optimierung

---

# 📚 Weiterführende Dokumentation

Weitere Informationen zu den einzelnen Projektbereichen befinden sich in den folgenden Dokumentationen:

- **README.md** – Projektübersicht
- **sql/README.md** – PostgreSQL-Datenbank
- **powerbi/README.md** – Power BI Dashboard
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

Dieses Projekt wurde entwickelt, um die Geschäftsprozesse einer kleinen Superette digital abzubilden und gleichzeitig eine zuverlässige Datenbasis für Analysen bereitzustellen.

Es verbindet PostgreSQL, Python, Streamlit und Power BI zu einer vollständigen Lösung für Datenerfassung, Verwaltung und Auswertung.

Während der Entwicklung standen eine übersichtliche Benutzeroberfläche, eine saubere Datenstruktur und eine einfache Erweiterbarkeit im Mittelpunkt.

Ich wünsche dir viel Freude beim Anschauen des Projekts und freue mich über Feedback oder einen fachlichen Austausch.