"""HANutrition constants."""

DOMAIN = "hanutrition"
DB_NAME = "hanutrition.db"
DB_DIR = "hanutrition"

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack", "dessert"]

# Default goals
DEFAULT_CALORIE_GOAL = 2500
DEFAULT_PROTEIN_GOAL = 200
DEFAULT_CARBS_GOAL = 300
DEFAULT_FAT_GOAL = 70

# Unit of measurement
UNIT_CALORIES = "kcal"
UNIT_GRAM = "g"

# Entity IDs
SENSOR_PREFIX = "nutrition_daily"
SENSOR_CALORIES = "calories"
SENSOR_PROTEIN = "protein"
SENSOR_CARBS = "carbs"
SENSOR_FAT = "fat"
SENSOR_GOAL_PROGRESS = "goal_progress"
SENSOR_PROTEIN_PCT = "protein_pct"
SENSOR_CARBS_PCT = "carbs_pct"
SENSOR_FAT_PCT = "fat_pct"
SENSOR_MEAL_COUNT = "meal_count"
SENSOR_LAST_MEAL = "last_meal_time"

SENSOR_WEEKLY_PREFIX = "nutrition_weekly_avg"
SENSOR_WEEKLY_CALORIES = "calories"
SENSOR_WEEKLY_PROTEIN = "protein"
