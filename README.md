# LG ESS (local) — Home Assistant integration

[![hacs][hacs-badge]][hacs] [![Validate](https://github.com/HomeOps/HASS-LG-ESS-Local/actions/workflows/validate.yml/badge.svg)](https://github.com/HomeOps/HASS-LG-ESS-Local/actions/workflows/validate.yml)

A **local, no-cloud** Home Assistant integration for **LG ESS / RESU** home batteries
(the LG Energy Solution RMD communication module — the one paired with LG EnerVu Plus).

It reads the battery's **local web portal over HTTP (port 80)** and exposes the data as
a proper Home Assistant **device** with sensors.

## Why this exists

The popular [`dkarv/ha-lg-ess`](https://github.com/dkarv/ha-lg-ess) integration (and the
`pyess` library) talk to LG's local **`/v1` HTTPS API on port 443**. On a number of units
that API is **disabled on the LAN/station interface** — it only answers on the battery's
own Wi-Fi setup AP — so those integrations can't connect over your network.

This integration instead scrapes the **RMD web portal** endpoints that *are* served on the
LAN, **unauthenticated**:

| Endpoint | Data |
|---|---|
| `GET /getbmsdata` | HTML table: SOC, SOH, current, cell/pack voltages, temperatures, cycle count, lifetime energy |
| `GET /getserverst` | JSON: operating mode + Wi-Fi/cloud connectivity |
| `GET /configapinfo` | JSON: SoftAP SSID `RESU_<MAC>` → used for the device's unique id |

No password, no cloud, no port 443.

## Entities

A single **LG ESS Battery** device with:

| Entity | Unit | Notes |
|---|---|---|
| State of charge | % | `device_class: battery` |
| State of health | % | |
| Power | W | DC at the inverter interface (`IPI_V × IPI_A`) |
| Current | A | positive = charging on this unit |
| Voltage | V | pack voltage |
| Temperature | °C | average cell temperature |
| Cycle count | — | `total_increasing` |
| Lifetime discharge | kWh | `device_class: energy`, `total_increasing` |
| Operation mode | — | e.g. `Normal/Running` |
| Wi-Fi status / Cloud status | — | connectivity |
| Charging | — | `binary_sensor`, `battery_charging` |

## Installation (HACS)

1. HACS → ⋮ → **Custom repositories**.
2. Add `https://github.com/HomeOps/HASS-LG-ESS-Local`, category **Integration**.
3. Install **LG ESS (local)** and restart Home Assistant.
4. **Settings → Devices & Services → Add Integration → LG ESS (local)**.
5. Enter the battery's **IP address** (e.g. `192.168.80.51`).

> Tip: give the battery a **DHCP reservation** so its IP doesn't change.

## Requirements

- Home Assistant **2024.1** or newer.
- The battery reachable on your LAN with its **web portal on port 80** open
  (the default for the RMD module).

## Notes & limitations

- **Read-only.** This integration does not control the battery.
- The **power sign** (charge vs discharge) is derived from the inverter-interface current;
  on these units positive current is charging. If your unit reports it inverted, open an issue.
- If your unit *does* expose the `/v1` HTTPS API on the LAN, consider
  [`dkarv/ha-lg-ess`](https://github.com/dkarv/ha-lg-ess) for the richer official API.

## Development / Testing

Two layers of tests, both run in CI (`.github/workflows/tests.yml`):

**Unit tests** (HA test harness) — config flow, coordinator parsing, and full
entry → device/sensor setup, using `pytest-homeassistant-custom-component`:

```bash
pip install -r requirements_test.txt
pytest
```

**hass/core docker smoke test** — loads the integration inside the official
Home Assistant container to catch real-HA import/manifest errors that hassfest
misses:

```bash
bash tests/docker/smoke.sh
# or pin a version:
HA_IMAGE=ghcr.io/home-assistant/home-assistant:stable bash tests/docker/smoke.sh
```

## License

[MIT](LICENSE) © Oscar Calvo / HomeOps

[hacs]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg
