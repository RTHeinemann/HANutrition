# HANutrition - Nutrition Tracking Integration

Ein vollständiges Home Assistant Custom Component für Ernährungs-Tracking mit SQLite-Datenbank.

## 🎯 Funktionen

- **Ernährungs-Tracking**: Kalorien, Protein, Kohlenhydrate, Fett tracken
- **Lebensmittel-Datenbank**: 40+ häufige Lebensmittel vorprogrammiert
- **Schnell-Erfassung**: log_quick service für schnelles Tracken
- **Zielverfolgung**: Tägliche Ziele für Kalorien und Makros
- **Wochenstatistiken**: Durchschnittliche Werte der letzten 7 Tage
- **Benutzerfreundlich**: Persistent Notifications für Feedback

## 📁 Projektstruktur

```
ha_nutrition/
├── docs/
│   └── integration-guide.md          # Vollständige Anleitung
├── custom_components/
│   └── hanutrition/
│       ├── __init__.py               # Hauptmodul
│       ├── manifest.json             # Manifest
│       ├── const.py                  # Konstanten
│       ├── database.py               # SQLite-Datenbank mit 40+ Lebensmitteln
│       ├── sensor.py                 # 12 Sensoren
│       └── services.py              # 3 Services (log_meal, add_food, log_quick)
├── ui_templates/
│   ├── index.html                    # Haupt-Interface
│   ├── css/
│   │   ├── reset.css                 # CSS Reset
│   │   └── main.css                  # Styles
│   └── js/
│       ├── api.js                    # API-Kommunikation
│       └── app.js                    # UI-Logik
└── tests/
    └── test_hanutrition.py           # Unit-Tests (optional)
```

## 🚀 Schnellstart

1. **Component kopieren**:
   ```bash
   cp -r custom_components/hanutrition /config/custom_components/
   ```

2. **Home Assistant neustarten**

3. **Integration aktivieren** (wird automatisch gefunden)

4. **Sensoren prüfen**:
   - `sensor.nutrition_daily_calories`
   - `sensor.nutrition_daily_protein`
   - `sensor.nutrition_daily_carbs`
   - `sensor.nutrition_daily_fat`
   - `sensor.nutrition_goal_progress`
   - `sensor.nutrition_weekly_avg_calories`
   - `sensor.nutrition_weekly_avg_protein`

## 📝 Services

### `hanutrition.log_meal`
```yaml
service: hanutrition.log_meal
data:
  meal_type: lunch
  food_name: "Hähnchen mit Reis"
  calories: 500
  protein: 40
  carbs: 50
  fat: 20
  serving_g: 300
  quantity: 1
  notes: "Mittagessen Büro"
```

### `hanutrition.log_quick`
```yaml
service: hanutrition.log_quick
data:
  food_name: "apfel"  # oder "banane", "reis", "huhn", etc.
  quantity: 2
```

### `hanutrition.add_food`
```yaml
service: hanutrition.add_food
data:
  food_name: "Pizza Margherita"
  calories: 266
  protein: 11
  carbs: 33
  fat: 10
  serving_g: 100
```

## 🍽️ Lebensmittel-Datenbank (Beispiele)

| Lebensmittel | kcal/100g | Protein | Kohlenhydrate | Fett |
|-------------|-----------|---------|---------------|------|
| Apfel | 52 | 0.3g | 14g | 0.2g |
| Banane | 89 | 1.1g | 23g | 0.3g |
| Reis (gekocht) | 130 | 2.7g | 28g | 0.3g |
| Hähnchenbrust | 165 | 31g | 0g | 3.6g |
| Lachs | 208 | 20g | 0g | 13g |
| Ei | 155 | 13g | 1.1g | 11g |
| Brokkoli | 34 | 2.8g | 7g | 0.4g |
| Pizza | 266 | 11g | 33g | 10g |
| ... | ... | ... | ... | ... |

Vollständige Liste in `database.py` FOOD_DATABASE (40+ Einträge).

## 🎨 UI-Templates

Die UI-Templates im `ui_templates/` Verzeichnis können in Home Assistant als Lovelace-Widgets eingebunden werden:

```yaml
type: iframe
url: /api/lovelace/resources/hanutrition/index.html
title: HANutrition
```

## 🧪 Tests

```bash
cd tests
python3 test_hanutrition.py
```

## ⚙️ Konfiguration

Standard-Ziele (in `const.py`):
- **Kalorien**: 2500 kcal/Tag
- **Protein**: 200g/Tag
- **Kohlenhydrate**: 300g/Tag
- **Fett**: 70g/Tag

## 📊 Sensoren

| Sensor | Beschreibung | Einheit |
|--------|-------------|---------|
| nutrition_daily_calories | Tägliche Kalorien | kcal |
| nutrition_daily_protein | Tägliche Proteine | g |
| nutrition_daily_carbs | Tägliche Kohlenhydrate | g |
| nutrition_daily_fat | Tägliche Fette | g |
| nutrition_goal_progress | Fortschritt Gesamtziel | % |
| nutrition_protein_pct | Fortschritt Protein | % |
| nutrition_carbs_pct | Fortschritt Kohlenhydrate | % |
| nutrition_fat_pct | Fortschritt Fett | % |
| nutrition_meal_count | Anzahl Mahlzeiten | count |
| nutrition_last_meal | Letzte Mahlzeit | timestamp |
| nutrition_weekly_avg_calories | Wöchentlicher Durchschnitt kcal | kcal |
| nutrition_weekly_avg_protein | Wöchentlicher Durchschnitt Protein | g |

## 🔒 Sicherheit

- SQLite-Datenbank liegt lokal in `/config/hanutrition/`
- Keine externen APIs oder Cloud-Dienste
- Alle Daten bleiben im eigenen Netzwerk

## 📋 Todo / Erweiterungsmöglichkeiten

- [ ] Hinzufügen von Mahlzeiten-Zeiten (früh, mittags, abends)
- [ ] Wasser-Tracking
- [ ] Rezept-Support
- [ ] Export-Funktion (CSV, JSON)
- [ ] Automatisches Scannen von Lebensmittel-Scans
- [ ] Mehrere Benutzer
- [ ] Fitness-Tracker-Integration
- [ ] Diät-Vorlagen (z.B. Low-Carb, High-Protein)
- [ ] Lebensmittel-Barcode-Scanner
- [ ] Community-Shared-Food-Database

## 📄 Lizenz

MIT - Frei für private und kommerzielle Nutzung

## 🤝 Contributing

Fork das Repository, erstelle einen Feature-Branch, commite deine Änderungen, und erstelle einen Pull Request.

## 📧 Support

Bei Fragen oder Problemen: [GitHub Issues](https://github.com/RTHeinemann/HANutrition/issues)

---

**HANutrition** - Made for Home Assistant, by Lucas Mueller. 🍎
