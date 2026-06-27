# HASS-LG-ESS-Local — project directives

HACS-compatible Home Assistant integration for LG ESS / RESU batteries that reads the
**local RMD web portal (HTTP, port 80)** — used because the LG `/v1` HTTPS API (443) is
disabled on the LAN side of many units.

## Layout
- `custom_components/lg_ess_local/` — the integration (domain `lg_ess_local`).
  - `coordinator.py` — `DataUpdateCoordinator`; fetches `/getbmsdata` (HTML) + `/getserverst` (JSON).
  - `config_flow.py` — IP entry; unique id from `RESU_<MAC>` via `/configapinfo`.
  - `sensor.py` / `binary_sensor.py` — declarative entity descriptions; one device.
  - `entity.py` — shared `DeviceInfo` base.
- No external Python `requirements` — uses HA's aiohttp client + stdlib `re`.

## Conventions
- **Conventional Commits** (release-please): `feat:`, `fix:`, `docs:`, `chore:`, `ci:`, …
  PR titles drive the changelog and version bump.
- **Versioning:** release-please bumps `custom_components/lg_ess_local/manifest.json`
  `version` via `extra-files` (jsonpath `$.version`) and `.release-please-manifest.json`.
  Do not hand-edit the version — let the release PR do it.
- **CI:** `validate.yml` runs **hassfest** + **HACS** action on every push/PR. Keep both green.
- Bootstrap version is `0.0.0`; the first `feat:` produces the `0.1.0` release PR.

## Data source notes
- `/getbmsdata` is an HTML table of `<td>Key</td><td>Value</td>` rows; values carry units
  (`98.72%`, `-5.700A`, `34.0&#8451`), parsed by leading-number regex.
- SOC key is `SOC` (distinct from `RealSOC`); power = `IPI_Voltage × IPI_Current`.
- All endpoints are **unauthenticated**; no credentials are stored.

---
*Last garbage-collected: 2026-06-26*
