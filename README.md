# DCoD
Data Center on Desk - virtual network infrastructure for VirtualBox VMs.

## DCoD system

DCoD system is intended to create and manage virtual L2 networks for VMs running on different hosts under VirtualBox hypervisor.

1. **VxLAN** used as overlay technology
2. **Head End Replication** mechanism used for handling boradcast traffic



### Host requirements

1. Windows or Linux system
3. VirtualBox hypervisor running
2. SSH servers running (connection using username&password required): 
   - Windows -- Bitvise SSH server
   - Linux -- OpenSSH server
4. *virtnet_proxy* VM imported to VirtualBox
5. For Windows systems -- VBoxManage.exe tool available under *\Program Files\Oracle\Virtualbox\\* path
6. On Director -> Python 3 with *paramiko*, *yaml*, *logging*, *time*, *argparse*, *threading*
 6.1. For monitoring server *Flask*, *json*, *requests*, *flask_restful*

### Network requirements

1. DHCP server running in LAN network in order to assign IP address to *virtnet_proxy* VM's bridged interface

# MANUAL

### Virtual network creation

**NOTE**: You do not have to manually start *virtnet_proxy* VM, if it does not run, the script automatically launches it.
**NOTE**: Script uses generic password for remote command execution on proxy VMs. It is read from password file. You can manually change it directly on proxy VM. 

1. Fill in the hosts yaml file with your hypervisor hosts ip addresses, ssh credentials & OS type (windows or linux)
2. Run virtnet script e.g. *./virtnet.py create --vni \<VNI\> -f \<hosts file\>*
3. Wait until script finishes. It can take some time depending on number of hosts

## Virtual network deletion

1. Make sure you have valid hosts file (all hypervisors covered)
2. Run virtnet script e.g. *./virtnet.py remove --vni \<VNI\> -f \<hosts file\>* in order to remove virtual network with specific VNI
3. Wait until script finishes. It can take some time depending on number of hosts

## Bring DCoD system down

NOTE: this procedure stops all *virtnet_proxy* VMs & clears its interfaces, so that the Proxy is in its generic state.

1. Make sure you have valid hosts file (all hypervisors covered)
2. Run virtnet script e.g. *./virtnet.py stop-proxies -f \<hosts file\>* in order to remove virtual network with specific VNI
3. Wait until script finishes. It can take some time depending on number of hosts

## Start monitoring server

**NOTE** Current implementation allows user to start the monitoring server which collects data form all proxies in system (in fact collects data from ifconfig command, executed on all proxies).

1. Make sure you have valid hosts file (all hypervisors covered)
2. Run server script e.g. *./server.py -f \<hosts file\> -p \<port\>* in order to start the monitoring server on localhost.
3. Go to *http://localhost:<port\>\/status* URL in order to get info about running DCoD system (currently presented in JSON format).


# DCoD system architecture

![Alt text](https://github.com/wojtaszevsky/DCoD/blob/main/dcod-architecutre.png?raw=true)


Key components:

1. **Hypervisor** - host with VirtualBox software running
2. **Proxy VM** - *virtnet_proxy* VM, running on each hypervisor, responsible for overlay packets encap/decap & broadcast traffic handling etc. In other words - overlay VTEP
3. **Internal network** - VirtualBox internal network created automatically for each virtual network (identified by VNI), access point to DCoD infrastructure for user's VMs
4. **Director** - logical component, place (host) where *virtnet.py* script & monitoring server script are available. **Director** must have access to all Hyperviors (DCoD hosts) via SSH

# TODO:

1. First of all code cleaning. I'm aware it is a mess. Initially it just had to work. I'm a network engineer, rather than programmer, still wanting to learn how to code though... :)
2. The windows VBoxManage.exe file location is hardcoded. Should make it flexible
3. Add the change of virtnet_proxy VM ssh password functionality
4. Add the ssh keypair login functionality (both to  hosts and proxies)
5. Other stuff...

