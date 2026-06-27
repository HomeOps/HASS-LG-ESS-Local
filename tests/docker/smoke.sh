#!/usr/bin/env bash
# hass/core docker smoke test.
#
# Loads the integration inside the official Home Assistant container so that
# real-HA import and manifest errors are caught (e.g. importing DeviceInfo from
# a module that does not exist) - things hassfest alone does not catch.
#
# Usage:
#   bash tests/docker/smoke.sh
#   HA_IMAGE=ghcr.io/home-assistant/home-assistant:2025.6 bash tests/docker/smoke.sh
set -euo pipefail

IMAGE="${HA_IMAGE:-ghcr.io/home-assistant/home-assistant:stable}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "==> Pulling ${IMAGE}"
docker pull -q "${IMAGE}"

echo "==> Importing every integration module under real Home Assistant"
docker run --rm \
  -e PYTHONPATH=/config \
  -v "${ROOT}/custom_components:/config/custom_components:ro" \
  "${IMAGE}" \
  python -c '
import importlib

from homeassistant.const import __version__ as ha_version

MODULES = [
    "__init__",
    "const",
    "coordinator",
    "config_flow",
    "entity",
    "sensor",
    "binary_sensor",
]
for name in MODULES:
    importlib.import_module(f"custom_components.lg_ess_local.{name}")
    print(f"  ok  custom_components.lg_ess_local.{name}")
print(f"All modules import cleanly under Home Assistant {ha_version}")
'

echo "==> Validating Home Assistant configuration with the integration present"
docker run --rm \
  -v "${ROOT}/custom_components:/config/custom_components:ro" \
  -v "${ROOT}/tests/docker/configuration.yaml:/config/configuration.yaml:ro" \
  "${IMAGE}" \
  python -m homeassistant --script check_config -c /config

echo "==> Docker smoke test passed"
