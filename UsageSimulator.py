import requests
import threading
import time
from datetime import datetime, timezone, timedelta

class UsageSimulator:
    def __init__(self, tcp_client):
        self.tcp_client = tcp_client
        self.running = True

        # Map of device IDs to local smart meter IDs
        self.device_map = {
            "ATH-SMP-TAS-50CF5C-3932": "SM01",
            "ATH-SMP-TAS-50D634-5684": "SM02",
            "ATH-SMP-TAS-5097E0-6112": "SM03",
        }

        self.data_lock = threading.Lock()
        self.latest_data = {}

    def fetch_power_data(self, device_id, timestamp):
        url = f"http://localhost:8082/api/v1/smart-devices/{device_id}/power-summary"
        params = {'from': timestamp}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("devicePowerUsage", [])
        except Exception as e:
            print(f"Error fetching data for {device_id}: {e}")
            return []

    def update_latest_data(self):
        while self.running:
            timestamp = (datetime.now(timezone.utc) - timedelta(seconds=30)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

            for device_id, sm_id in self.device_map.items():
                print(f"[{sm_id}] Fetching data for {device_id} at {timestamp}")
                usage_list = self.fetch_power_data(device_id, timestamp)

                if usage_list:
                    last_entry = usage_list[-1]
                    active_power = last_entry['activePower'] * 100
                    reactive_power = last_entry['reactivePower'] * 100

                    with self.data_lock:
                        self.latest_data[sm_id] = (active_power, reactive_power, last_entry['timeStamp'])

                    print(f"[{sm_id}] Updated latest data: {active_power}, {reactive_power}")
                else:
                    print(f"[{sm_id}] No data found.")

            time.sleep(10)  # Wait before checking again

    def send_data_periodically(self):
        while self.running:
            time.sleep(20)  # Wait some time before sending to avoid flooding

            payloads = []
            with self.data_lock:
                for sm_id in self.device_map.values():
                    if sm_id in self.latest_data:
                        ap, rp, ts = self.latest_data[sm_id]
                        payload = f"HS01,{sm_id},{ap},{rp}"
                        payloads.append(payload)
                        print(f"[{sm_id}] Prepared payload with timestamp {ts}")
                    else:
                        print(f"[{sm_id}] No data to send yet.")

            for payload in payloads:
                full_message = f"POWER|{payload}"
                self.tcp_client.send_command(full_message)  # Raw sending (no msg_type split)
                print(f"Sent: {full_message}")
                time.sleep(0.1)  # Give Simulink time to process each

    def run(self):
        try:
            # Start data fetching in a separate thread
            data_thread = threading.Thread(target=self.update_latest_data)
            data_thread.start()

            # Keep sending the synchronized data
            self.send_data_periodically()

        except KeyboardInterrupt:
            self.running = False
            print("Shutting down...")
