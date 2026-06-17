from datetime import timedelta

DOMAIN = "samsung_custom"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_ACCESS_TOKEN = "access_token"

UPDATE_INTERVAL = timedelta(seconds=60)

# Capabilities
CAP_WASHING_COURSE = "samsungce.dishwasherWashingCourse"
CAP_OPERATING_STATE = "dishwasherOperatingState"
CAP_DISHWASHER_OPERATION = "samsungce.dishwasherOperation"
CAP_REMOTE_CONTROL = "remoteControlStatus"
CAP_SWITCH = "switch"
CAP_WASHING_OPTIONS = "samsungce.dishwasherWashingOptions"

# Added generic capabilities
CAP_WASHER_COURSE = "samsungce.washerCycle"
CAP_WASHER_OPERATING_STATE = "samsungce.washerOperatingState"
CAP_DRYER_COURSE = "samsungce.dryerCycle"
CAP_DRYER_OPERATING_STATE = "samsungce.dryerOperatingState"
CAP_OVEN_OPERATING_STATE = "samsungce.ovenOperatingState"
CAP_TEMPERATURE_MEASUREMENT = "temperatureMeasurement"
CAP_THERMOSTAT_COOLING = "thermostatCoolingSetpoint"

SAMSUNG_WASHER_CYCLES = {
    "01": "Cotton",
    "02": "Synthetics",
    "03": "Wool",
    "04": "Hand Wash",
    "05": "Daily Wash",
    "06": "Quick Wash",
    "07": "Intensive Cold",
    "08": "Super Eco Wash",
    "09": "Super Eco Wash",
    "0A": "Bedding",
    "0B": "15' Quick Wash",
    "0C": "Rinse + Spin",
    "0D": "Spin",
    "0E": "Drain/Spin",
    "11": "Drum Clean",
    "1C": "Eco 40-60",
    "1D": "Speed Wash+Dry",
    "1E": "Outdoor Care",
    "1F": "Baby Care",
    "21": "Denim",
    "2B": "Active Wear",
    "2C": "Colors",
    "35": "Towels",
    "37": "Dry Only",
    "38": "Cotton Dry",
    "39": "Synthetics Dry",
    "7F": "Mixed Load",
    "96": "Silent Wash",
    "A0": "Wash and Dry",
    "A1": "Air Wash",
    "A2": "Deodorization",
    "A3": "Sanitization",
}

