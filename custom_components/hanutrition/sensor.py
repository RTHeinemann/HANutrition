"""HANutrition sensor platform."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .database import NutritionDatabase
from .const import (
    DOMAIN,
    SENSOR_PREFIX,
    SENSOR_CALORIES,
    SENSOR_PROTEIN,
    SENSOR_CARBS,
    SENSOR_FAT,
    SENSOR_GOAL_PROGRESS,
    SENSOR_PROTEIN_PCT,
    SENSOR_CARBS_PCT,
    SENSOR_FAT_PCT,
    SENSOR_MEAL_COUNT,
    SENSOR_LAST_MEAL,
    SENSOR_WEEKLY_PREFIX,
    SENSOR_WEEKLY_CALORIES,
    SENSOR_WEEKLY_PROTEIN,
    DEFAULT_CALORIE_GOAL,
    DEFAULT_PROTEIN_GOAL,
    DEFAULT_CARBS_GOAL,
    DEFAULT_FAT_GOAL,
    UNIT_CALORIES,
    UNIT_GRAM,
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HANutrition sensors from config entry."""
    db: NutritionDatabase = hass.data[DOMAIN]["database"]
    
    entities = [
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_CALORIES}",
            "Daily Calories",
            lambda: db.get_daily_totals(),
            UNIT_CALORIES,
            "mdi-restaurant",
        ),
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_PROTEIN}",
            "Daily Protein",
            lambda: db.get_daily_totals()["protein"],
            UNIT_GRAM,
            "mdi-protein",
        ),
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_CARBS}",
            "Daily Carbs",
            lambda: db.get_daily_totals()["carbs"],
            UNIT_GRAM,
            "mdi-carbs",
        ),
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_FAT}",
            "Daily Fat",
            lambda: db.get_daily_totals()["fat"],
            UNIT_GRAM,
            "mdi-fat",
        ),
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_GOAL_PROGRESS}",
            "Goal Progress",
            lambda: _get_goal_progress(db),
            "%",
            "mdi:percent",
        ),
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_PROTEIN_PCT}",
            "Protein Progress",
            lambda: _get_pct(db.get_daily_totals()["protein"], DEFAULT_PROTEIN_GOAL),
            "%",
            "mdi:percent",
        ),
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_CARBS_PCT}",
            "Carbs Progress",
            lambda: _get_pct(db.get_daily_totals()["carbs"], DEFAULT_CARBS_GOAL),
            "%",
            "mdi:percent",
        ),
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_FAT_PCT}",
            "Fat Progress",
            lambda: _get_pct(db.get_daily_totals()["fat"], DEFAULT_FAT_GOAL),
            "%",
            "mdi:percent",
        ),
        NutritionSensor(
            f"{SENSOR_PREFIX}_{SENSOR_MEAL_COUNT}",
            "Daily Meals",
            lambda: db.get_daily_meal_count(),
            "",
            "mdi:food-apple",
        ),
        NutritionSensor(
            SENSOR_LAST_MEAL,
            "Last Meal",
            lambda: db.get_last_meal_time_str(),
            "",
            "mdi:clock-outline",
            device_class="timestamp",
        ),
        NutritionSensor(
            f"{SENSOR_WEEKLY_PREFIX}_{SENSOR_WEEKLY_CALORIES}",
            "Weekly Avg Calories",
            lambda: db.get_weekly_avg_calories(),
            UNIT_CALORIES,
            "mdi:chart-line",
        ),
        NutritionSensor(
            f"{SENSOR_WEEKLY_PREFIX}_{SENSOR_WEEKLY_PROTEIN}",
            "Weekly Avg Protein",
            lambda: db.get_weekly_avg_protein(),
            UNIT_GRAM,
            "mdi:chart-line",
        ),
    ]
    
    async_add_entities(entities)


def _get_pct(value: float, goal: float) -> float:
    """Calculate percentage of goal."""
    if goal <= 0:
        return 0
    return round(min((value / goal) * 100, 999), 1)


def _get_goal_progress(db: NutritionDatabase) -> float:
    """Calculate overall goal progress."""
    totals = db.get_daily_totals()
    goals = _get_goals()
    
    # Weighted average of all progress percentages
    weights = {
        "calories": 1.0,
        "protein": 1.5,
        "carbs": 1.0,
        "fat": 1.0,
    }
    
    total_weight = sum(weights.values())
    weighted_sum = 0
    
    for metric, goal_val in goals.items():
        if goal_val > 0:
            progress = min(totals.get(metric, 0) / goal_val, 1.0) * 100
            weighted_sum += progress * weights.get(metric, 1.0)
    
    return round(weighted_sum / total_weight, 1) if total_weight > 0 else 0


def _get_goals() -> dict:
    """Get current goals from input helpers."""
    from homeassistant.helpers import input_helpers
    return {
        "calories": DEFAULT_CALORIE_GOAL,
        "protein": DEFAULT_PROTEIN_GOAL,
        "carbs": DEFAULT_CARBS_GOAL,
        "fat": DEFAULT_FAT_GOAL,
    }


class NutritionSensor(SensorEntity, RestoreEntity):
    """Representation of a HANutrition sensor."""
    
    def __init__(
        self,
        unique_id: str,
        name: str,
        value_fn,
        unit: str,
        icon: str,
        device_class: str = None,
    ):
        """Initialize the sensor."""
        self._unique_id = f"{DOMAIN}_{unique_id}"
        self._name = name
        self._value_fn = value_fn
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_name = f"HANutrition {name}"
        self._attr_native_value = None
        self._attr_extra_state_attributes = {
            "sensor_type": unique_id,
            "integration": DOMAIN,
        }
    
    @property
    def unique_id(self) -> str:
        return self._unique_id
    
    @property
    def name(self) -> str:
        return self._attr_name
    
    @property
    def native_value(self):
        return self._value_fn()
    
    @property
    def icon(self) -> str:
        return self._attr_icon
    
    @property
    def native_unit_of_measurement(self) -> str:
        return self._attr_native_unit_of_measurement
    
    @property
    def device_class(self):
        return self._attr_device_class
    
    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes
    
    async def async_added_to_hass(self) -> None:
        """Restore state when restarted."""
        await super().async_added_to_hass()
        state = await self.async_get_last_sensor_data()
        if state:
            self._attr_native_value = state.native_value
