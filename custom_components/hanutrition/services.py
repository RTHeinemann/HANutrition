"""HANutrition services for manual meal logging."""

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, MEAL_TYPES
from .database import FOOD_DATABASE

# Service schemas
SERVICE_LOG_MEAL_SCHEMA = vol.Schema({
    vol.Required("meal_type"): vol.In(MEAL_TYPES),
    vol.Optional("food_name"): cv.string,
    vol.Optional("calories", default=0): cv.positive_float,
    vol.Optional("protein", default=0): cv.positive_float,
    vol.Optional("carbs", default=0): cv.positive_float,
    vol.Optional("fat", default=0): cv.positive_float,
    vol.Optional("serving_g", default=100): cv.positive_float,
    vol.Optional("quantity", default=1): cv.positive_float,
    vol.Optional("notes"): cv.string,
})

SERVICE_ADD_FOOD_SCHEMA = vol.Schema({
    vol.Required("food_name"): cv.string,
    vol.Required("calories"): cv.positive_float,
    vol.Required("protein"): cv.positive_float,
    vol.Required("carbs"): cv.positive_float,
    vol.Required("fat"): cv.positive_float,
    vol.Optional("serving_g", default=100): cv.positive_float,
})

SERVICE_LOG_QUICK_SCHEMA = vol.Schema({
    vol.Required("food_name"): cv.string,
    vol.Optional("quantity", default=1): cv.positive_float,
})

# Service descriptors for frontend
SERVICE_DESCRIPTORS = [
    {
        "name": "log_meal",
        "description": "Log a meal with nutritional info",
        "fields": [
            {"name": "meal_type", "type": "select", "options": MEAL_TYPES},
            {"name": "food_name", "type": "text"},
            {"name": "calories", "type": "number"},
            {"name": "protein", "type": "number"},
            {"name": "carbs", "type": "number"},
            {"name": "fat", "type": "number"},
            {"name": "serving_g", "type": "number"},
            {"name": "quantity", "type": "number"},
            {"name": "notes", "type": "text"},
        ],
    },
    {
        "name": "add_food",
        "description": "Add custom food to database",
        "fields": [
            {"name": "food_name", "type": "text"},
            {"name": "calories", "type": "number"},
            {"name": "protein", "type": "number"},
            {"name": "carbs", "type": "number"},
            {"name": "fat", "type": "number"},
            {"name": "serving_g", "type": "number"},
        ],
    },
    {
        "name": "log_quick",
        "description": "Quick meal log using food database",
        "fields": [
            {"name": "food_name", "type": "text"},
            {"name": "quantity", "type": "number"},
        ],
    },
]


def register_services(hass: HomeAssistant) -> None:
    """Register all HANutrition services."""
    if hass.data.get(DOMAIN, {}).get("services_registered"):
        return
    
    _log_meal_service = lambda call: _handle_log_meal(hass, call)
    _add_food_service = lambda call: _handle_add_food(hass, call)
    _log_quick_service = lambda call: _handle_log_quick(hass, call)
    
    hass.services.register(DOMAIN, "log_meal", _log_meal_service, SERVICE_LOG_MEAL_SCHEMA)
    hass.services.register(DOMAIN, "add_food", _add_food_service, SERVICE_ADD_FOOD_SCHEMA)
    hass.services.register(DOMAIN, "log_quick", _log_quick_service, SERVICE_LOG_QUICK_SCHEMA)
    
    hass.data[DOMAIN]["services_registered"] = True


async def _handle_log_meal(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle log_meal service call."""
    db = hass.data[DOMAIN]["database"]
    user_id = db.get_active_user_id()
    
    food_name = call.data.get("food_name", "Sonstiges")
    quantity = call.data.get("quantity", 1)
    
    # Calculate final values if food database match found
    if food_name.lower() in FOOD_DATABASE:
        food = FOOD_DATABASE[food_name.lower()]
        base_cal = food["calories"] * (call.data["serving_g"] / 100) * quantity
        base_prot = food["protein"] * (call.data["serving_g"] / 100) * quantity
        base_carbs = food["carbs"] * (call.data["serving_g"] / 100) * quantity
        base_fat = food["fat"] * (call.data["serving_g"] / 100) * quantity
    else:
        base_cal = call.data["calories"] * quantity
        base_prot = call.data["protein"] * quantity
        base_carbs = call.data["carbs"] * quantity
        base_fat = call.data["fat"] * quantity
    
    db.log_meal(
        user_id=user_id,
        meal_type=call.data["meal_type"],
        food_name=food_name,
        calories=base_cal,
        protein=base_prot,
        carbs=base_carbs,
        fat=base_fat,
        serving_g=call.data["serving_g"],
        quantity=quantity,
    )
    
    # Save to input helper for state tracking
    await hass.services.async_call(
        "input_number", "set_value", {
            "entity_id": f"input_number.nutrition_{call.data['meal_type']}",
            "value": base_cal,
        },
    )
    
    if call.data.get("notes"):
        await hass.services.async_call(
            "input_text", "set_value", {
                "entity_id": "input_text.nutrition_notes",
                "value": call.data["notes"],
            },
        )
    
    # Update UI with success message
    await hass.services.async_call(
        "persistent_notification", "create", {
            "title": f"✅ {food_name} für {call.data['meal_type']} gespeichert",
            "message": f"{base_cal:.0f} kcal • {base_prot:.0f}g Protein • {base_carbs:.0f}g Kohlenhydrate • {base_fat:.0f}g Fett",
            "notification_id": "nutrition_log_success",
        },
    )


async def _handle_add_food(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle add_food service call."""
    db = hass.data[DOMAIN]["database"]
    
    success = db.add_food_to_db(
        name=call.data["food_name"],
        calories=call.data["calories"],
        protein=call.data["protein"],
        carbs=call.data["carbs"],
        fat=call.data["fat"],
        serving_g=call.data["serving_g"],
    )
    
    if success:
        await hass.services.async_call(
            "persistent_notification", "create", {
                "title": "✅ Essen hinzugefügt",
                "message": f"Neues Essen '{call.data['food_name']}' zur Datenbank hinzugefügt.",
                "notification_id": "nutrition_add_success",
            },
        )


async def _handle_log_quick(hass: HomeAssistant, call: ServiceCall) -> None:
    """Handle log_quick service call."""
    db = hass.data[DOMAIN]["database"]
    food_name = call.data["food_name"].lower()
    
    # Auto-detect from food database
    matched_food = None
    for key, info in FOOD_DATABASE.items():
        if key in food_name or food_name in key:
            matched_food = info
            break
    
    if not matched_food:
        await hass.services.async_call(
            "persistent_notification", "create", {
                "title": "❌ Essen nicht gefunden",
                "message": f"'{call.data['food_name']}' ist nicht in der Datenbank. Bitte manuell loggen oder zum Food-Database hinzufügen.",
                "notification_id": "nutrition_log_error",
            },
        )
        return
    
    quantity = call.data.get("quantity", 1)
    
    # Log as snack type by default
    db.log_meal(
        user_id=db.get_active_user_id(),
        meal_type="snack",
        food_name=matched_food["name"],
        calories=matched_food["calories"] * quantity,
        protein=matched_food["protein"] * quantity,
        carbs=matched_food["carbs"] * quantity,
        fat=matched_food["fat"] * quantity,
        serving_g=matched_food["serving_g"],
        quantity=quantity,
    )
    
    await hass.services.async_call(
        "persistent_notification", "create", {
            "title": f"✅ {matched_food['name']} x{quantity}",
            "message": f"{matched_food['calories'] * quantity:.0f} kcal • {matched_food['protein'] * quantity:.0f}g Protein",
            "notification_id": "nutrition_log_success",
        },
    )
