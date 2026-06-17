from datetime import timedelta

DOMAIN = "samsung_dishwasher"
CONF_PAT = "personal_access_token"
CONF_DEVICE_ID = "device_id"

UPDATE_INTERVAL = timedelta(seconds=60)

# Capabilities
CAP_WASHING_COURSE = "samsungce.dishwasherWashingCourse"
CAP_OPERATING_STATE = "dishwasherOperatingState"
CAP_DISHWASHER_OPERATION = "samsungce.dishwasherOperation"
CAP_REMOTE_CONTROL = "remoteControlStatus"
CAP_SWITCH = "switch"
CAP_WASHING_OPTIONS = "samsungce.dishwasherWashingOptions"
