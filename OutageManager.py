import requests
from datetime import datetime, timezone

# ovst management url
JAVA_NOTIFY_URL = "http://localhost:8080/api/"
current_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

auth_data = {
    "username": "oversight_admin",
    "password": "welCome1/",
    "rememberMe": True,
    "serviceProvider": "CEB"
}

outage_id = ""

class OutageManager:
    def __init__(self, tcp_client):
        self.tcp_client = tcp_client
        self.outage_active = False

    def start_outage(self):
        self.tcp_client.send_command("START_OUTAGE")
        response = self.tcp_client.receive()
        if response == "switch_off_success":
            self.outage_active = True
            print("Outage successfully started.")
            self.notify_java("started")
        else:
            print(f"Unexpected response: {response}")

    def end_outage(self):
        self.tcp_client.send_command("END_OUTAGE")
        response = self.tcp_client.receive()
        if response == "outage_ended":
            self.outage_active = False
            print("Outage successfully ended.")
            self.notify_java("ended")
        else:
            print(f"Unexpected response: {response}")

    def notify_java(self, status):
        try:
            if status == "started":
                print("Notifying Java that outage started...")
                auth_response = requests.post(JAVA_NOTIFY_URL + "admin/login", json=auth_data)
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + auth_response.json().get("token")
                }
                create_outage_data = {
                    "startDate": current_time,
                    "supplyStatus": "CAN_PROVIDE_POWER"
                }
                response = requests.post(JAVA_NOTIFY_URL + "transformer/TX-1002/outage/unplanned", headers=headers, json=create_outage_data)
                outage_id = response.json().get("outageId")
                if response.status_code == 200:
                    print("Java notified successfully.")
                else:
                    print(f"Java notification failed: {response.status_code}")
            elif status == "ended":
                print("Notifying Java that outage ended...")
                auth_response = requests.post(JAVA_NOTIFY_URL + "admin/login", json=auth_data)
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + auth_response.json().get("token")
                }
                end_outage_data = {
                    "unplannedOutageId": outage_id,
                }
                response = requests.post(JAVA_NOTIFY_URL + "transformer/TX-1002/outage/unplanned/end", headers=headers, json=end_outage_data)
                if response.status_code == 200:
                    print("Java notified successfully.")
                else:
                    print(f"Java notification failed: {response.status_code}")
        except Exception as e:
            print(f"Error notifying Java: {e}")
