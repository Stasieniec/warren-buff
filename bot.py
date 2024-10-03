# bot.py

import threading
from flask import Flask, request, jsonify
import logging
import importlib
import os
import json

# Initialize Flask app
app = Flask(__name__)

# Global variables to track running modules
running_modules = {}
module_threads = {}

# Configure logging
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Load configuration
with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

# Flask route to start a module
@app.route('/start_module', methods=['POST'])
def start_module():
    data = request.get_json()
    module_name = data['module_name']
    mode = data.get('mode', 'test')
    params = data.get('params', {})

    if module_name in running_modules:
        return jsonify({'status': 'Module already running', 'module': module_name}), 400

    try:
        # Import the module dynamically
        module = importlib.import_module(f"modules.{module_name}")

        # Create a stop event
        stop_event = threading.Event()

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
            # You can add any periodic tasks here
            pass
    except KeyboardInterrupt:
        logging.info('Bot stopped by user')
