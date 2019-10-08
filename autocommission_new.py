from manager import DeviceManager

if __name__ == "__main__":

    # Instantiate the DeviceManager
    PAEManager = DeviceManager()

    # Get devices(boards) in the system
    ## devices = PAEManager.get_USBDevices()
    devices = PAEManager.get_MockDevices(8)
    ## devices = PAEManager.get_HTTPDevices()

    PAEManager.devices = devices

    # TODO: Decouple configuration from the code. Create YAML file with all the configs

    # Set topology
    top = PAEManager.all_to_one()
    PAEManager.topology = top

    # PAEManager.plot(top)
    
    # Factory reset the boards
    # [PAEManager.reset_device(dev) for dev in PAEManager.devices]
    for dev in PAEManager.devices:
        PAEManager.reset_device(dev)

    PAEManager.plot_graph()
    
    # Create network
    PAEManager.apply_topology()
    
    # Open UDP and connect all the boards
    ip = PAEManager.open_udp_communication(PAEManager.devices[0])
    for dev in PAEManager.devices[1:]:
        PAEManager.udp_connect(ip, dev)

    # Open terminal for each device
    for device in devices: 
        device.terminal()

    # TODO: Implement terminal for the program (cmd, ncurses or miniterm.py (from pyserial)) 
   

