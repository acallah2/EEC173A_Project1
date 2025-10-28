import socket
import time

# server settings
SERVER_HOST = 'localhost'
SERVER_PORT = 5001
BUFFER_SIZE = 65507  # max UDP packet size

def main():
    # make a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    
    print(f"UDP Server listening on {SERVER_HOST}:{SERVER_PORT}")
    print("Waiting for client connection...")
    
    # wait for START message from client
    data, client_address = server_socket.recvfrom(BUFFER_SIZE)
    if data.decode() == "START":
        print(f"Client connected: {client_address}")
        server_socket.sendto("READY".encode(), client_address)
    
    # receive data and calculate throughput
    total_bytes_received = 0
    start_time = time.time()
    
    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        
        # check if client is done sending
        if data.decode() == "END":
            end_time = time.time()
            print("Data transfer complete!")
            break
        
        total_bytes_received += len(data)
    
    # calculate throughput in megabits per second
    time_taken = end_time - start_time
    throughput_mbps = (total_bytes_received * 8) / (time_taken * 1000000)  # Mbps
    throughput_MBps = total_bytes_received / (time_taken * 1000000)  # MBps
    
    print(f"\nServer Statistics:")
    print(f"Total data received: {total_bytes_received / 1000000:.2f} MB")
    print(f"Time taken: {time_taken:.4f} seconds")
    print(f"Throughput: {throughput_mbps:.2f} Mbps ({throughput_MBps:.2f} MBps)")
    
    # send throughput back to client
    throughput_message = f"{throughput_mbps:.2f}"
    server_socket.sendto(throughput_message.encode(), client_address)
    
    print("\nThroughput sent to client. Server shutting down.")
    server_socket.close()

if __name__ == "__main__":
    main()
