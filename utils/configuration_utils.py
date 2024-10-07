# utils/configuration_utils.py
import json
import os
import time
import threading
import logging

# Configure logging to use bot.log
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Track the last modification time of the config file
last_modified_time = None
config_lock = threading.Lock()

# Function to check if the configuration file has changed
def config_has_changed():
    global last_modified_time
    with config_lock:
        current_modified_time = os.path.getmtime('config/config.json')
        if last_modified_time is None or current_modified_time > last_modified_time:
            last_modified_time = current_modified_time
            logging.info("Configuration file has changed.")
            return True
    return False

# Function to reload the configuration
def reload_configuration():
    with open('config/config.json', 'r') as config_file:
        config = json.load(config_file)
        logging.info("Configuration file reloaded.")
        return config


