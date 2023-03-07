"""Countdown sensors"""
from datetime import datetime, timedelta

import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .api import CountdownApi

from .const import (
    DOMAIN,
    SENSOR_NAME
)

NAME = DOMAIN
ISSUEURL = "https://github.com/codyc1515/hacs_countdown/issues"

STARTUP = f"""
-------------------------------------------------------------------
{NAME}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUEURL}
-------------------------------------------------------------------
"""

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ACCESS_TOKEN): cv.string
})

SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities
):
    config = hass.data[DOMAIN][config_entry.entry_id]
    token = config[CONF_ACCESS_TOKEN]
    
    api = CountdownApi(token)
    
    sensors = []
    sensors .append(CountdownDeliveriesSensor(SENSOR_NAME, api))
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    token = config.get(CONF_ACCESS_TOKEN)

    api = CountdownApi(token)

    _LOGGER.debug('Setting up sensor(s) from yaml...')

    sensors = []
    sensors .append(CountdownDeliveriesSensor(SENSOR_NAME, api))
    async_add_entities(sensors, True)


class CountdownDeliveriesSensor(Entity):
    def __init__(self, name, api):
        self._name = name
        self._icon = "mdi:truck-delivery"
        self._state = ""
        self._state_attributes = {}
        self._unit_of_measurement = None
        self._unique_id = DOMAIN
        self._api = api

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._state_attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    def update(self):
        _LOGGER.debug('Checking login validity')
        if self._api.check_auth():
            # Get todays date
            _LOGGER.debug('Fetching deliveries')
            data = []
            response = self._api.get_deliveries()
            if response['orders']:
                _LOGGER.debug(response['orders'])
                for order in response['orders']:
                    # Delivery statuses
                    if order['orderStatus'] == 'PENDING':
                        self._state = "Received"
                    elif order['orderStatus'] == 'UNASSIGNED':
                        self._state = "Out for delivery"
                    elif order['orderStatus'] == 'ASSIGNED':
                        self._state = "Arriving"
                    elif order['orderStatus'] == 'COMPLETE':
                        self._state = "Delivered"

                    # Not sure if this is used for delivery
                    elif order['orderStatus'] == 'FAILEDCOMPLETE':
                        self._state = "Delivery failed"

                    # Not sure if these are used (maybe for pickup?)
                    elif order['orderStatus'] == 'READY':
                        self._state = "Order ready"
                    elif order['orderStatus'] == 'OMW':
                        self._state = "Driver on way"
                    else:
                        self._state = "Unknown orderStatus (" + order['orderStatus'] + ")"

                    self._state_attributes['Order Number'] = order['orderNumber']
                    self._state_attributes['Order Date'] = order['orderDate']
                    self._state_attributes['Pickup Start'] = order['pickupStart']
                    self._state_attributes['Pickup End'] = order['pickupEnd']
            else:
                self._state = "None"
                _LOGGER.debug('Found no orders on refresh')
        else:
            _LOGGER.error('Unable to log in')
