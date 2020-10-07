#!/usr/bin/env python3

import yaml
import paramiko
import time
import logging


LOG = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(message)s')
handler.setFormatter(formatter)
LOG.addHandler(handler)
LOG.setLevel(logging.INFO)
logging.getLogger("paramiko").setLevel(logging.WARNING)

class Host:
    def __init__(self, ip, os, user, password):
        self.ip = ip
        self.os = os
        self.user = user
        self.password = password 
        self.proxy_ip = ""
    
    def get_pw_from_file(self):
        with open("passwordfile", "r") as pw_file:
            return pw_file.readline()

    def connect_ssh(self):
        try:
                    
            shell = paramiko.SSHClient()
            shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            shell.connect(self.ip,22,self.user,self.password, timeout=10)
            
        except paramiko.AuthenticationException:
            LOG.info(self.ip +": Authentication failed, please verify your credentials")
            result_flag = False
            return result_flag
        except paramiko.SSHException as sshException:
            LOG.info(self.ip +": Could not establish SSH connection: %s" % sshException)
            result_flag = False
            return result_flag
    
        except Exception as e:
            LOG.info(self.ip +": Exception in connecting to the server " )
            
            result_flag = False
            return result_flag
            shell.close()
        return shell
    def check_ssh_connection(self):
        LOG.info("Checking ssh connections...")
        shell = self.connect_ssh()
        if shell == False:
            return False
        try:
            if self.os == "windows":
                _, stdout, stderr = shell.exec_command("ver")
                exit_status = stdout.channel.recv_exit_status()
                if exit_status == 0:
                    
                    LOG.info("SSH_CONN to " + self.ip + " : "+ " ".join(stdout.readlines()))
                    shell.close()
                    return True

                else:
                    LOG.info("SSH_CONN to " + self.ip + " : "+ "Unable to connect")
                    shell.close()
                    return False
            elif self.os == "linux":
                _, stdout, stderr = shell.exec_command("uname -a")
                exit_status = stdout.channel.recv_exit_status()
                if exit_status == 0:
                   
                    LOG.info("SSH_CONN to " + self.ip + " : "+ " ".join(stdout.readlines()))
                    shell.close()
                    return True
                else:
                    LOG.info("SSH_CONN to " + self.ip + " : "+ "Unable to connect")
                    shell.close()
                    return False
                    
        except Exception as e:
            LOG.info("ERROR: "+ self.ip + ":")
            LOG.info(e)
            return False
    def start_proxy(self):
        LOG.info('running proxy VMs')
        shell = self.connect_ssh()
        try:
            if self.os == "windows":

                    _, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\VirtualBox\VBoxManage.exe\" list runningvms\"" )
                    exit_status = stdout.channel.recv_exit_status()
                    lines=stdout.readlines()
                    if  any("virtnet_proxy" in s for s in lines):
                        LOG.info("Proxy already running on host: "+ self.ip)
                    else:
                        _, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\VirtualBox\VBoxManage.exe\" startvm \"\"virtnet_proxy\"\" --type headless\"" )
                        exit_status = stdout.channel.recv_exit_status()         
                        if exit_status == 0:
                            LOG.info("VM_started on host " + self.ip +" "+ " ".join(stdout.readlines()))
                            time.sleep(30)
                        else:
                            LOG.info("Error occured on host "+ self.ip +" "+  " ".join(stderr.readlines()))

                           
                    shell.close()
        
            elif self.os == "linux":
                _, stdout, stderr = shell.exec_command("VBoxManage list runningvms" )
                exit_status = stdout.channel.recv_exit_status()
                lines=stdout.readlines()
                if  any("virtnet_proxy" in s for s in lines):
                    LOG.info("Proxy already running on host: "+ self.ip)
                else:
                    _, stdout, stderr = shell.exec_command("VBoxManage startvm \"virtnet_proxy\" --type headless" )
                    exit_status = stdout.channel.recv_exit_status()         
                    if exit_status == 0:
                        LOG.info("VM_started on host "+ self.ip + " " + " ".join(stdout.readlines()))
                        time.sleep(30)
                    else:
                        LOG.info("Error occured on host "+ self.ip +" "+  " ".join(stderr.readlines()))
                    
                       
                shell.close()
        except Exception as e:
            LOG.info("Error occured on host "+ self.ip +": ")
            LOG.info(e)
            shell.close()

    def get_proxy_ip(self):
       
        shell = self.connect_ssh()
        try:
            if self.os == 'windows':
                while True: 
                    stdin, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\Virtualbox\VBoxManage\" guestcontrol \"\"virtnet_proxy\"\" run --exe \"\"/home/virtnet/show_ip.sh\"\" --username virtnet --password "+ self.get_pw_from_file()+"\"")
                    exit_status = stdout.channel.recv_exit_status()         
               
                    if exit_status == 0:
                        proxy_ip=stdout.readlines()
                        if proxy_ip[0].strip('\n') == "":
                            continue
                        LOG.info("Got proxy ip from host  "+ self.ip+": " +proxy_ip[0].strip('\n'))
                        self.proxy_ip = proxy_ip[0].strip('\n')
                        shell.close()
                        break
                        
                    else:
                        LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))

                        
                    time.sleep(2)
                        
                        
            elif self.os == "linux": 
                while True:
                              
                        _, stdout, stderr = shell.exec_command("VBoxManage guestcontrol \"virtnet_proxy\" run --exe \"/home/virtnet/show_ip.sh\" --username virtnet --password "+ self.get_pw_from_file() )
                        exit_status = stdout.channel.recv_exit_status()          
                        if exit_status == 0:
                            proxy_ip=stdout.readlines()
                            if proxy_ip[0].strip('\n') == "":
                                continue
                            LOG.info ("Got proxy ip from host  "+ self.ip+": " +proxy_ip[0].strip('\n'))
                            self.proxy_ip = proxy_ip[0].strip('\n')
                            shell.close()
                            break
                        else:
                            LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))

                           
                        time.sleep(2)
        except Exception as e:
            LOG.info("Error occured on host "+ self.ip +": ")
            LOG.info(e)
            shell.close()
               
        
    def stop_proxy(self):
        
        shell = self.connect_ssh()
        try:
            if self.os=="windows":
                _, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\VirtualBox\VBoxManage.exe\" list runningvms\"" )
                exit_status = stdout.channel.recv_exit_status()
                lines=stdout.readlines()
                if not any("virtnet_proxy" in s for s in lines):
                    LOG.info("Proxy not running on host: "+ self.ip)
                else:
                    self.flush_vbox_interfaces() 
                    _, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\VirtualBox\VBoxManage.exe\" controlvm \"\"virtnet_proxy\"\" poweroff\"" )
                    exit_status = stdout.channel.recv_exit_status() 
                         
                    if exit_status == 0:
                        LOG.info("Proxy VM powered off on host "+self.ip)
                    else:
                        LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))
                    

                        
                shell.close()
            elif self.os=="linux":
                _, stdout, stderr = shell.exec_command("VBoxManage list runningvms" )
                exit_status = stdout.channel.recv_exit_status()
                lines=stdout.readlines()
                if not any("virtnet_proxy" in s for s in lines):
                    LOG.info("proxy not running on host: "+ self.ip)
                else:
                    self.flush_vbox_interfaces() 
                    _, stdout, stderr = shell.exec_command("VBoxManage controlvm \"virtnet_proxy\" poweroff" )
                    exit_status = stdout.channel.recv_exit_status()  
                      
                    if exit_status == 0:
                        LOG.info("Proxy VM powered off on host "+ self.ip)
                    else:
                        LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))
                   
                    
                shell.close()

        except Exception as e:
            LOG.info("Error occured on host "+ self.ip +": ")
            LOG.info(e)
            shell.close()  

          
            


    def execute_command_on_proxies(self, cmd):
        while True:
            try:
                client=paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(self.proxy_ip,22,'virtnet',self.get_pw_from_file())
                time.sleep(1)
                stdin, stdout, stderr = client.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                output = stdout.readlines()

                client.close()
                return output           
            except Exception as e:
                LOG.info('Error executing command on :'+ self.proxy_ip+ ": ")
                LOG.info(e)
                time.sleep(2)
                client.close()

    def add_internal_network(self, number, iface):
        shell = self.connect_ssh()
        if self.os == 'windows':
            try:
                stdin, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\Virtualbox\VBoxManage\" controlvm \"\"virtnet_proxy\"\" nic"+str(iface)+" intnet "+"vx"+str(number)+"\"")
                exit_status = stdout.channel.recv_exit_status()
                stdin2, stdout2, stderr2 = shell.exec_command("\"\"\Program Files\Oracle\Virtualbox\VBoxManage\" controlvm \"\"virtnet_proxy\"\" setlinkstate"+str(iface)+" on\"")
                exit_status = stdout2.channel.recv_exit_status()          
                if exit_status == 0:
                    
                    shell.close()
                else:
                    LOG.info("Error occured on host "+ self.ip +": "+ " ".join(stderr.readlines()))
                    shell.close()
            except Exception as e:
                LOG.info("Error occured on host "+ self.ip +": ")
                LOG.info(e)
                shell.close()
        elif self.os == 'linux':
            try:
                stdin, stdout, stderr = shell.exec_command("VBoxManage controlvm \"virtnet_proxy\" nic"+str(iface)+" intnet "+"vx"+str(number))                         
                exit_status = stdout.channel.recv_exit_status()            
                stdin2, stdout2, stderr2 = shell.exec_command("VBoxManage controlvm \"virtnet_proxy\" setlinkstate"+str(iface)+" on")                         
                exit_status = stdout2.channel.recv_exit_status()           
                if exit_status == 0:
                    
                    shell.close()
                else:
                    LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))
                    shell.close()
            except Exception as e:
                LOG.info("Error occured on host "+ self.ip +": ")
                LOG.info(e)
                shell.close()
    def append_ip_to_proxy_fdb(self, vni, ip):
        self.execute_command_on_proxies( 'sudo bridge fdb append ff:ff:ff:ff:ff:ff dev vx'+str(vni)+ ' dst '+ ip)

    def delete_fdb_entry(self, vni, ip):
        self.execute_command_on_proxies( 'sudo bridge fdb del ff:ff:ff:ff:ff:ff dev vx'+str(vni)+ ' dst '+ ip)

    def add_virtnet(self, vni):
        if self.check_if_network_exists(vni) == False:
            LOG.info('Creating network on proxy ' + self.proxy_ip)
            iface = self.get_free_interface()
            try:
                self.add_internal_network(vni,int(iface[0])-1)
        
                self.execute_command_on_proxies( 'sudo brctl addbr br-'+str(vni))
                self.execute_command_on_proxies( 'sudo ip link add vx'+str(vni)+' type vxlan id '+str(vni)+' dstport 4789 local '+self.proxy_ip + " dev enp0s3")
                self.execute_command_on_proxies( 'sudo brctl addif br-'+str(vni)+' vx'+str(vni))
                self.execute_command_on_proxies( 'sudo ip link set br-'+str(vni)+' up')
                self.execute_command_on_proxies( 'sudo ip link set vx'+str(vni)+' up')
        
        
                
                self.execute_command_on_proxies( 'sudo brctl addif br-'+str(vni)+ " " + iface[1].strip('\n'))
                self.execute_command_on_proxies( 'sudo ifup '+ iface[1].strip('\n'))
                LOG.info("Network created on proxy "+ self.proxy_ip)
            except paramiko.SSHException as e:
                LOG.info ("Error occured on proxy "+ self.proxy_ip +": ")
                LOG.info(e)
                self.del_virtnet(vni)
        else:
            LOG.info("Network already exists on proxy "+ self.proxy_ip)
                
    
    def del_virtnet(self, vni):
        LOG.info('removing net vx'+vni + " on host " + self.ip )
        iface = self.get_iface_info(vni,"name")
        iface_number = self.get_iface_info(vni, "number")
        if self.check_if_network_exists(vni) == True:
            try:
                self.del_internal_network(iface_number)
                LOG.info('Removing network on proxy ' + self.proxy_ip)
                if iface is not None:
                    self.execute_command_on_proxies( 'sudo ifdown '+iface)
                    self.execute_command_on_proxies( 'sudo ip link set vx'+str(vni)+' down')
                    self.execute_command_on_proxies( 'sudo ip link set br-'+str(vni)+' down')

                    self.execute_command_on_proxies( 'sudo ip link del vx'+str(vni))
                    self.execute_command_on_proxies( 'sudo brctl delbr br-'+str(vni))
        
                    LOG.info('Removed network on proxy ' + self.proxy_ip)
              
            except paramiko.SSHException as e:
                LOG.info("Error occured on proxy "+ self.proxy_ip +": ")
                LOG.info(e)
                
                self.del_internal_network(iface_number)
        else:
            LOG.info("Network with vni "+vni+" does not exist on proxy "+ self.proxy_ip)
        
    def del_internal_network(self, iface):
        shell = self.connect_ssh()
        if self.os == 'windows':
            try:
                stdin2, stdout2, stderr2 = shell.exec_command("\"\"\Program Files\Oracle\Virtualbox\VBoxManage\" controlvm \"\"virtnet_proxy\"\" setlinkstate"+str(iface)+" off\"")
                exit_status = stdout2.channel.recv_exit_status() 
                stdin, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\Virtualbox\VBoxManage\" controlvm \"\"virtnet_proxy\"\" nic"+str(iface)+" null\"")
                exit_status = stdout.channel.recv_exit_status() 
                if exit_status == 0:
                    
                    shell.close()
                else:
                    LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))
                    shell.close()
            except Exception as e:
                LOG.info("Error occured on host "+ self.ip +": ")
                LOG.info(e)
                shell.close()
        elif self.os == 'linux':
            try:
                stdin2, stdout2, stderr2 = shell.exec_command("VBoxManage controlvm \"virtnet_proxy\" setlinkstate"+str(iface)+" off")                         
                exit_status = stdout2.channel.recv_exit_status()
                stdin, stdout, stderr = shell.exec_command("VBoxManage controlvm \"virtnet_proxy\" nic"+str(iface)+" null")                         
                exit_status = stdout.channel.recv_exit_status() 
                if exit_status == 0:
                    
                    shell.close()
                else:
                    LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))
                    shell.close()
            except Exception as e:
                LOG.info("Error occured on host "+ self.ip +": ")
                LOG.info(e)
                shell.close()

    def get_iface_info(self, vni, command):
        output = self.execute_command_on_proxies( '/home/virtnet/get_iface_info.py')
        ifaces = []
        for string in output:
            ifaces.append(string.split())
        for iface in ifaces:
            if iface[2].strip("\n") == str(vni):
                if command =="number":
                    return int(iface[0])-1
                elif command =="name":
                    return iface[1]
        return None

    def get_free_interface(self):
        
        output = self.execute_command_on_proxies( '/home/virtnet/show-interfaces.py')
        iface = output[0].split(" ")
        return iface

    def check_if_network_exists(self, vni):
        if self.get_iface_info(vni, "name") != None:
            return True
        else:
            return False
    
    def reset_iface(self, vni):
        LOG.info("resetting iface on proxy: "+self.proxy_ip)
        iface = self.get_iface_info(vni, "name")
        if iface != None:
            self.execute_command_on_proxies("sudo ifdown "+ iface)
            self.execute_command_on_proxies("sudo ifup "+ iface)
        else:
            LOG.info("Error occured on host "+ self.ip +" Cannot reset interface")
    
    def flush_vbox_interfaces(self):
        
        LOG.info("Flushing Proxy's interfaces on host "+ self.ip + "...")
        if self.os == 'windows':
            for i in range(2,37):
                shell = self.connect_ssh()
                try:
                    stdin2, stdout2, stderr2 = shell.exec_command("\"\"\Program Files\Oracle\Virtualbox\VBoxManage\" controlvm \"\"virtnet_proxy\"\" setlinkstate"+str(i)+" off\"")
                    exit_status = stdout2.channel.recv_exit_status() 
                    stdin, stdout, stderr = shell.exec_command("\"\"\Program Files\Oracle\Virtualbox\VBoxManage\" controlvm \"\"virtnet_proxy\"\" nic"+str(i)+" null\"")
                    exit_status = stdout.channel.recv_exit_status()
                    if exit_status == 0:
                        
                        shell.close()
                    else:
                        LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))
                        shell.close()
                except Exception as e:
                    LOG.info("Error occured on host "+ self.ip +": ")
                    LOG.info(e)
                    shell.close()
        elif self.os == 'linux':
            for i in range(2,37):
                shell = self.connect_ssh()
                try:
                    stdin2, stdout2, stderr2 = shell.exec_command("VBoxManage controlvm \"virtnet_proxy\" setlinkstate"+str(i)+" off")                         
                    exit_status = stdout2.channel.recv_exit_status()
                    stdin, stdout, stderr = shell.exec_command("VBoxManage controlvm \"virtnet_proxy\" nic"+str(i)+" null")                         
                    exit_status = stdout.channel.recv_exit_status()  
                     
                    if exit_status == 0:
                    
                        shell.close()
                    else:
                        LOG.info("Error occured on host "+ self.ip +" "+ " ".join(stderr.readlines()))
                        shell.close()
                except Exception as e:
                    LOG.info("Error occured on host "+ self.ip +": ")
                    LOG.info(e)
                    shell.close()


def parse_hosts_file(filename):
    ssh_hosts={}
    with open(filename,"r") as hosts_file:
        data = yaml.load(hosts_file, Loader=yaml.BaseLoader)
        for section in data:
            if section=="hosts":
                for hosts in data[section]:
                    ssh_hosts[hosts]=data[section][hosts]
 
    return ssh_hosts




    





