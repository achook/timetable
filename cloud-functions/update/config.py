from secrets import get_secret
from configcatclient import create_client as configcat_create

configcat_key = get_secret("CONFIGCAT_KEY")
configcat_client = configcat_create(configcat_key)

def get_config(key: str):
    return configcat_client.get_value(key, '')
