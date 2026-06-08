# HANutrition 🍎

Track your nutrition in Home Assistant!

## Features

- Macro Tracking: calories, protein, carbs, fat
- Multiple meal types: breakfast, lunch, dinner, snacks
- Built-in food database with search
- Goal progress visualization
- Weekly averages for trend tracking
- Multi-user support

## Installation

### Via HACS (recommended)

1. Open HACS in Home Assistant
2. Navigate to Integrations
3. Open the menu (⋮) and choose "Custom repositories"
4. Add `https://github.com/RTHeinemann/HANutrition` as category `Integration`
5. Search for "HANutrition"
6. Download and restart Home Assistant

### Manual

1. Copy `custom_components/hanutrition` to your HA `custom_components` folder
2. Restart Home Assistant
3. Add integration via Settings → Devices & Services

## Usage

### Log a meal

```yaml
service: hanutrition.log_meal
data:
  meal_type: breakfast
  food_name: Oatmeal with berries
  calories: 350
  protein: 12
  carbs: 60
  fat: 8
```

### Add custom food

```yaml
service: hanutrition.add_food
data:
  name: Homemade Granola
  calories: 475
  protein: 14
  carbs: 64
  fat: 20
```

### Configure goals

Create these helpers in Home Assistant:

- `input_number.protein_goal` - daily protein target (default: 200g)
- `input_number.calories_goal` - daily calorie target (default: 2500 kcal)

## Sensors

- `sensor.nutrition_daily_calories` - Today's calories
- `sensor.nutrition_daily_protein` - Today's protein
- `sensor.nutrition_daily_carbs` - Today's carbs
- `sensor.nutrition_daily_fat` - Today's fat
- `sensor.nutrition_daily_goal_progress` - Goal progress %
- `sensor.nutrition_daily_protein_pct` - Protein progress %
- `sensor.nutrition_daily_carbs_pct` - Carbs progress %
- `sensor.nutrition_daily_fat_pct` - Fat progress %
- `sensor.nutrition_weekly_avg_calories` - Weekly avg calories
- `sensor.nutrition_weekly_avg_protein` - Weekly avg protein
- `sensor.nutrition_daily_meal_count` - Today's meal count
- `sensor.nutrition_last_meal_time` - Last meal timestamp

## Services

- `hanutrition.log_meal` - Log a meal
- `hanutrition.add_food` - Add food to database
- `hanutrition.log_quick` - Quick log from food database

## License

MIT

## Author

Lucas Mueller
