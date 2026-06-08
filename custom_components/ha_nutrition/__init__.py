"""ha_nutrition - Nutrition tracking integration for Home Assistant."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, DB_NAME, DB_DIR
from .database import NutritionDatabase
from .services import register_services, SERVICE_DESCRIPTORS
import logging

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the ha_nutrition component."""
    db_path = hass.config.path(DOMAIN, DB_NAME)
    db_dir = hass.config.path(DOMAIN)
    
    db = NutritionDatabase(db_path, db_dir)
    db.initialize()
    
    hass.data.setdefault(DOMAIN, {})["database"] = db
    
    # Register services
    register_services(hass)
    hass.data.setdefault(DOMAIN, {})["services_registered"] = True
    
    # Store service descriptors for UI
    hass.data.setdefault(DOMAIN, {})["service_descriptors"] = SERVICE_DESCRIPTORS
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ha_nutrition from a config entry."""
    await async_setup(hass, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    return unload_ok
