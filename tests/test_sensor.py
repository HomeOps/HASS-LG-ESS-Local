"""End-to-end setup test: entry -> device + sensor states."""

from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.lg_ess_local.const import CONF_MAC, DOMAIN

from .const import HOST, MAC, SAMPLE_BMS, SAMPLE_SERVER


async def _setup(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> MockConfigEntry:
    aioclient_mock.get(f"http://{HOST}/getbmsdata", text=SAMPLE_BMS)
    aioclient_mock.get(f"http://{HOST}/getserverst", json=SAMPLE_SERVER)
    entry = MockConfigEntry(
        domain=DOMAIN, unique_id=MAC, data={CONF_HOST: HOST, CONF_MAC: MAC}
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_sensors_created_with_values(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Setup creates SOC/power sensors and the charging binary sensor."""
    await _setup(hass, aioclient_mock)
    ent_reg = er.async_get(hass)

    soc_id = ent_reg.async_get_entity_id("sensor", DOMAIN, f"{MAC}_soc")
    assert soc_id is not None
    assert hass.states.get(soc_id).state == "98.72"

    power_id = ent_reg.async_get_entity_id("sensor", DOMAIN, f"{MAC}_power")
    assert hass.states.get(power_id).state == "780"

    charging_id = ent_reg.async_get_entity_id("binary_sensor", DOMAIN, f"{MAC}_charging")
    assert hass.states.get(charging_id).state == "on"  # positive current = charging


async def test_single_device(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """All entities are grouped under one device identified by the MAC."""
    entry = await _setup(hass, aioclient_mock)
    dev_reg = dr.async_get(hass)
    device = dev_reg.async_get_device(identifiers={(DOMAIN, MAC)})
    assert device is not None
    assert device.manufacturer == "LG Energy Solution"

    entities = er.async_entries_for_config_entry(
        er.async_get(hass), entry.entry_id
    )
    assert len({e.device_id for e in entities}) == 1


async def test_unload(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """The entry unloads cleanly."""
    entry = await _setup(hass, aioclient_mock)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert DOMAIN not in hass.data or entry.entry_id not in hass.data.get(DOMAIN, {})
