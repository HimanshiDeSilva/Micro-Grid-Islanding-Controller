import socket
import threading

class TCPServer:

    def __init__(self, host='0.0.0.0', port=54320):
        self.host = host
        self.port = port
        self.client_socket = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"📡 TCP Server started at {self.host}:{self.port}. Waiting for MATLAB client...")
        self.client_socket, addr = self.server_socket.accept()
        print(f"✅ MATLAB client connected from {addr}.")

    def send(self, message):
        if self.client_socket:
            self.client_socket.send(message.encode('utf-8'))
            print(f"Sent to MATLAB: {message}")

    def receive(self):
        if self.client_socket:
            return self.client_socket.recv(1024).decode('utf-8')

    def close(self):
        if self.client_socket:
            self.client_socket.close()
        self.server_socket.close()