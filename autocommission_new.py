from manager import DeviceManager

if __name__ == "__main__":

    # Instantiate the DeviceManager
    PAEManager = DeviceManager()

    # Get devices(boards) in the system
    devices = PAEManager.get_USBDevices()
    ## devices = PAEManager.get_MockDevices(8)
    ## devices = PAEManager.get_HTTPDevices()

    PAEManager.devices = devices

    # Set topology
    # TODO: Implement topology setting with a graph library or handmade graph ?
    # Currently implementing a all to 1 structure, connecting all the boards to
    # the first one
    
    # Factory reset the boards
    # [PAEManager.reset_device(dev) for dev in PAEManager.devices]
    for dev in PAEManager.devices:
        PAEManager.reset_device(dev)

    # Create network
    commissioner = PAEManager.devices[0]
    PAEManager.initialize_commissioner(commissioner)
    
    # Connect all the other devices to the commisioner
    for dev in PAEManager.devices[1:]:
        PAEManager.authenticate(commissioner, dev)
    
    # Open UDP and connect all the boards
    ip = PAEManager.open_udp_communication(commissioner)
    for dev in PAEManager.devices[1:]:
        PAEManager.udp_connect(ip, dev)

    # Open terminal for each device
    for device in devices: 
        device.terminal()

    # TODO: Implement terminal for the program (cmd, ncurses or miniterm.py (from pyserial)) 
   

