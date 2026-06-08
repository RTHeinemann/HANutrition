"""HANutrition - Nutrition tracking integration for Home Assistant."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .database import NutritionDatabase
from .services import register_services, SERVICE_DESCRIPTORS
import logging

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the HANutrition component."""
    db_dir = hass.config.path(DOMAIN)
    db_path = hass.config.path(f"{DOMAIN}/hanutrition.db")
    
    db = NutritionDatabase(db_path, db_dir)
    db.initialize()
    
    hass.data.setdefault(DOMAIN, {})["database"] = db
    
    register_services(hass)
    hass.data.setdefault(DOMAIN, {})["services_registered"] = True
    hass.data.setdefault(DOMAIN, {})["service_descriptors"] = SERVICE_DESCRIPTORS
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HANutrition from a config entry."""
    await async_setup(hass, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok
