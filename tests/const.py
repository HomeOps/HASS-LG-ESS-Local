"""Shared sample data for the LG ESS (local) tests.

The BMS sample mirrors the real /getbmsdata HTML (a <td>Key</td><td>Value</td>
table, values carrying units) captured from a live RESU unit.
"""

from __future__ import annotations

HOST = "192.168.1.50"
MAC = "64:cb:e9:f2:5e:8e"

SAMPLE_APINFO = {
    "state": 0,
    "ssid": "RESU_64CBE9F25E8E",
    "pwd": "64CBE9F25E8E1234",
    "chl": 11,
    "ecn": 4,
    "ssidhidden": 0,
}

SAMPLE_SERVER = {
    "ServerStatusCap": "Status",
    "bmsOperationMode": "Normal/Running",
    "canStatus": "OK",
    "wifiConnection": "OK",
    "ethConnection": "NO",
    "serverConnection": "OK",
    "state": 0,
}

# Note: RealSOC precedes SOC to prove the SOC regex does not match RealSOC,
# and temperature uses the &#8451 (degree-C) entity like the real portal.
SAMPLE_BMS = """<caption>BMS Periodic Data</caption>
<tr><th>Item</th><th>Value</th></tr>
<tr><td>Time</td><td>Fri Jun 26 13:43:32 2026</td></tr>
<tr><td>RealSOC</td><td>98.72%</td></tr>
<tr><td>SOC</td><td>98.72%</td></tr>
<tr><td>SOH</td><td>89.09%</td></tr>
<tr><td>Current</td><td>5.700A</td></tr>
<tr><td>BPI_Voltage</td><td>272.3V</td></tr>
<tr><td>AvgTemperature</td><td>34.0&#8451</td></tr>
<tr><td>CycleCount</td><td>732 Cycle</td></tr>
<tr><td>LifeTimeDischargeEnergy</td><td>10546767Wh</td></tr>
<tr><td>IPI_Voltage</td><td>410.7V</td></tr>
<tr><td>IPI_Current</td><td>1.9A</td></tr>
"""

# Expected normalized coordinator output for the sample above.
EXPECTED = {
    "soc": 98.72,
    "soh": 89.09,
    "current": 5.7,
    "voltage": 272.3,
    "temperature": 34.0,
    "cycle_count": 732,
    "lifetime_discharge": 10546.8,  # round(10546767 / 1000, 1)
    "power": round(410.7 * 1.9),    # 780
    "operation_mode": "Normal/Running",
    "wifi": "OK",
    "cloud": "OK",
}
