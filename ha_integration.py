"""HA Integration für ha_nutrition - Entity-ID Mapping und Helfer"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

# Mapping: entity_id → Sensor-Name
SENSOR_ENTITY_IDS = [
    "sensor.nutrition_daily_calories",
    "sensor.nutrition_daily_protein",
    "sensor.nutrition_daily_carbs",
    "sensor.nutrition_daily_fat",
    "sensor.nutrition_daily_goal_progress",
    "sensor.nutrition_daily_protein_pct",
    "sensor.nutrition_daily_carbs_pct",
    "sensor.nutrition_daily_fat_pct",
    "sensor.nutrition_weekly_avg_calories",
    "sensor.nutrition_weekly_avg_protein",
    "sensor.nutrition_daily_meal_count",
    "sensor.nutrition_last_meal_time",
]

# Mapping: entity_id → Ziel-Helfer
HELPER_MAPPING = {
    "sensor.nutrition_daily_protein": {
        "type": "input_number",
        "key": "protein_goal",
        "description": "Tägliches Protein-Ziel in Gramm",
        "min": 0,
        "max": 500,
        "step": 1,
        "unit": "g",
        "initial": 200,
    },
    "sensor.nutrition_daily_calories": {
        "type": "input_number",
        "key": "calories_goal",
        "description": "Tägliches Kalorien-Ziel",
        "min": 0,
        "max": 10000,
        "step": 1,
        "unit": "kcal",
        "initial": 2500,
    },
}

# Helper-Konfiguration für HA
HELPER_CONFIG = {
    "input_number": [
        {
            "name": "Tägliches Protein-Ziel",
            "key": "protein_goal",
            "min": 0,
            "max": 500,
            "step": 1,
            "unit_of_measurement": "g",
            "initial": 200,
        },
        {
            "name": "Tägliches Kalorien-Ziel",
            "key": "calories_goal",
            "min": 0,
            "max": 10000,
            "step": 1,
            "unit_of_measurement": "kcal",
            "initial": 2500,
        },
    ]
}

class HAIntegration:
    """Integration mit Home Assistant"""
    
    def __init__(self, ha_proxy):
        """
        Args:
            ha_proxy: Zugriff auf HA-Dienste (state management, helpers)
        """
        self.ha = ha_proxy
        self.sensor_ids = SENSOR_ENTITY_IDS
        self.helper_config = HELPER_CONFIG
    
    async def create_helpers(self) -> List[str]:
        """Erstelle input_number-Helfer in HA."""
        created = []
        for helper in self.helper_config["input_number"]:
            key = helper["key"]
            
            # Prüfe ob Helper existiert
            entity_id = f"input_number.{key}"
            state = self.ha.get_state(entity_id)
            
            if state is None:
                # Erstelle Helper
                success = await self.ha.create_helper(
                    type="input_number",
                    name=helper["name"],
                    key=key,
                    min=helper["min"],
                    max=helper["max"],
                    step=helper["step"],
                    unit=helper["unit_of_measurement"],
                    initial=helper["initial"],
                )
                if success:
                    created.append(entity_id)
                    _LOGGER.info("Created helper: %s", entity_id)
                else:
                    _LOGGER.warning("Failed to create helper: %s", entity_id)
            else:
                created.append(entity_id)
                _LOGGER.info("Helper already exists: %s", entity_id)
        
        return created
    
    async def get_helper_value(self, key: str) -> Optional[float]:
        """Wert eines Helpers auslesen."""
        entity_id = f"input_number.{key}"
        state = self.ha.get_state(entity_id)
        
        if state is not None:
            return float(state)
        return None
    
    async def set_helper_value(self, key: str, value: float):
        """Wert eines Helpers setzen."""
        entity_id = f"input_number.{key}"
        await self.ha.set_state(entity_id, value)
        _LOGGER.info("Set helper %s to %s", entity_id, value)
    
    def get_sensor_entity_id(self, sensor_name: str) -> str:
        """Entity-ID für Sensor-Name."""
        for entity_id in self.sensor_ids:
            if sensor_name in entity_id:
                return entity_id
        return None
    
    async def get_sensor_state(self, sensor_name: str) -> Optional[float]:
        """Sensor-Wert auslesen."""
        entity_id = self.get_sensor_entity_id(sensor_name)
        if entity_id is None:
            return None
        
        state = self.ha.get_state(entity_id)
        if state is not None:
            return float(state)
        return None
    
    async def get_all_sensor_states(self) -> Dict[str, Optional[float]]:
        """Alle Sensor-Werte auslesen."""
        states = {}
        for entity_id in self.sensor_ids:
            state = self.ha.get_state(entity_id)
            key = entity_id.split(".")[1]
            states[key] = float(state) if state is not None else None
        return states
    
    async def calculate_goal_progress(self) -> Dict[str, float]:
        """Berechne Fortschritt basierend auf Helfern."""
        protein_goal = await self.get_helper_value("protein_goal")
        calories_goal = await self.get_helper_value("calories_goal")
        
        protein_current = await self.get_sensor_state("protein")
        calories_current = await self.get_sensor_state("calories")
        
        progress = {}
        
        if protein_goal and protein_current:
            progress["protein_pct"] = min(100, (protein_current / protein_goal) * 100)
        
        if calories_goal and calories_current:
            progress["calories_pct"] = min(100, (calories_current / calories_goal) * 100)
        
        return progress
    
    async def get_all_states(self) -> Dict:
        """Alle relevanten Zustände ausgeben."""
        states = await self.get_all_sensor_states()
        progress = await self.calculate_goal_progress()
        
        result = {
            "sensors": states,
            "helpers": {
                "protein_goal": await self.get_helper_value("protein_goal"),
                "calories_goal": await self.get_helper_value("calories_goal"),
            },
            "progress": progress,
        }
        
        _LOGGER.info("All states: %s", result)
        return result
