#!/usr/bin/env python3

import ssh_conn.ssh as connections
import time
import argparse
from threading import Thread
import logging



def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('command', type=str, help='action to perform', metavar='Action')
    required_args = parser.add_argument_group('required arhuments')
    parser.add_argument('--vni', type=int, help='VxLAN VNI Number', metavar='VNI', dest='vni', required=False)
    required_args.add_argument('-f', '--filename', metavar='Filename', type=str, dest='filename', required=True)
    args=parser.parse_args()
    return args


def create_virtual_network(host, hosts, vni):
    host.add_virtnet(str(args.vni))
    for other_host in hosts:
        if other_host.ip != host.ip:
            host.append_ip_to_proxy_fdb(str(vni), other_host.proxy_ip)

def delete_virtual_network(host, hosts, vni):
    if host.check_if_network_exists(vni) == True:
        for other_host in hosts:
            if other_host.ip != host.ip:
                host.delete_fdb_entry(str(args.vni), other_host.proxy_ip)
        host.del_virtnet(str(args.vni))
def reset_iface(host,vni):
    host.reset_iface(vni)

def stop_proxies(host):
    host.stop_proxy()

if __name__=='__main__':
    print("\n\nCreated by Wojciech Majcher, Computer Networks and Services Division WUT\n\n")
    hosts = []
    args=parse_args()
    host_info = connections.parse_hosts_file(args.filename)
    for host in host_info:
        hosts.append(connections.Host(host, host_info[host]['os'], host_info[host]['user'], host_info[host]['password']))
    
    if args.command=='create' and (args.vni > 0 and args.vni < 16777215):
        
        for host in hosts:
            info = host.check_ssh_connection()
            if info == False:
                print("Failed to connect to host : " + host.ip + " removing it from hosts list...")
                hosts.remove(host)
        
        threads=[]
        for host in hosts:
            threads.append(Thread(target=host.start_proxy))
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        
        threads.clear()
        for host in hosts:
            threads.append(Thread(target=host.get_proxy_ip))
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        threads.clear()
        for host in hosts:
            threads.append(Thread(target=create_virtual_network, args=(host, hosts, args.vni)))
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        threads.clear()
    elif args.command=='remove' and (args.vni > 0 and args.vni < 16777215):
        
        for host in hosts:
            info = host.check_ssh_connection()
            if info == False:
                print("Failed to connect to host : " + host.ip + " removing it from hosts list...")
                hosts.remove(host)
        
        threads=[]
        for host in hosts:
            threads.append(Thread(target=host.get_proxy_ip))
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        threads.clear()
        for host in hosts:
            threads.append(Thread(target=delete_virtual_network, args=(host, hosts, args.vni)))
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        threads.clear()
    elif args.command=='reset' and (args.vni > 0 and args.vni < 16777215):
       
        threads=[]
        
        for host in hosts:
            threads.append(Thread(target=host.get_proxy_ip))
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        threads.clear()
        for host in hosts:
            threads.append(Thread(target=reset_iface, args=(host, args.vni)))
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        threads.clear()
    elif args.command=='stop-proxies':
       
        threads=[]
        
        
        for host in hosts:
            threads.append(Thread(target=stop_proxies, args=(host,)))
        for x in threads:
            x.start()
        for x in threads:
            x.join()
        threads.clear()

    

    ##TODO: możliwość zmiany hasła do maszyn virtualnych