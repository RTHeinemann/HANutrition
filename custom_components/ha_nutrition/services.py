"""Service handlers for ha_nutrition."""

import logging
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from .const import (
    DOMAIN, SERVICE_LOG_MEAL, SERVICE_ADD_FOOD, SERVICE_SEARCH_FOOD,
    SERVICE_ADD_USER, SERVICE_SET_ACTIVE_USER, MEAL_TYPES
)

_LOGGER = logging.getLogger(__name__)

# Service schemas
LOG_MEAL_SCHEMA = vol.Schema({
    vol.Required("meal_type"): vol.In(MEAL_TYPES),
    vol.Required("food_name"): cv.string,
    vol.Required("calories"): cv.positive_float,
    vol.Required("protein"): cv.positive_float,
    vol.Required("carbs"): cv.positive_float,
    vol.Required("fat"): cv.positive_float,
    vol.Optional("notes"): cv.string,
    vol.Optional("user_id"): cv.string,
})

ADD_FOOD_SCHEMA = vol.Schema({
    vol.Required("name"): cv.string,
    vol.Required("calories"): cv.positive_float,
    vol.Required("protein"): cv.positive_float,
    vol.Required("carbs"): cv.positive_float,
    vol.Required("fat"): cv.positive_float,
    vol.Optional("category"): cv.string,
    vol.Optional("unit"): cv.string,
})

SEARCH_FOOD_SCHEMA = vol.Schema({
    vol.Required("query"): cv.string,
})

ADD_USER_SCHEMA = vol.Schema({
    vol.Required("name"): cv.string,
})

SET_USER_SCHEMA = vol.Schema({
    vol.Required("user_id"): cv.string,
})

SERVICES = {
    SERVICE_LOG_MEAL: LOG_MEAL_SCHEMA,
    SERVICE_ADD_FOOD: ADD_FOOD_SCHEMA,
    SERVICE_SEARCH_FOOD: SEARCH_FOOD_SCHEMA,
    SERVICE_ADD_USER: ADD_USER_SCHEMA,
    SERVICE_SET_ACTIVE_USER: SET_USER_SCHEMA,
}

# Service descriptions for UI
SERVICE_DESCRIPTORS = {
    SERVICE_LOG_MEAL: {
        "description": "Mahlzeit erfassen",
        "fields": {
            "meal_type": {"description": "Mahlzeit-Typ", "example": "frühstück"},
            "food_name": {"description": "Essensname", "example": "Hähnchenbrust"},
            "calories": {"description": "Kalorien in kcal", "example": "165"},
            "protein": {"description": "Protein in g", "example": "31"},
            "carbs": {"description": "Kohlenhydrate in g", "example": "0"},
            "fat": {"description": "Fett in g", "example": "3.6"},
            "notes": {"description": "Notizen (optional)", "example": "mit Gewürzen"},
        },
    },
    SERVICE_ADD_FOOD: {
        "description": "Neues Lebensmittel zur Datenbank hinzufügen",
        "fields": {
            "name": {"description": "Name", "example": "Kichererbsen"},
            "calories": {"description": "Kalorien pro 100g", "example": "164"},
            "protein": {"description": "Protein pro 100g", "example": "8.9"},
            "carbs": {"description": "Kohlenhydrate pro 100g", "example": "27"},
            "fat": {"description": "Fett pro 100g", "example": "2.6"},
        },
    },
    SERVICE_SEARCH_FOOD: {
        "description": "Lebensmittel in der Datenbank suchen",
        "fields": {
            "query": {"description": "Suchbegriff", "example": "Reis"},
        },
    },
    SERVICE_ADD_USER: {
        "description": "Neuen Benutzer anlegen",
        "fields": {
            "name": {"description": "Name", "example": "Lucas"},
        },
    },
    SERVICE_SET_ACTIVE_USER: {
        "description": "Aktiven Benutzer setzen",
        "fields": {
            "user_id": {"description": "Benutzer-ID", "example": "default"},
        },
    },
}

def register_services(hass: HomeAssistant):
    """Register all custom services."""
    for service_name, service_schema in SERVICES.items():
        try:
            hass.services.async_register(
                DOMAIN, service_name,
                _make_handler(service_name, hass),
                schema=service_schema,
            )
            _LOGGER.info("Registered service %s.%s", DOMAIN, service_name)
        except Exception as e:
            _LOGGER.warning("Could not register service %s.%s: %s", DOMAIN, service_name, str(e))

def _make_handler(service_name: str, hass: HomeAssistant):
    """Create a handler closure for a service."""
    async def handler(call: ServiceCall):
        db = hass.data[DOMAIN]["database"]
        
        if service_name == SERVICE_LOG_MEAL:
            meal_data = {
                "meal_type": call.data.get("meal_type", "sonstiges"),
                "food_name": call.data.get("food_name", "Unbekannt"),
                "calories": float(call.data.get("calories", 0)),
                "protein": float(call.data.get("protein", 0)),
                "carbs": float(call.data.get("carbs", 0)),
                "fat": float(call.data.get("fat", 0)),
                "notes": call.data.get("notes"),
                "user_id": call.data.get("user_id", "default"),
            }
            
            _LOGGER.info("Logging meal: %s", meal_data)
            db.log_meal(**meal_data)
            
        elif service_name == SERVICE_ADD_FOOD:
            food_data = {
                "name": call.data.get("name"),
                "calories_100g": float(call.data.get("calories", 0)),
                "protein_100g": float(call.data.get("protein", 0)),
                "carbs_100g": float(call.data.get("carbs", 0)),
                "fat_100g": float(call.data.get("fat", 0)),
                "category": call.data.get("category", "sonstige"),
                "portation_desc": call.data.get("unit", "100g"),
            }
            db.add_food(**food_data)
            
        elif service_name == SERVICE_SEARCH_FOOD:
            query = call.data.get("query", "")
            results = db.search_food(query)
            _LOGGER.info("Search results for '%s': %d found", query, len(results))
            
        elif service_name == SERVICE_ADD_USER:
            name = call.data.get("name")
            user_id = name.lower().replace(" ", "_")
            db.add_user(user_id, name)
            _LOGGER.info("User '%s' added with id '%s'", name, user_id)
            
        elif service_name == SERVICE_SET_ACTIVE_USER:
            user_id = call.data.get("user_id")
            _LOGGER.info("Active user set to: %s", user_id)
    
    return handler
