import socket

class TCPClient:
    def __init__(self, server_ip, server_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.server_port = server_port

    def connect(self):
        self.sock.connect((self.server_ip, self.server_port))
        return self.sock.recv(1024).decode('utf-8')

    def send_command(self, msg_type, data=""):
        message = f"{msg_type}|{data}" if data else msg_type
        self.sock.send(message.encode('utf-8'))
        print(f"Sent: {message}")

    def receive(self):
        return self.sock.recv(1024).decode('utf-8')

    def close(self):
        self.sock.close()
