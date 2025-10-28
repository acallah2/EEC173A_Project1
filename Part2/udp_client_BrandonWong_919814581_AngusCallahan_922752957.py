import socket
import time

# server settings
SERVER_HOST = 'localhost'
SERVER_PORT = 5001
BUFFER_SIZE = 65507  # max UDP packet size
DATA_TO_SEND = 100 * 1000000  # send 100 MB

def main():
    # make a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5)  # timeout after 5 seconds
    
    print(f"Connecting to server at {SERVER_HOST}:{SERVER_PORT}")
    
    # send START message to server
    client_socket.sendto("START".encode(), (SERVER_HOST, SERVER_PORT))
    
    # wait for server to respond
    try:
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        if response.decode() == "READY":
            print("Server is ready. Starting data transfer...")
    except socket.timeout:
        print("Error: Server didn't respond. Is it running?")
        client_socket.close()
        return
    
    # now send the actual data
    bytes_sent = 0
    packet_size = BUFFER_SIZE - 100  # leave some room just in case
    data_packet = b'X' * packet_size  # fill packet with X's
    
    start_time = time.time()
    
    while bytes_sent < DATA_TO_SEND:
        remaining = DATA_TO_SEND - bytes_sent
        
        if remaining < packet_size:
            # last packet might be smaller
            data_packet = b'X' * remaining
        
        client_socket.sendto(data_packet, (SERVER_HOST, SERVER_PORT))
        bytes_sent += len(data_packet)
        
        # print progress every 10 MB so we know it's working
        if bytes_sent % (10 * 1000000) < packet_size:
            print(f"Sent: {bytes_sent / 1000000:.2f} MB / {DATA_TO_SEND / 1000000:.2f} MB")
    
    end_time = time.time()
    
    # tell server we're done
    client_socket.sendto("END".encode(), (SERVER_HOST, SERVER_PORT))
    
    print(f"\nData transfer complete!")
    print(f"Total data sent: {bytes_sent / 1000000:.2f} MB")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # get throughput from server
    print("\nWaiting for throughput measurement from server...")
    try:
        throughput_data, _ = client_socket.recvfrom(BUFFER_SIZE)
        throughput_mbps = float(throughput_data.decode())
        print(f"\n{'='*50}")
        print(f"Throughput (from server): {throughput_mbps:.2f} Mbps")
        print(f"{'='*50}")
    except socket.timeout:
        print("Error: Didn't get throughput from server.")
    
    client_socket.close()

if __name__ == "__main__":
    main()
