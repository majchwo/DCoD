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
   - Linux -- OpenSSH 
4. *virtnet_proxy* VM imported to VirtualBox
5. For Windows systems -- VBoxManage.exe tool available under *\Program Files\Oracle\Virtualbox\\* path

### Network requirements

1. DHCP server running in LAN network in order to assign IP address to *virtnet_proxy* VM's bridged interface



## DCoD system architecture

![Alt text](https://github.com/wojtaszevsky/DCoD/blob/main/dcod-architecutre.png?raw=true)


Key components:

1. **Hypervisor** - host with VirtualBox software running
2. **Proxy VM** - *virtnet_proxy* VM, running on each hypervisor, responsible for overlay packets encap/decap & broadcast traffic handling etc. In other words - overlay VTEP.
3. **Internal network** - VirtualBox internal network created automatically for each virtual network (identified by VNI), access point to DCoD infrastructure for user's VMs
4. **Director** - logical component, place (host) where *virtnet.py* script & monitoring server script are available. **Director** must have access to all Hyperviors (DCoD hosts) via SSH.
