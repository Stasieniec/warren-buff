# utils/state_utils.py
import os
import json
import time
import threading
import logging
import alpaca_trade_api as tradeapi

# Configure logging to use bot.log
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Create a FileHandler and add it to the logger
file_handler = logging.FileHandler('logs/bot.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))

# Add the handler to the root logger
logger = logging.getLogger()
logger.addHandler(file_handler)

# Optional: Add a StreamHandler to log to console as well, which helps while debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))
logger.addHandler(console_handler)


# Function to determine if it is time to back up the state (e.g., every hour)
last_backup_time = None
BACKUP_INTERVAL = 3600  # 1 hour in seconds
backup_lock = threading.Lock()

# Function to determine if it is time to back up the state
def time_to_backup():
    global last_backup_time
    with backup_lock:
        current_time = time.time()
        if last_backup_time is None or (current_time - last_backup_time) > BACKUP_INTERVAL:
            last_backup_time = current_time
            logging.info("Time to backup state.")
            return True
    return False

# Function to back up the state
def backup_state(running_modules):
    with backup_lock:
        # Create a backup directory if it doesn't exist
        if not os.path.exists('backups'):
            os.makedirs('backups')

        # Serialize the running modules state
        backup_data = {
            'timestamp': time.time(),
            'running_modules': list(running_modules.keys())
        }

        # Write the backup to a file
        backup_filename = f"backups/state_backup_{int(time.time())}.json"
        with open(backup_filename, 'w') as backup_file:
            json.dump(backup_data, backup_file, indent=4)
        logging.info(f"State backed up to {backup_filename}.")
