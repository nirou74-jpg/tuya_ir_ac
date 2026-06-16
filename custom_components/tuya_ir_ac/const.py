"""Constants for the Tuya IR AC integration."""

DOMAIN = "tuya_ir_ac"

CONF_CLIENT_ID = "client_id"
CONF_SECRET_KEY = "secret_key"
CONF_DEVICE_ID = "device_id"
CONF_REGION = "region"

# Région -> base URL de l'API Tuya OpenAPI
REGIONS = {
    "eu": "https://openapi.tuyaeu.com",
    "us": "https://openapi.tuyaus.com",
    "cn": "https://openapi.tuyacn.com",
    "in": "https://openapi.tuyain.com",
}
DEFAULT_REGION = "eu"

# Intervalle de rafraîchissement du status (secondes)
SCAN_INTERVAL_SECONDS = 30

# ---- Mapping des modes (M) ----
# M = 0 cold, 1 heat, 2 auto, 3 dehumidification (dry), 4 wind_dry (fan_only)
MODE_TO_M = {
    "cool": 0,
    "heat": 1,
    "auto": 2,
    "dry": 3,
    "fan_only": 4,
}
M_TO_MODE = {v: k for k, v in MODE_TO_M.items()}

# ---- Mapping des ventilateurs (F) ----
# F = 0 auto, 1 low, 2 medium, 3 high
FAN_TO_F = {
    "auto": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}
F_TO_FAN = {v: k for k, v in FAN_TO_F.items()}

# Bornes de température
TEMP_MIN = 16
TEMP_MAX = 30
TEMP_STEP = 1
