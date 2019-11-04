import yaml
import threading
import logging
import sys

sys.path.append('src/')
import src.ot_functions as ot
from src.manager import DeviceManager

if __name__ == "__main__":

    file = open("debug_config.yaml", 'r') 
    config = yaml.safe_load(file)

    # Instantiate the DeviceManager
    PAEManager = DeviceManager(config)

    # Get a logger
    log = PAEManager.log

    # Get devices(boards) in the system
    if config['device']['device_type'] == 'USB':
        devices = PAEManager.get_USBDevices()

    elif config['device']['device_type'] == 'Mock':
        devices = PAEManager.get_MockDevices(config['device']['mock_config']['number'],config['device']['commissioner_device_id'])

    elif config['device']['device_type'] == 'HTTP':
        log.info('Device not yet implemented')
        exit()
    else:
        log.critical('Device type does not exist')
        exit()

    PAEManager.devices = devices

    # Set topology
    top = PAEManager.all_to_one()
    PAEManager.topology = top

    # Factory reset the boards
    if config['threading']:
        devices_resetting = list()
        for dev in PAEManager.devices:
            devices_resetting.append(threading.Thread(target=ot.reset_device, args=(dev,)))
            devices_resetting[-1].start()

        # Wait for all the boards to open the udp port
        [reseted_device.join() for reseted_device in devices_resetting]
        
    else:
        for dev in PAEManager.devices:
            ot.reset_device(dev)

    # Print the topology
    if config['topology']['plot']:
        PAEManager.plot_graph()
    
    # Create network
    # TODO: Redo the apply_topology function bc no longer ok
    PAEManager.apply_topology()
    
    # Open UDP and connect all the boards
    if config['threading']:
        openingudps=list()
        ip = ot.open_udp_communication(PAEManager.devices[0])
        for dev in PAEManager.devices[1:]:
            openingudps.append(threading.Thread(target=ot.udp_connect, args=(ip, dev)))
            openingudps[-1].start()

        # Wait for all the boards to open the udp port
        [openedudp.join() for openedudp in openingudps]
    else:
        ip = ot.open_udp_communication(PAEManager.devices[0])
        for dev in PAEManager.devices[1:]:
            ot.udp_connect(ip, dev)
    
    if config['open_terms']:   # See config.yaml    
        # Open terminal for each device   
        for device in devices: 
            device.terminal()

    # TODO: Implement terminal for the program (cmd, ncurses or miniterm.py (from pyserial)) 
