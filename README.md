# Ravelli Smart Wi‑Fi — Home Assistant Custom Integration (Unofficial)

> **Status:** Working against the public CloudWiNet token API (`https://ws.cloudwinet.it/WiNetStove.svc/json`).  
> **Why this exists?** Public repos disappeared; this gives you a modern, config‑flow, coordinator‑based integration that you can extend.

## Features
- Config Flow (UI): API token + base URL (defaults to CloudWiNet)
- DataUpdateCoordinator (polls status)
- Entities:
  - `climate.ravelli_*` (heat/off, target temperature)
  - Sensors: ambient temperature, target setpoint, power level, status text/code + error info
- Options Flow: change polling interval and base URL

## Known limitations
- You still need to extract the **API token (GUID)** from the official Ravelli / CloudWiNet app. The integration cannot obtain it for you.
- Only endpoints exposed by `WiNetStove.svc` are implemented (status, temperature, power, ignit/shutdown). Anything else will need more reverse engineering.

## Install (local testing)
1. Copy the `custom_components/ravelli_smartwifi` folder into your Home Assistant `/config/custom_components/`.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration → Ravelli Smart Wi‑Fi**.
4. Enter the stove **API token** (looks like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`). Default base URL already points to CloudWiNet, but you can override it if needed.
5. Adjust the polling interval/base URL later via the integration options if necessary.

## HACS (optional)
This repo is HACS‑ready (`hacs.json`). After you push to GitHub:
- In HACS → Integrations → Custom repositories → add your repo URL as type **Integration**.

## Development
- Home Assistant min version is pinned in `manifest.json`.
- Use `logger:` in your HA `configuration.yaml` to enable debug:
  ```yaml
  logger:
    default: warning
    logs:
      custom_components.ravelli_smartwifi: debug
  ```

## Disclaimer
This project is unaffiliated with Ravelli. Use at your own risk; rate‑limit your polling (default 30s). Do not publish secrets.
