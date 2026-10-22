"""Constants for the PowerK integration."""

DOMAIN = "powerk"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_TOKEN = "token"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_NAME = "PowerK Smart Strip"
DEFAULT_PORT = 7896
DEFAULT_SCAN_INTERVAL = 5  # seconds
MIN_SCAN_INTERVAL = 2
MAX_SCAN_INTERVAL = 60

# Device info
MANUFACTURER = "LG U+ / Jinheung / TCL"
MODEL = "MTTL-W01"

# Endpoints
API_STATE = "/api/state"
API_ONOFF = "/api/onoff"
