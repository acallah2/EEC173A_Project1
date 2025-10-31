import json
import socket

HOST = '127.0.0.1'
PORT = 8000

blockList = ["10.0.0.1", "203.51.100.23", "192.168.1.1"]

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))

    server_socket.listen()

    # Continuously accept and handle incoming client connections
    while True:
        client_socket, (client_addr, client_port) = server_socket.accept()
        dataReceived = client_socket.recv(4096)
        decodedData = dataReceived.decode('utf-8')
        jsonData = json.loads(decodedData)

        SERVER_HOST = jsonData["server_ip"]
        SERVER_PORT = jsonData["server_port"]
        message = jsonData["message"]
        
        # Check if the requested server IP is in the block list
        if SERVER_HOST in blockList:
            print(f"Blocked request to {SERVER_HOST} from {client_addr}:{client_port}")
            client_socket.sendall(f"Error: Access to {SERVER_HOST} is blocked".encode('utf-8'))
            continue

        print("Forwarding message to server:", SERVER_HOST, SERVER_PORT)
        print("Message content:", message)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as forward_socket:
            forward_socket.connect((SERVER_HOST, SERVER_PORT))
            forward_socket.sendall(message.encode('utf-8'))

            responseData = forward_socket.recv(4096)

            client_socket.sendall(responseData)
            client_socket.close()
