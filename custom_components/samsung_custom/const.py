from datetime import timedelta

DOMAIN = "samsung_custom"
CONF_PAT = "personal_access_token"

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

