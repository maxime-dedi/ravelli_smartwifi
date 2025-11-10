# Ravelli Smart Wi‑Fi — Home Assistant Custom Integration (Unofficial)

> **Status:** MVP skeleton ready to push to GitHub. Cloud API calls are stubbed — fill in the endpoints in `api.py` to make it work with your account.  
> **Why this exists?** Public repos disappeared; this gives you a modern, config‑flow, coordinator‑based integration that you can extend.

## Features (designed)
- Config Flow (UI): email, password, base URL, device ID
- DataUpdateCoordinator (polls status)
- Entities:
  - `climate.ravelli_*` (heat/off, target temperature)
  - Sensors: ambient temperature, target setpoint, power level, status text/code
- Options Flow: change polling interval, base URL, device id

## Known limitations
- The **cloud API for Ravelli Smart Wi‑Fi is not public**. The `api.py` has placeholders where you must put the actual endpoints/headers derived from your traffic (mobile app) or docs if available.
- MFA / captcha not implemented.

## Install (local testing)
1. Copy the `custom_components/ravelli_smartwifi` folder into your Home Assistant `/config/custom_components/`.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration → Ravelli Smart Wi‑Fi**.
4. Enter your **email / password**, **base URL** (example: `https://smart.ravelli.cloud/`), and **Device ID**.
5. If login fails, update `api.py` endpoint paths and JSON keys to match your cloud.

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
