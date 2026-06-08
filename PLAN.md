# HANutrition — Projektplan

## Konzept
Ernährungstagebuch mit Makro-Auswertung als Home Assistant native Integration, parallel zu HAGym.

## Name
- Repository: `RTHeinemann/HANutrition`
- Integration: `ha_nutrition`
- Entity Prefix: `nutrition_`

## Architektur-Entscheidungen
- SQLite von Anfang an (kein YAML-Migration-Pfad)
- Seed-Datenbank mit Standard-Lebensmitteln (50-100 Einträge)
- Energy-Dashboard-Stil als MVP Dashboard
- Multi-User-ready von Anfang an
- NFC/QR-Workflow vorbereitet

## Phasen

### Phase 1 — MVP (SQLite-Integration + Energy Dashboard)
**Ziel:** Essen eintragen, Makro-Summen, Energy-Dashboard, erste Analytics

- `custom_components/ha_nutrition/` — HACS-Integration
- SQLite-Backend mit Schemas für:
  - `meals` (essen getrackt)
  - `food_database` (Lebensmittel-Datenbank)
  - `user_profiles` (Multi-User)
  - `macros_daily_summary` (tägliche Aggregation)
- Services: `log_meal`, `set_daily_goal`, `set_user`, `search_food`, `add_food_to_db`
- Entities: input helpers, template sensors für Summen
- Energy-Dashboard mit Makro-Balken
- Seed-Datenbank: 50-100 Standard-Lebensmittel

### Phase 2 — Erweiterte Analytics + Custom Cards
**Ziel:** Dashboard-Deep-Dive

- Custom Cards:
  - `ha-nutrition-daily-card`
  - `ha-nutrition-macro-ring-card`
  - `ha-nutrition-trend-card`
  - `ha-nutrition-meal-log-card`
  - `ha-nutrition-balance-card`
- Weekly/Monthly/Yearly Makro-Trends
- Makro-Balance-Analyse (Protein/Kohle/Fett)
- Meal-Timing-Verteilung
- Erfahrungs-Streaks

### Phase 3 — NFC/QR + Family Features
**Ziel:** Convenience und Household

- NFC/QR für schnelle Meal-Entry in Küche
- Meal-Typ-Vorschläge via NFC
- Household-Dashboard
- Pro-Family-Member Profile + Goals
- Training load vs protein intake (HAGym-Cross-Project)
- Recovery-Analyse

## Seed-Food-Datenbank (Standard-Lebensmittel)
### Gemüse
- Brokkoli, Karotte, Zucchini, Paprika, Tomate, Gurke, Spinat, Salat, Kartoffel, Süßkartoffel, Zwiebel, Knoblauch, Gurke, Rosenkohl

### Obst
- Banane, Apfel, Orange, Erdbeere, Himbeere, Blaubeere, Kiwi, Pfirsich, Weintraube, Mango, Ananas, Melone

### Fleisch & Fisch
- Hähnchenbrust, Putenbrust, Rinderhack, Rinderfilet, Lachs, Thunfisch, Forelle, Kabeljau, Schweinefilet, Wiener Würstchen

### Milchprodukte
- Vollmilch, Magerquark, Griechischer Joghurt, Hüttenkäse, Mozzarella, Cheddar, Parmesan, Sahne, Butter, Ei (Ganzes), Eiweiß

### Getreide & Kohlenhydrate
- Reis (Basmati), Nudeln (Vollkorn), Vollkornbrot, Weizenbrot, Haferflocken, Kartoffeln, Ofenkartoffel, Kartoffeln

### Hülsenfrüchte & Nüsse
- Kichererbsen, Linsen (rot), weiße Bohnen, Kidneybohnen, Linsen, Haselnüsse, Walnüsse, Mandeln, Erdnüsse, Chiasamen, Leinsamen

### Sonstiges
- Olivenöl, Butter, Margarine, Honig, Ahornsirup, Reiswaffeln, Vollkornwaffeln, Quark (Mager), Proteinpulver

## Verzeichnisstruktur
```
HANutrition/
├── custom_components/ha_nutrition/
│   ├── __init__.py
│   ├── config_flow.py
│   ├── const.py
│   ├── coordinator.py
│   ├── entity.py
│   ├── sensors.py
│   ├── services.py
│   ├── seed_data/
│   │   └── foods.json
│   └── translations/
├── dashboards/
│   └── ha_nutrition_energy_dashboard.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── HACS_INSTALLATION.md
│   ├── DEVELOPMENT_SETUP.md
│   └── NFC_WORKFLOW.md
├── examples/
│   └── nutrition_config.yaml
├── packages/
│   └── ha_nutrition_helpers.yaml
├── .hacs.json
├── LICENSE
└── README.md
```
