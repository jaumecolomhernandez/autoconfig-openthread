from manager import DeviceManager
import yaml


if __name__ == "__main__":

    file = open("config.yaml", 'r') 
    config = yaml.safe_load(file)
    config['open_terms']

    # Instantiate the DeviceManager
    PAEManager = DeviceManager(config)

    # Get devices(boards) in the system
    dc = config['device']
    if dc['device_type'] == 'USB':
        devices = PAEManager.get_USBDevices()

    elif dc['device_type'] == 'Mock':
        devices = PAEManager.get_MockDevices(dc['mock_config']['number'])

    elif dc['device_type'] == 'HTTP':
        print('Device not yes implemented')
        exit()
    else:
        print('Device type does not exist')
        exit()

    PAEManager.devices = devices

    # TODO: Decouple configuration from the code. Create YAML file with all the configs

    # Set topology
    top = PAEManager.all_to_one()
    PAEManager.topology = top

    # Factory reset the boards
    for dev in PAEManager.devices:
        PAEManager.reset_device(dev)

    # Print the topology
    if config['topology']['plot']:
        PAEManager.plot_graph()
    
    # Create network
    PAEManager.apply_topology()
    
    # Open UDP and connect all the boards
    # ip = PAEManager.open_udp_communication(PAEManager.devices[0])
    for dev in devices:
        ip_static_set(dev)

    
    if config['open_terms']:   # See config.yaml    
        # Open terminal for each device   
        for device in devices: 
            device.terminal()

    # TODO: Implement terminal for the program (cmd, ncurses or miniterm.py (from pyserial)) 
