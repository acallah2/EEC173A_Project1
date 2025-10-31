import json
import socket

data = {
    "server_ip": "127.0.0.1",
    "server_port": 7000,
    "message": "ping"
}

jsonData = json.dumps(data)

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8000

# Create a TCP socket and connect to the proxy server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((PROXY_HOST, PROXY_PORT))
    s.sendall(jsonData.encode('utf-8'))

    receivedData = s.recv(4096)

    print("Received: ", receivedData.decode('utf-8'))