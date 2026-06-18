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

# Oven specific capabilities
CAP_OVEN_MODE = "samsungce.ovenMode"
CAP_OVEN_SETPOINT = "ovenSetpoint"
CAP_MICROWAVE_POWER = "samsungce.microwavePower"
CAP_OVEN_DOOR = "samsungce.doorState"
CAP_OVEN_LAMP = "samsungce.lamp"
CAP_KIDS_LOCK = "samsungce.kidsLock"

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

OVEN_MODE_MAP = {
    "Bake": "Statico",
    "ConvectionBake": "BottomHeatplusConvection",
    "ConvectionRoast": "TopHeatplusConvection",
    "Broil": "LargeGrill",
    "LargeGrill": "LargeGrill",
    "ConvectionBroil": "Grill Ventilato",
    "SteamCook": "Cottura a Vapore",
    "SteamBake": "Cottura a Vapore",
    "SteamRoast": "Arrosto a Vapore",
    "SteamBottomHeatplusConvection": "Vapore + Calore Inf + Ventilato",
    "Microwave": "Microonde",
    "MWplusGrill": "Microonde + Grill",
    "MWplusConvection": "Microonde + Ventilato",
    "MWplusHotBlast": "Microonde + Hot Blast",
    "MWplusHotBlast2": "Microonde + Hot Blast 2",
    "SlimMiddle": "Slim Middle",
    "SlimStrong": "Slim Strong",
    "SlowCook": "Cottura Lenta",
    "Proof": "Lievitazione",
    "Dehydrate": "Disidratazione",
    "Others": "Altro",
    "StrongSteam": "Vapore Forte",
    "Descale": "Decalcificazione",
    "Rinse": "Risciacquo"
}

OVEN_JOB_STATE_MAP = {
    "scheduledStart": "Avvio Programmato",
    "fastPreheat": "Preriscaldamento Rapido",
    "scheduledEnd": "Fine Programmata",
    "stone_heating": "Riscaldamento Pietra",
    "timeHoldPreheat": "Preriscaldamento in Attesa",
}

DISHWASHER_JOB_STATE_MAP = {
    "air_wash": "Lavaggio ad Aria",
    "cooling": "Raffreddamento",
    "drying": "Asciugatura",
    "finish": "Finito",
    "pre_wash": "Prelavaggio",
    "rinse": "Risciacquo",
    "spin": "Centrifuga",
    "wash": "Lavaggio",
    "wrinkle_prevent": "Antipiega"
}
