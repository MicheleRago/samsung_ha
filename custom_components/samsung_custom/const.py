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
CAP_OVEN_OPERATING_STATE_STANDARD = "ovenOperatingState"
OVEN_OPERATING_STATE_CAPABILITIES = (
    CAP_OVEN_OPERATING_STATE,
    CAP_OVEN_OPERATING_STATE_STANDARD,
)
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
    # Labels aligned with the SmartThings app for this oven model.
    "heating": "Convenzione",
    "Bake": "Ventola convenzionale",
    "Broil": "Grill Grande",
    "ConvectionBroil": "Grill ventilato",
    "ConvectionRoast": "Riscaldamento superiore+convenzione",
    "ConvectionBake": "Riscaldamento inferiore+convenzione",
    "SlimStrong": "Cottura intensiva",
    "BottomHeat": "Rosolatura",
    "Conventional": "Ventola convenzionale",
    "KeepWarm": "Mantenimento caldo",
    "BreadProof": "Lievitazione",
    "AirFryer": "Air Fryer",
    "SelfClean": "Autopulizia",
    "SteamClean": "Pulizia a vapore",
    
    # Altre modalità per sicurezza
    "SteamCook": "Cottura a Vapore",
    "MWplusHotBlast2": "Microonde + Hot Blast 2",
    "SlimMiddle": "Slim Middle",
    "SlowCook": "Cottura Lenta",
    "Proof": "Lievitazione",
    "Dehydrate": "Disidratazione",
    "Others": "Altro",
    "StrongSteam": "Vapore Forte",
    "Descale": "Decalcificazione",
    "Rinse": "Risciacquo"
}

OVEN_DEFAULT_MODES = (
    "heating",
    "Bake",
    "Broil",
    "ConvectionBroil",
    "ConvectionRoast",
    "ConvectionBake",
    "SlimStrong",
    "BottomHeat",
)

OVEN_EXTRA_MODES = (
    "KeepWarm",
    "BreadProof",
    "AirFryer",
    "Dehydrate",
    "SelfClean",
    "SteamClean",
)

OVEN_SELECT_MODES = OVEN_DEFAULT_MODES + OVEN_EXTRA_MODES

OVEN_MODE_COMMAND_ALIASES = {}

OVEN_MODE_NAME_ALIASES = {
    "Convenzione": "heating",
    "Convezione": "heating",
    "Forno ventilato": "heating",
    "Ventilato": "heating",
    "Cottura ventilata": "heating",
    "Ventola convenzionale": "Bake",
    "Ventola convenzionata": "Bake",
    "Grill Grande": "Broil",
    "Grill ventilato": "ConvectionBroil",
    "Riscaldamento superiore+convenzione": "ConvectionRoast",
    "Riscaldamento superiore+convezione": "ConvectionRoast",
    "Riscaldamento superiore + convenzione": "ConvectionRoast",
    "Riscaldamento superiore + convezione": "ConvectionRoast",
    "Riscaldamento inferiore+convenzione": "ConvectionBake",
    "Riscaldamento inferiore+convezione": "ConvectionBake",
    "Riscaldamento inferiore + convenzione": "ConvectionBake",
    "Riscaldamento inferiore + convezione": "ConvectionBake",
    "Cottura intensiva": "SlimStrong",
    "Rosolatura": "BottomHeat",
    "Mantenimento caldo": "KeepWarm",
    "Lievitazione": "BreadProof",
    "Air Fryer": "AirFryer",
    "Disidratazione": "Dehydrate",
    "Autopulizia": "SelfClean",
    "Pulizia a vapore": "SteamClean",
}


def normalize_oven_mode_code(mode):
    """Return a SmartThings mode code that can be used in commands."""
    if isinstance(mode, str):
        return OVEN_MODE_COMMAND_ALIASES.get(
            mode,
            OVEN_MODE_NAME_ALIASES.get(mode, mode),
        )
    return mode


def get_oven_operating_state(status):
    """Return oven operating state capability data from either known API name."""
    for capability in OVEN_OPERATING_STATE_CAPABILITIES:
        if capability in status:
            return status.get(capability) or {}
    return {}

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
