"""Tests for the LG ESS (local) data coordinator parsing."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

from custom_components.lg_ess_local.coordinator import LgEssLocalCoordinator

from .const import EXPECTED, HOST, SAMPLE_BMS, SAMPLE_SERVER


async def test_coordinator_parses_sample(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """The coordinator normalizes the BMS HTML + server JSON correctly."""
    aioclient_mock.get(f"http://{HOST}/getbmsdata", text=SAMPLE_BMS)
    aioclient_mock.get(f"http://{HOST}/getserverst", json=SAMPLE_SERVER)

    coordinator = LgEssLocalCoordinator(hass, HOST, None)
    data = await coordinator._async_update_data()

    for key, expected in EXPECTED.items():
        assert data[key] == expected, f"{key}: {data[key]!r} != {expected!r}"


async def test_coordinator_update_failed(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A transport error surfaces as UpdateFailed."""
    from homeassistant.helpers.update_coordinator import UpdateFailed

    aioclient_mock.get(f"http://{HOST}/getbmsdata", exc=ConnectionError("down"))

    coordinator = LgEssLocalCoordinator(hass, HOST, None)
    try:
        await coordinator._async_update_data()
    except UpdateFailed:
        return
    raise AssertionError("expected UpdateFailed")
