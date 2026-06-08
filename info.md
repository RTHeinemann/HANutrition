# Ha Nutrition 🍎

Track your nutrition in Home Assistant!

## Features

- **Macro Tracking**: Calories, protein, carbs, fat
- **Multiple Meal Types**: breakfast, lunch, dinner, snacks
- **Food Database**: Built-in search & add
- **Goal Progress**: Real-time progress visualization
- **Weekly Averages**: Track trends over time
- **Multi-User**: Support for family members

## Installation

### Via HACS (recommended)

1. Open HACS in Home Assistant
2. Click "Integrations"
3. Click "Explore & Add Repositories"
4. Search for "Ha Nutrition"
5. Click "Download"
6. Restart Home Assistant
7. Go to Settings → Devices & Services → Add Integration
8. Search for "Ha Nutrition" and configure

### Manual Installation

1. Copy the `custom_components/ha_nutrition` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Ha Nutrition" and configure

## Usage

### Log a Meal

```yaml
service: ha_nutrition.log_meal
data:
  meal_type: breakfast
  food_name: Hähnchenbrust mit Reis
  calories: 450
  protein: 40
  carbs: 50
  fat: 12
```

### Add a Food

```yaml
service: ha_nutrition.add_food
data:
  name: Kichererbsen
  calories: 164
  protein: 8.9
  carbs: 27
  fat: 2.6
```

### Set Goals

Create input_number helpers in Home Assistant:

- `input_number.protein_goal` (default: 200g)
- `input_number.calories_goal` (default: 2500 kcal)

## Sensors

| Sensor | Description |
|--------|-------------|
| `nutrition_daily_calories` | Today's calories |
| `nutrition_daily_protein` | Today's protein (g) |
| `nutrition_daily_carbs` | Today's carbs (g) |
| `nutrition_daily_fat` | Today's fat (g) |
| `nutrition_daily_goal_progress` | Goal progress % |
| `nutrition_daily_protein_pct` | Protein progress % |
| `nutrition_daily_carbs_pct` | Carbs progress % |
| `nutrition_daily_fat_pct` | Fat progress % |
| `nutrition_weekly_avg_calories` | Weekly avg calories |
| `nutrition_weekly_avg_protein` | Weekly avg protein |
| `nutrition_daily_meal_count` | Today's meal count |
| `nutrition_last_meal_time` | Last meal timestamp |

## License

MIT

## Author

Lucas Mueller
