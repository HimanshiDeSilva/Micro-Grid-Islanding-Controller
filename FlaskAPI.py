import time
from flask_cors import CORS
from flask import Flask, jsonify, request


class FlaskAPI:
    def __init__(self, outage_manager, tcp_client):
        self.app = Flask(__name__)
        CORS(self.app)
        self.outage_manager = outage_manager
        self.tcp_client = tcp_client
        self.device_map = {
            "ATH-SMP-TAS-50CF5C-3932": "SM01",
            "ATH-SMP-TAS-50D634-5684": "SM02",
            "ATH-SMP-TAS-5097E0-6112": "SM03",
            #"ATH-SMP-TAS-509574-5492": "SM05",
            #"ATH-SMP-TAS-50D634-5689": "SM06",
        }
        self.register_routes()

    def register_routes(self):
        @self.app.route('/disconnect_meters', methods=['PUT'])
        def disconnect_meters():
            if not self.outage_manager.outage_active:
                return jsonify({"error": "Outage not active"}), 400
            try:
                meters = request.json.get("smartMeters", [])
                print(f"Disconnecting meters: {meters}")
                for m in meters:
                    sm_name = self.device_map.get(m.upper())
                    if sm_name:
                        self.tcp_client.send_command("DISCONNECT", sm_name)
                        print(f"Disconnecting {sm_name}")
                    else:
                        print(f"Unknown device ID: {m} — not in device_map")
                    time.sleep(1)
                return jsonify({"status": "Smart meters disconnected"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            
        @self.app.route('/reconnect_meters', methods=['PUT'])
        def reconnect_meters():
            if self.outage_manager.outage_active:
                return jsonify({"error": "Outage not active"}), 400
            try:
                meters = request.json.get("smartMeters", [])
                print(f"Reconnecting meters: {meters}")
                for m in meters:
                    sm_name = self.device_map.get(m.upper())  # Look up human-readable name
                    if sm_name:
                        self.tcp_client.send_command("CONNECT", sm_name)
                        print(f"Reconnecting {sm_name}")  
                    else:
                        print(f"Unknown device ID: {m} — not in device_map")
                    time.sleep(1)
                return jsonify({"status": "Smart meters reconnected"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/toggle', methods=['POST'])
        def toggle():
            data = request.get_json()
            power_state = data.get("power")

            print(f"Received toggle request: {power_state}")

            if power_state == "OFF":
                self.outage_manager.start_outage()
            elif power_state == "ON":
                self.outage_manager.end_outage()
            else:
                return jsonify({"error": "Invalid power state"}), 400

            return jsonify({"status": "Command executed"}), 200
    def run(self):
        self.app.run(host='0.0.0.0', port=5000)
