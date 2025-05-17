import socket
import time

class TCPClient:
    def __init__(self, server_ip, server_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.server_port = server_port

    def connect(self, retries=30, delay=2):
        attempt = 0
        while attempt < retries:
            try:
                self.sock.connect((self.server_ip, self.server_port))
                print("✅ Connected to MATLAB TCP server.")
                return self.sock.recv(1024).decode('utf-8')
            except (ConnectionRefusedError, OSError):
                print(f"⏳ Waiting for MATLAB to start TCP server... Retry {attempt + 1}/{retries}")
                time.sleep(delay)
                attempt += 1
        raise ConnectionError("❌ Could not connect to MATLAB after multiple attempts.")

    def send_command(self, msg_type, data=""):
        message = f"{msg_type}|{data}" if data else msg_type
        self.sock.send(message.encode('utf-8'))
        print(f"Sent: {message}")

    def receive(self):
        return self.sock.recv(1024).decode('utf-8')

    def close(self):
        self.sock.close()
