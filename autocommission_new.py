from manager import DeviceManager
import yaml
import threading
import logging
import logger


if __name__ == "__main__":

    file = open("config.yaml", 'r') 
    config = yaml.safe_load(file)
    config['open_terms']

    # Run logger module, to configure handlers and formats
    logger.init()
    
    # Create a logger
    logger = logging.getLogger(__name__)

    # Instantiate the DeviceManager
    PAEManager = DeviceManager(config)

    # Get devices(boards) in the system
    dc = config['device']
    
    if dc['device_type'] == 'USB':
        devices = PAEManager.get_USBDevices()

    elif dc['device_type'] == 'Mock':
        devices = PAEManager.get_MockDevices(dc['mock_config']['number'],dc['commissioner_device_id'])

    elif dc['device_type'] == 'HTTP':
        logger.info('Device not yet implemented')
        exit()
    else:
        logger.critical('Device type does not exist')
        exit()

    PAEManager.devices = devices

    # TODO: Decouple configuration from the code. Create YAML file with all the configs

    # Set topology
    top = PAEManager.all_to_one()
    PAEManager.topology = top

    # TODO multithreading for reset
    # Factory reset the boards
    for dev in PAEManager.devices:
        PAEManager.reset_device(dev)

    # Print the topology
    if config['topology']['plot']:
        PAEManager.plot_graph()
    
    # Create network
    PAEManager.apply_topology()
    
    # Open UDP and connect all the boards
    if config['threading']:
        openingudps=list()
        ip = PAEManager.open_udp_communication(PAEManager.devices[0])
        for dev in PAEManager.devices[1:]:
            openingudps.append(threading.Thread(target=PAEManager.udp_connect, args=(ip, dev)))
            openingudps[-1].start()

        # Wait for all the boards to open the udp port
        [openedudp.join() for openedudp in openingudps]
    else:
        ip = PAEManager.open_udp_communication(PAEManager.devices[0])
        for dev in PAEManager.devices[1:]:
            PAEManager.udp_connect(ip, dev)
    
    if config['open_terms']:   # See config.yaml    
        # Open terminal for each device   
        for device in devices: 
            device.terminal()

    # TODO: Implement terminal for the program (cmd, ncurses or miniterm.py (from pyserial)) 
