import threading
from TCPServer import TCPServer
from OutageManager import OutageManager
from FlaskAPI import FlaskAPI
from UsageSimulator import UsageSimulator

# # TCP Connection to MATLAB server
# SERVER_IP = '127.0.0.1'
# SERVER_PORT = 54320

# def main():
#     tcp_client = TCPServer(SERVER_IP, SERVER_PORT)
#     try:
#         response = tcp_client.connect()
#         if response != "simulation_started":
#             print(f"Unexpected response: {response}")
#             return

#         print("MATLAB simulation has started.")

#         outage_manager = OutageManager(tcp_client)
#         simulator = UsageSimulator(tcp_client)
#         flask_api = FlaskAPI(outage_manager, tcp_client)

#         threading.Thread(target=simulator.run, daemon=True).start()
#         flask_api.run()

#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         tcp_client.close()

# main()

def main():
    tcp_server = TCPServer()
    try:
        tcp_server.start()

        print("🕓 Waiting for simulation to start...")
        while True:
            msg = tcp_server.receive()
            if msg == "simulation_started":
                print("✅ Simulation started confirmed by client.")
                break

        outage_manager = OutageManager(tcp_server)
        simulator = UsageSimulator(tcp_server)
        flask_api = FlaskAPI(outage_manager, tcp_server)

        threading.Thread(target=simulator.run, daemon=True).start()
        flask_api.run()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        tcp_server.close()

main()

