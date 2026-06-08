"""Constants for ha_nutrition."""

DOMAIN = "ha_nutrition"

ENTITY_PREFIX = "nutrition"

# Entity IDs
ENTITY_MEAL_FOOD = "nutrition_meal_food"
ENTITY_MEAL_CALORIES = "nutrition_meal_calories"
ENTITY_MEAL_PROTEIN = "nutrition_meal_protein"
ENTITY_MEAL_CARBS = "nutrition_meal_carbs"
ENTITY_MEAL_FAT = "nutrition_meal_fat"
ENTITY_MEAL_NOTES = "nutrition_meal_notes"
ENTITY_SAVE_MEAL = "nutrition_save_meal"
ENTITY_MEAL_TYPE = "nutrition_meal_type"

# Input Helpers
INPUT_CALORIE_GOAL = "input_number.nutrition_daily_calorie_goal"
INPUT_PROTEIN_GOAL = "input_number.nutrition_daily_protein_goal"
INPUT_CARBS_GOAL = "input_number.nutrition_daily_carbs_goal"
INPUT_FAT_GOAL = "input_number.nutrition_daily_fat_goal"

# Sensors
SENSOR_DAILY_CALORIES = "sensor.nutrition_daily_calories"
SENSOR_DAILY_PROTEIN = "sensor.nutrition_daily_protein"
SENSOR_DAILY_CARBS = "sensor.nutrition_daily_carbs"
SENSOR_DAILY_FAT = "sensor.nutrition_daily_fat"
SENSOR_DAILY_GOAL_PROGRESS = "sensor.nutrition_daily_goal_progress"
SENSOR_DAILY_PROTEIN_PCT = "sensor.nutrition_daily_protein_pct"
SENSOR_DAILY_CARBS_PCT = "sensor.nutrition_daily_carbs_pct"
SENSOR_DAILY_FAT_PCT = "sensor.nutrition_daily_fat_pct"
SENSOR_WEEKLY_AVG_CALORIES = "sensor.nutrition_weekly_avg_calories"
SENSOR_WEEKLY_AVG_PROTEIN = "sensor.nutrition_weekly_avg_protein"
SENSOR_DAILY_MEAL_COUNT = "sensor.nutrition_daily_meal_count"
SENSOR_LAST_MEAL_TIME = "sensor.nutrition_last_meal_time"

# Services
SERVICE_LOG_MEAL = "log_meal"
SERVICE_SET_DAILY_GOAL = "set_daily_goal"
SERVICE_ADD_FOOD = "add_food"
SERVICE_SEARCH_FOOD = "search_food"
SERVICE_EXPORT_DATA = "export_data"
SERVICE_ADD_USER = "add_user"
SERVICE_SET_ACTIVE_USER = "set_active_user"

# Meal types
MEAL_TYPES = ["frühstück", "morgenssnack", "mittagessen", "nachmittagnsnack", "abendessen", "snack", "sonstiges"]

# Database
DB_NAME = "ha_nutrition.db"
DB_DIR = "ha_nutrition"
SCHEMA_VERSION = 1

# User
DEFAULT_USER_ID = "default"
LEGACY_USER_ID = "legacy"
