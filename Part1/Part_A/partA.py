import dpkt
import collections
import socket
import os
import datetime

def pcapAnalyzer(directory):
    results = {}
    
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path) and path.endswith('.pcap'):
            protocolCounter = collections.Counter()
            ipTimeStamps = []

            with open(path, 'rb') as f:
                pcap = dpkt.pcap.Reader(f)

                for timestamp, buf in pcap:
                    eth = dpkt.ethernet.Ethernet(buf)
                    if isinstance(eth.data, dpkt.ip.IP):
                        ip = eth.data

                        dstIp = socket.inet_ntoa(ip.dst)
                        ts = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        ipTimeStamps.append((dstIp, ts))

                        if isinstance(ip.data, dpkt.icmp.ICMP):
                            protocolCounter['ICMP'] += 1
                        
                        elif isinstance(ip.data, dpkt.tcp.TCP):
                            tcp = ip.data
                            
                            if tcp.dport == 80 or tcp.sport == 80:
                                protocolCounter['TCP_HTTP'] += 1
                            elif tcp.dport == 443 or tcp.sport == 443:
                                protocolCounter['TCP_HTTPS'] += 1
                            elif tcp.dport == 21 or tcp.sport == 21:
                                protocolCounter['FTP'] += 1
                            elif tcp.dport == 22 or tcp.sport == 22:
                                protocolCounter['SSH'] += 1
                            elif tcp.dport == 25 or tcp.sport == 25:
                                protocolCounter['SMTP'] += 1
                            elif tcp.dport == 53 or tcp.sport == 53:
                                protocolCounter['DNS'] += 1
                            else:
                                protocolCounter['TCP_Other'] += 1
                        
                        elif isinstance(ip.data, dpkt.udp.UDP):
                            udp = ip.data

                            if udp.dport == 80 or udp.sport == 80:
                                protocolCounter['UDP_HTTP'] += 1
                            elif udp.dport == 443 or udp.sport == 443:
                                protocolCounter['UDP_HTTPS'] += 1
                            elif udp.dport == 53 or udp.sport == 53:
                                protocolCounter['DNS'] += 1
                            elif udp.dport == 4500 or udp.sport == 4500:
                                protocolCounter['ESP'] += 1
                            else:
                                protocolCounter['UDP_Other'] += 1
                                    
            results[name] = {'protocols': protocolCounter, 'ipTimeStamps': ipTimeStamps}

    return results

if __name__ == "__main__":
    directory = r"c:\Users\Angus\Desktop\EEC_173A\Project1\Part1\Part_A"
    results = pcapAnalyzer(directory)

    print("Common Destination IPs:")
    for pcapFile, data in results.items():
        print(f"File: {pcapFile}")

        ipCounter = collections.Counter([dstIp for dstIp, ts in data['ipTimeStamps']])
        for ip, count in ipCounter.most_common(3):
            timestamp = next(ts for dstIp, ts in data['ipTimeStamps'] if dstIp == ip)
            print(f"  {ip}: {count} packets (first seen: {timestamp})")

    print("Protocol counts:")
    for pcapFile, data in results.items():
        print(f"File: {pcapFile}")
        for protocol, count in data['protocols'].items():
            print(f"{protocol}: {count}")