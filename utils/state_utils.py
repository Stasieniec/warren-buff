# utils/state_utils.py
import os
import json
import time
import threading
import logging

# Configure logging to use bot.log
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

log_handler = logging.FileHandler('logs/bot.log')
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))
log_handler.flush = True

logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# Function to determine if it is time to back up the state (e.g., every hour)
last_backup_time = None
BACKUP_INTERVAL = 3600  # 1 hour in seconds
backup_lock = threading.Lock()

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