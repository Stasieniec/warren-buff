from flask import Flask, request, jsonify
app = Flask(__name__)


@app.route('/start_module', methods=['POST'])
def start_module():
    data = request.get_json()
    module_name = data['module_name']
    mode = data.get('mode', 'test')
    # Code to start the module
    return jsonify({'status': 'Module started', 'module': module_name, 'mode': mode})


@app.route('/stop_module', methods=['POST'])
def stop_module():
    data = request.get_json()
    module_name = data['module_name']
    # Code to stop the module
    return jsonify({'status': 'Module stopped', 'module': module_name})

@app.route('/status', methods=['GET'])
def status():
    # Code to retrieve status
    return jsonify({'status': 'Bot is running', 'modules': list_of_running_modules})
