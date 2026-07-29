# ERD-Beschreibung - Gestion de Superette

## 1. Ziel des Datenmodells

Dieses Dokument beschreibt das relationale Datenmodell des Projekts **Gestion de Superette**.

Die Datenbank wurde nach einer Analyse der Geschäftsprozesse einer kleinen Superette entwickelt, um alle operativen Geschäftsabläufe in einer zentralen PostgreSQL-Datenbank abzubilden.

Sie verwaltet insbesondere folgende Bereiche:

- Produkte
- Kategorien
- Einkäufe
- Verkäufe
- Lagerbestand
- Inventur
- Verluste
- Ausgaben
- Kasse / Tresorerie
- Berichte
- Power BI Dashboards

Das Modell folgt der Logik eines einfachen ERP-Systems und basiert auf einem relationalen Datenmodell. Zur Unterstützung von Berichten und Analysen werden Tabellen nach einer Dimension-/Fakt-Struktur organisiert und durch Beziehungen miteinander verknüpft. Dadurch können sowohl der tägliche Geschäftsbetrieb als auch analytische Auswertungen in Power BI effizient unterstützt werden.

---

## 2. Allgemeine Übersicht des Modells

Das Datenmodell orientiert sich an den wichtigsten Geschäftsprozessen der Superette. Die Tabelle `dim_produits` bildet dabei die zentrale Entität und ist mit den Bereichen Einkauf, Verkauf, Inventur und Verluste verknüpft.

Die Tabelle `dim_date` ermöglicht zeitbezogene Analysen der Geschäftsprozesse. Die Faktentabellen speichern die operativen und finanziellen Geschäftsvorgänge und bilden die Grundlage für Berichte und Power BI-Dashboards.

```text
                    dim_categories
                           │
                           ▼
                    dim_produits
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
dim_lignes_achat   dim_lignes_vente      dim_pertes
        │                  │                  │
        ▼                  ▼                  ▼
 fact_achats        fact_ventes      fact_inventaire
        │                  │
        ▼                  ▼
dim_acheteurs     dim_vendeurs
        │
        ▼
      dim_date

        ▼
Lagerbestand • Berichte • Power BI
```