import threading
from TCPServer import TCPServer
from OutageManager import OutageManager
from FlaskAPI import FlaskAPI
from UsageSimulator import UsageSimulator

def main():
    tcp_server = TCPServer()
    try:
        tcp_server.start()

        print("Waiting for simulation to start...")
        while True:
            msg = tcp_server.receive()
            if msg == "simulation_started":
                print("Simulation started confirmed by client.")
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

