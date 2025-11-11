"""
Legacy placeholder platform.

Home Assistant may still try to import this module if an older config entry
referenced the number platform. We keep the module so setup does not fail,
and immediately warn users to remove the obsolete entity. New installs use
the select platform for power levels.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    _LOGGER.warning(
        "The Ravelli Smart Wi‑Fi power number platform is deprecated. "
        "Please remove the old entity; power control now uses select.ravelli_*."
    )
    return True
