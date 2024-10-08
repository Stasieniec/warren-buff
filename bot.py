# bot.py

import threading
from flask import Flask, request, jsonify
import logging
import importlib
import os
import json
import time
from utils import configuration_utils, state_utils
import threading
from utils.alpaca_utils import save_module_state
from logging.handlers import RotatingFileHandler
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Global variables to track running modules
running_modules = {}
module_threads = {}
module_locks = threading.Lock()

# Configure logging to use bot.log with log rotation
log_file_path = 'logs/bot.log'
log_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
rotating_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3)
rotating_handler.setFormatter(log_formatter)
rotating_handler.setLevel(logging.INFO)

# Add the handler to the root logger
logger = logging.getLogger()
logger.addHandler(rotating_handler)
logger.setLevel(logging.INFO)

# Optional: Add a StreamHandler to log to console as well, which helps while debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# Ensure database directory and connection
if not os.path.exists('database'):
    os.makedirs('database')

conn = sqlite3.connect('database/trading_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables for module states and action history if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS module_state (
    module_name TEXT PRIMARY KEY,
    max_money_per_day REAL,
    max_money_per_transaction REAL,
    history TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_name TEXT,
    action TEXT,
    symbol TEXT,
    quantity INTEGER,
    price REAL,
    timestamp REAL
)
''')
conn.commit()

# Load configuration
def load_configuration():
    with open('config/config.json', 'r') as config_file:
        return json.load(config_file)

config = load_configuration()

# Flask route to start a module
@app.route('/start_module', methods=['POST'])
def start_module():
    data = request.get_json()
    module_name = data['module_name']
    mode = data.get('mode', 'test')
    params = data.get('params', {})

    with module_locks:
        if module_name in running_modules:
            return jsonify({'status': 'Module already running', 'module': module_name}), 400

        try:
            # Import the module dynamically
            module = importlib.import_module(f"modules.{module_name}")

            # Create a stop event
            stop_event = threading.Event()

            # Set up initial module state
            module_state = {
                "max_money_per_day": params.get("max_money_per_day", 1000),
                "max_money_per_transaction": params.get("max_money_per_transaction", 500),
                "history": []
            }
            save_module_state(module_name, module_state)

            # Insert or update module state in the database
            cursor.execute('''
                INSERT OR REPLACE INTO module_state (module_name, max_money_per_day, max_money_per_transaction, history)
                VALUES (?, ?, ?, ?)
            ''', (module_name, module_state['max_money_per_day'], module_state['max_money_per_transaction'], json.dumps(module_state['history'])))
            conn.commit()

            # Start the module in a new thread
            module_thread = threading.Thread(target=module.run, args=(mode, stop_event, params))
            module_thread.start()

            # Keep track of the module and its thread
            running_modules[module_name] = stop_event
            module_threads[module_name] = module_thread

            logging.info(f"Started module {module_name} in {mode} mode")
            return jsonify({'status': 'Module started', 'module': module_name, 'mode': mode}), 200

        except Exception as e:
            logging.error(f"Error starting module {module_name}: {str(e)}")
            return jsonify({'status': 'Error', 'message': str(e)}), 500

# Flask route to stop a module
@app.route('/stop_module', methods=['POST'])
def stop_module():
    data = request.get_json()
    module_name = data['module_name']

    with module_locks:
        if module_name not in running_modules:
            return jsonify({'status': 'Module not running', 'module': module_name}), 400

        # Signal the module to stop
        running_modules[module_name].set()
        module_threads[module_name].join()

        # Remove the module from tracking
        del running_modules[module_name]
        del module_threads[module_name]

        logging.info(f"Stopped module {module_name}")
        return jsonify({'status': 'Module stopped', 'module': module_name}), 200

# Flask route to get the status
@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'Bot is running',
        'running_modules': list(running_modules.keys())
    }), 200

def start_module_internal(module_name, config):
    mode = config.get('mode', 'test')
    params = config.get('params', {})
    start_module_data = {
        'module_name': module_name,
        'mode': mode,
        'params': params
    }
    start_module()

def run_flask_app():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Ensure the logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # Allows the program to exit even if this thread is running
    flask_thread.start()

    logging.info('Bot started')

    try:
        # Main bot loop
        while True:
            # Check health of running modules
            with module_locks:
                for module_name, thread in module_threads.items():
                    if not thread.is_alive():
                        logging.error(f"Module {module_name} has stopped unexpectedly. Restarting...")
                        start_module_internal(module_name, config)

            # Check for configuration updates
            if configuration_utils.config_has_changed():
                config = load_configuration()
                logging.info("Configuration reloaded.")

            # Save state periodically
            if state_utils.time_to_backup():
                state_utils.backup_state(running_modules)
                logging.info("State backed up.")

            # Send a heartbeat signal for monitoring
            logging.info("Heartbeat: Bot is running smoothly...")

            # Sleep for a short while before next iteration
            time.sleep(60)

    except KeyboardInterrupt:
        logging.info('Bot stopped by user')
    finally:
        conn.close()