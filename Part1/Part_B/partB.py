import dpkt
import socket
import os
from urllib.parse import urlparse, parse_qs

# Get the path to the PCAP file
script_dir = os.path.dirname(os.path.abspath(__file__))
pcap_path = os.path.join(script_dir, "PCAP1_1.pcap")

def format_ipv6(addr):
    # Convert IPv6 bytes to readable format
    return socket.inet_ntop(socket.AF_INET6, addr)

# Open and read the pcap file
f = open(pcap_path, 'rb')
pcap = dpkt.pcap.Reader(f)

for timestamp, buf in pcap:
    try:
        eth = dpkt.ethernet.Ethernet(buf)
        
        # Looking for IPv6 packets
        if isinstance(eth.data, dpkt.ip6.IP6):
            ip = eth.data
            
            # Check if it's TCP
            if isinstance(ip.data, dpkt.tcp.TCP):
                tcp = ip.data
                
                # Filter for HTTP traffic on port 80
                if (tcp.dport == 80 or tcp.sport == 80) and len(tcp.data) > 0:
                    
                    # Parse HTTP request if possible
                    try:
                        request = dpkt.http.Request(tcp.data)
                        
                        # Print request info
                        print("="*60)
                        print(f"HTTP Request: {request.method} {request.uri} HTTP/{request.version}")
                        print(f"Source: [{format_ipv6(ip.src)}]:{tcp.sport}")
                        print(f"Destination: [{format_ipv6(ip.dst)}]:{tcp.dport}")
                        print()
                        
                        # Break down the URI
                        parsed_uri = urlparse(request.uri)
                        print(f"Request Method: {request.method}")
                        print(f"Request URI Path: {parsed_uri.path}")
                        
                        # Check for query parameters
                        if parsed_uri.query:
                            print(f"Request URI Query: {parsed_uri.query}")
                            query_params = parse_qs(parsed_uri.query)
                            for param, value in query_params.items():
                                print(f"  Request URI Query Parameter: {param} = {value[0]}")
                        
                        print(f"Request Version: HTTP/{request.version}")
                        print()
                        
                        # Display headers
                        for header, value in request.headers.items():
                            print(f"{header}: {value}")
                        
                        # Show body if it exists
                        if request.body:
                            print(f"\nBody: {request.body.decode('utf-8', errors='ignore')}")
                        
                        print("="*60)
                        print()
                        
                    except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
                        # Skip if not a valid HTTP request
                        pass
                        
    except Exception as e:
        # Skip packets that cause error
        continue

f.close()
