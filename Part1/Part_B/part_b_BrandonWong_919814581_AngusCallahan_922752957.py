import dpkt
import socket
import os
from urllib.parse import urlparse, parse_qs

script_dir = os.path.dirname(os.path.abspath(__file__))
pcap_path = os.path.join(script_dir, "PCAP1_1.pcap")

def format_ipv6(addr):
    return socket.inet_ntop(socket.AF_INET6, addr)

f = open(pcap_path, 'rb')
pcap = dpkt.pcap.Reader(f)

for timestamp, buf in pcap:
    try:
        eth = dpkt.ethernet.Ethernet(buf)
        
        # All HTTP traffic is IPv6 TCP on port 80
        if isinstance(eth.data, dpkt.ip6.IP6):
            ip = eth.data
            
            if isinstance(ip.data, dpkt.tcp.TCP):
                tcp = ip.data
                
                if (tcp.dport == 80 or tcp.sport == 80) and len(tcp.data) > 0:
                    
                    try:
                        request = dpkt.http.Request(tcp.data)
                        
                        # Print HTTP request details
                        print("="*60)
                        print(f"HTTP Request: {request.method} {request.uri} HTTP/{request.version}")
                        print(f"Source: [{format_ipv6(ip.src)}]:{tcp.sport}")
                        print(f"Destination: [{format_ipv6(ip.dst)}]:{tcp.dport}")
                        print()
                        
                        parsed_uri = urlparse(request.uri)
                        print(f"Request Method: {request.method}")
                        print(f"Request URI Path: {parsed_uri.path}")
                        
                        if parsed_uri.query:
                            print(f"Request URI Query: {parsed_uri.query}")
                            query_params = parse_qs(parsed_uri.query)
                            for param, value in query_params.items():
                                print(f"  Request URI Query Parameter: {param} = {value[0]}")
                        
                        print(f"Request Version: HTTP/{request.version}")
                        print()
                        
                        for header, value in request.headers.items():
                            print(f"{header}: {value}")
                        
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
