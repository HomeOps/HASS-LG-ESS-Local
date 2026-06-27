"""Tests for the LG ESS (local) config flow."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.lg_ess_local.const import CONF_MAC, DOMAIN

from .const import HOST, MAC, SAMPLE_APINFO, SAMPLE_BMS


async def test_user_flow_success(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A valid host creates an entry with the MAC as the unique id."""
    aioclient_mock.get(f"http://{HOST}/getbmsdata", text=SAMPLE_BMS)
    aioclient_mock.get(f"http://{HOST}/configapinfo", json=SAMPLE_APINFO)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_HOST: HOST, CONF_MAC: MAC}
    assert result["result"].unique_id == MAC


async def test_user_flow_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A transport error shows the cannot_connect error."""
    aioclient_mock.get(f"http://{HOST}/getbmsdata", exc=ConnectionError("down"))

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_duplicate_aborts(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Configuring the same battery twice aborts."""
    MockConfigEntry(domain=DOMAIN, unique_id=MAC, data={CONF_HOST: HOST}).add_to_hass(
        hass
    )
    aioclient_mock.get(f"http://{HOST}/getbmsdata", text=SAMPLE_BMS)
    aioclient_mock.get(f"http://{HOST}/configapinfo", json=SAMPLE_APINFO)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
