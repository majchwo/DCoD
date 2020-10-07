#! /usr/bin/env python3

import flask
import requests
from flask_restful import Resource, Api
import yaml
import argparse
import paramiko
from time import sleep
import json

app = flask.Flask(__name__)

def parse_args():
    parser=argparse.ArgumentParser()
    
    required_args = parser.add_argument_group('required arhuments')
    
    required_args.add_argument('-f', '--filename', metavar='Filename', type=str, dest='filename', required=True)
    required_args.add_argument('-p', '--port', metavar='Port', type=str, dest='port', required=True)
    
    args=parser.parse_args()
    return args


def get_pw_from_file():
        with open("passwordfile", "r") as pw_file:
            return pw_file.readline()


def get_proxy_ip(hosts):
       
    proxies = {} 
    for host in hosts:
        proxies[host] ="Cannot connect to proxy !"
        try:
            shell = paramiko.SSHClient()
            shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            shell.connect(host,22,hosts[host]["user"],hosts[host]["password"], timeout=10)
            if hosts[host]["os"] == 'windows':
                
                for i in range(1,10): 
                    stdin, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\Virtualbox\VBoxManage\" guestcontrol \"\"virtnet_proxy\"\" run --exe \"\"/home/virtnet/show_ip.sh\"\" --username virtnet --password "+ get_pw_from_file()+"\"")
                    exit_status = stdout.channel.recv_exit_status()         
               
                    if exit_status == 0:
                        proxy_ip=stdout.readlines()
                        if proxy_ip[0].strip('\n') == "":
                            sleep(1)
                            continue
                            
                       
                        proxies[host] = proxy_ip[0].strip('\n')
                        shell.close()
                        break
                        
                    else:
                        print("Error", exit_status)

                        print(host, " : ", stderr.read())
            elif  hosts[host]["os"] == "linux": 
               
                for i in range(1,10):
                              
                    _, stdout, stderr = shell.exec_command("VBoxManage guestcontrol \"virtnet_proxy\" run --exe \"/home/virtnet/show_ip.sh\" --username virtnet --password "+ get_pw_from_file())
                    exit_status = stdout.channel.recv_exit_status()         
                    if exit_status == 0:
                        proxy_ip=stdout.readlines()
                        if proxy_ip[0].strip('\n') == "":
                            sleep(1)
                            continue
                       
                        proxies[host] = proxy_ip[0].strip('\n')
                        shell.close()
                        break
        except Exception as e:
            print("ERROR: "+ host)
            shell.close()
    return proxies

def get_info(proxies):
    proxies_info = {}
    for host in proxies:
        
        proxies_info["HOST " + host] = {}
        try:
            if proxies[host] != "Cannot connect to proxy !":
                r = requests.get('http://' + proxies[host]+":80", timeout=10)
                if r != "":
                    proxies_info["HOST " + host]["PROXY " + proxies[host]] = {}
                    proxies_info["HOST " + host]["PROXY " + proxies[host]] = r.json()
                else:
                    proxies_info["HOST " + host]["PROXY " + proxies[host]] = {}
                    proxies_info["HOST " + host]["PROXY " + proxies[host]] = "Cannot connect to proxy !"
            else:
                proxies_info["HOST " + host]["PROXY " + proxies[host]] = {}
                proxies_info["HOST " + host]["PROXY " + proxies[host]] = "Cannot connect to proxy !"
        except requests.exceptions.RequestException as e:
            return {host: {"ERROR":" Cannot connect to proxy, check host and/or proxy connection"}}
    
        
    return proxies_info


def parse_hosts_file(filename):
    ssh_hosts={}
    with open(filename,"r") as hosts_file:
        data = yaml.load(hosts_file, Loader=yaml.BaseLoader)
        for section in data:
            if section=="hosts":
                for hosts in data[section]:
                    ssh_hosts[hosts]=data[section][hosts]
  
    return ssh_hosts    

args=parse_args()
    
hosts = parse_hosts_file(args.filename)
proxies = get_proxy_ip(hosts)
print(proxies)
@app.route("/status")
def get():
        return flask.jsonify(get_info(proxies))


if __name__ == "__main__":
    
  
    app.run("0.0.0.0",port=str(args.port))
    