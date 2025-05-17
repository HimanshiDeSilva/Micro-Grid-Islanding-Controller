import requests
import threading
import time
from datetime import datetime, timezone, timedelta

class UsageSimulator:
    def __init__(self, tcp_client):
        self.tcp_client = tcp_client
        self.running = True

        self.device_map = {
            "ATH-SMP-TAS-50CF5C-3932": "SM01",
            "ATH-SMP-TAS-50D634-5684": "SM02",
            "ATH-SMP-TAS-5097E0-6112": "SM03",
            #"ATH-SMP-TAS-509574-5492": "SM05",
            #"ATH-SMP-TAS-50D634-5689": "SM06",
        }

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

    def process_device(self, device_id, sm_id):
        while self.running:
            timestamp = (datetime.now(timezone.utc) - timedelta(seconds=10)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            usage_list = self.fetch_power_data(device_id, timestamp)

            if usage_list:
                last_entry = usage_list[-1]  # Get the most recent (last) entry
                active_power = last_entry['activePower']*100
                reactive_power = last_entry['reactivePower']*100
                payload = f"HS01,{sm_id}, {active_power},{reactive_power}"
                self.tcp_client.send_command("POWER", payload)
                print(f"[{sm_id}] Sent data at {last_entry['timeStamp']}")
            else:
                print(f"[{sm_id}] No data found. Retrying...")

            time.sleep(20)

    def run(self):
        threads = []

        for device_id, sm_id in self.device_map.items():
            t = threading.Thread(target=self.process_device, args=(device_id, sm_id))
            t.start()
            threads.append(t)

        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            self.running = False
            print("Shutting down...")
