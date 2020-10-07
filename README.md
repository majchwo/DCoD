# DCoD
Data Center on Desk - virtual network infrastructure for VirtualBox VMs.

## DCoD system

DCoD system is intended to create and manage virtual L2 networks for VMs running on different hosts under VirtualBox hypervisor.

1. **VxLAN** used as overlay technology
2. **Head End Replication** mechanism used for handling boradcast traffic

### Host requirements

1. Windows or Linux system
3. VirtualBox hypervisor running
2. SSH servers running: 
   - Windows -- Bitvise SSH server
   - Linux -- OpenSSH 
4. *virtnet_proxy* VM imported to VirtualBox
5. For Windows systems -- VBoxManage.exe tool available under 

