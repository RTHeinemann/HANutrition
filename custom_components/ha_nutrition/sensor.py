"""Sensor platform for ha_nutrition."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
import logging

from .const import DOMAIN, SENSOR_DAILY_CALORIES, SENSOR_DAILY_PROTEIN
from .const import SENSOR_DAILY_CARBS, SENSOR_DAILY_FAT, SENSOR_DAILY_GOAL_PROGRESS
from .const import SENSOR_DAILY_PROTEIN_PCT, SENSOR_DAILY_CARBS_PCT, SENSOR_DAILY_FAT_PCT
from .const import SENSOR_WEEKLY_AVG_CALORIES, SENSOR_WEEKLY_AVG_PROTEIN
from .const import SENSOR_DAILY_MEAL_COUNT, SENSOR_LAST_MEAL_TIME

_LOGGER = logging.getLogger(__name__)


SENSOR_DEFINITIONS = [
    ("nutrition_daily_calories", "Tägliche Kalorien", "kcal", "calories", "mdi food-calories", "sensors.diet_daily_calories"),
    ("nutrition_daily_protein", "Tägliches Protein", "g", "protein", "mdi protein", "sensors.diet_daily_protein"),
    ("nutrition_daily_carbs", "Tägliche Kohlenhydrate", "g", "carbs", "mdi carbs", "sensors.diet_daily_carbs"),
    ("nutrition_daily_fat", "Tägliches Fett", "g", "fat", "mdi fat", "sensors.diet_daily_fat"),
    ("nutrition_daily_goal_progress", "Tägliches Ziel", "%", "progress", "mdi progress-clock", "sensors.diet_daily_goal_progress"),
    ("nutrition_daily_protein_pct", "Protein-Fortschritt", "%", "protein_pct", "mdi progress-clock", "sensors.diet_daily_protein_pct"),
    ("nutrition_daily_carbs_pct", "Kohlenhydrate-Fortschritt", "%", "carbs_pct", "mdi progress-clock", "sensors.diet_daily_carbs_pct"),
    ("nutrition_daily_fat_pct", "Fett-Fortschritt", "%", "fat_pct", "mdi progress-clock", "sensors.diet_daily_fat_pct"),
    ("nutrition_weekly_avg_calories", "Wochen-Durchschnitt Kalorien", "kcal", "weekly_avg_calories", "mdi food-calories", "sensors.diet_weekly_avg_calories"),
    ("nutrition_weekly_avg_protein", "Wochen-Durchschnitt Protein", "g", "weekly_avg_protein", "mdi protein", "sensors.diet_weekly_avg_protein"),
    ("nutrition_daily_meal_count", "Anzahl Mahlzeiten", "mahlzeiten", "meal_count", "mdi food-takeout", "sensors.diet_meal_count"),
    ("nutrition_last_meal_time", "Letzte Mahlzeit", "", "last_meal_time", "mdi clock-time-eight", "sensors.diet_last_meal_time"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from config entry."""
    sensors = []
    for sensor_def in SENSOR_DEFINITIONS:
        sensors.append(NutritionSensor(hass, sensor_def))
    async_add_entities(sensors)
    
    # Register services
    _register_services(hass)


class NutritionSensor(SensorEntity):
    """Representation of a ha_nutrition sensor."""
    
    def __init__(self, hass: HomeAssistant, sensor_def: tuple):
        """Initialize the sensor."""
        self.hass = hass
        self.entity_id = f"sensor.{sensor_def[0]}"
        self._attr_name = sensor_def[1]
        self._attr_native_unit_of_measurement = sensor_def[2]
        self._attr_icon = sensor_def[4]
        self._attr_extra_state_attributes = {}
        
        self._key = sensor_def[3]  # data key
        self._state_class = "measurement"
        
        # Use translation key if available
        self._attr_translation_key = sensor_def[5]
        
        self._sensor_def = sensor_def
    
    @property
    def should_poll(self) -> bool:
        """Poll for updates."""
        return True
    
    async def async_added_to_hass(self) -> None:
        """Set up poll timer."""
        # Poll every 15 minutes
        from homeassistant.helpers.event import async_track_time_interval
        async_track_time_interval(self.hass, self._poll, 15 * 60)
    
    @callback
    def _poll(self, now):
        """Poll for data updates."""
        self.async_schedule_update_ha_state(True)
    
    def update(self) -> None:
        """Fetch data from underlying integration."""
        db = self.hass.data[DOMAIN]["database"]
        user_id = "default"
        
        if self._key == "calories":
            data = db.get_daily_totals(user_id, _today())
            self._attr_native_value = round(data["calories"], 1)
            self._attr_extra_state_attributes = {
                "protein": round(data["protein"], 1),
                "carbs": round(data["carbs"], 1),
                "fat": round(data["fat"], 1),
                "meal_count": data["meal_count"],
            }
            
        elif self._key == "protein":
            data = db.get_daily_totals(user_id, _today())
            self._attr_native_value = round(data["protein"], 1)
            self._attr_extra_state_attributes = {
                "calories": round(data["calories"], 1),
                "carbs": round(data["carbs"], 1),
                "fat": round(data["fat"], 1),
            }
            
        elif self._key == "carbs":
            data = db.get_daily_totals(user_id, _today())
            self._attr_native_value = round(data["carbs"], 1)
            
        elif self._key == "fat":
            data = db.get_daily_totals(user_id, _today())
            self._attr_native_value = round(data["fat"], 1)
            
        elif self._key == "progress":
            data = db.get_daily_totals(user_id, _today())
            # Show percentage of protein goal as default
            self._attr_native_value = None
            
        elif self._key == "protein_pct":
            data = db.get_daily_totals(user_id, _today())
            # Will be calculated based on input helper
            
        elif self._key == "carbs_pct":
            data = db.get_daily_totals(user_id, _today())
            
        elif self._key == "fat_pct":
            data = db.get_daily_totals(user_id, _today())
            
        elif self._key == "weekly_avg_calories":
            data = db.get_weekly_average(user_id, 7)
            self._attr_native_value = data["avg_calories"]
            
        elif self._key == "weekly_avg_protein":
            data = db.get_weekly_average(user_id, 7)
            self._attr_native_value = data["avg_protein"]
            
        elif self._key == "meal_count":
            data = db.get_daily_totals(user_id, _today())
            self._attr_native_value = data["meal_count"]
            
        elif self._key == "last_meal_time":
            last = db.get_last_meal_time(user_id)
            self._attr_native_value = last[:10] if last else None


def _today() -> str:
    """Get today's date as string."""
    from datetime import date
    return date.today().isoformat()


def _register_services(hass: HomeAssistant):
    """Register custom services."""
    from .services import register_services
    register_services(hass)
