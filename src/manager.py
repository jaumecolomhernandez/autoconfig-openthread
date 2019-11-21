import os, re, time
import threading, logging, sys

import topology
import ot_functions as ot
import device_classes as d

sys.path.append('flask_server/')
from flask_server.main import app as FlaskServer
from flask_server.main import init_app_old

sys.path.append('networking/')
#from src.tcp_customserver_class import TCPServer
from networking.udp_customserver_class import UDPServer

import serial

class DeviceManager(object):
    """ """
    # TODO: Complete all the docstrings
    # TODO: Implement PEP8 in the most complete sense
    
    def __init__(self, config):
        """  """
        
        self.devices = list()
        self.topology = {}
        self.commissioner_id = config['device']['commissioner_device_id']
        self.config = config 

        
        self.init_log(config)
        self.log = logging.getLogger("PAEManager") 

        # Server object/s
        self.internal_server = UDPServer('localhost', 12342, self, logging.getLogger("UDPServer"))

        self.external_server = FlaskServer  # TODO: Make this a class # TODO Think new way of initializing this
        init_app_old(self, logging.getLogger("FlaskServer"))

        # TODO: (OPENTHREAD) Test the case where there is no range and transmission involves a two hop travel
        # TODO: Create distinct function to init servers maybe

        # And start server/s
        iserver_thread = threading.Thread(target=self.internal_server.run_forever)
        iserver_thread.start()

        eserver_thread = threading.Thread(target=self.external_server.run, kwargs={'host' : '0.0.0.0', 'port' : 8088})
        eserver_thread.start()

        if config['debug']:
            import serial
    
    def init_log(self, config):
        """  """
        # Create a custom logger, defining from which level the logger will handle errors
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)

        # Create a handler to display by console
        handler = logging.StreamHandler()
        
        # Defining the level of the handler, reading from the config.yalm
        handler.setLevel(config['logger']['level'])

        # Read the format from de config.yalm and create a Formatter
        format = logging.Formatter(config['logger']['format'],  datefmt='%m/%d/%Y %I:%M:%S')
        
        # Add the Formatter to the handler
        handler.setFormatter(format)

        # Add handler to the logger
        log.addHandler(handler)
    
    def get_device(self, id_number=None, address_tuple=None):
        """ Returns a device given its id (ONLY PASS ONE PARAMETER!)
            Params:
            - id_number (integer)
            - address_tuple (tuple(integer, string))
            Return:
            - device (Device object)
        """
        # Find the device in the list
        # (N time log) maybe use binary search if needed ?
        if id_number >= 0:
            result = next((dev for dev in self.devices if dev.id == id_number), None)
        elif address_tuple:
            result = next((dev for dev in self.devices if dev.addr == address_tuple), None)
        else:
            result = None
            print("There's no argument!(get_device())")
        
        return result

    def authorize(self, dev, message, address_tuple):
        """ Authorized new devices to the system
            Params:
            - dev: UDP or TCP device
            - message: list of space separated words in of message
            - address_tuple: tuple with host and port
            Returns:
            - Message to send back to the device
        """

        if len(message) != 2:
            return "NON-AUTHORIZED: invalid order"
        
        if message[0] != "AUTH":
            return "NON-AUTHORIZED: invalid order"

        dev_id = int(message[1]) # This is the id (AUTH 45)
        old_dev = self.get_device(id_number=dev_id)

        # In case this device exists we reconnect de device, and delete the old one
        if(old_dev): 
            # Change parameters
            old_dev.addr = dev.addr
            old_dev.obj = dev.obj
            old_dev.connexion = True
            # Remove old device
            self.devices.remove(dev)

            # Send information along
            self.log.info(f"Device {address_tuple} with ID: {old_dev.id} correctly reconnected")
            return "Device authorized\r\n"
        
        # Then it is a new device, we add it to the list
        else: 
            # Set parameters
            dev.id = dev_id
            dev.connexion = True

            # Send information along
            self.log.info(f"Device {address_tuple} with ID: {dev.id} correctly authorized")
            return "Device authorized\r\n"

    
    def UDPhandle_request(self, message, address_tuple):
        """"""

        dev = self.get_device(address_tuple=address_tuple)
        message = message.decode('ascii').split()

        # First time connecting from this address_tuple
        if not dev:
            # OJO AQUI, FIQUEM EL SOCKET DEL SERVER A CADA DEVICE 
            # TODO: PENSAR EN EL FUTUR SI AIXO ES LA MILLOR MANERA DE FER-HO
            dev = self.add_UDPDevice(self.internal_server.server_socket, address_tuple)
            
            self.log.info(f"Added device to list {address_tuple}")
            # Here it doesn't return to allow to authorize on the first message
            
        # If it is not the first time check if reconnecting
        if not dev.connexion:   
            # self.authorize handles all the logs
            return self.authorize(dev, message, address_tuple)

        # TODO: Implement live check

        # Then standard orders
        if message[0] == "AUTH":
            return "Already connected!"
        elif message[0] == "VERSION":
            return f"You are -> {address_tuple}"
        elif message[0] == "ORDER2":
            pass
        else:
            self.log.error(f"Instruction unknown ({message})")
            return f"Instruction unknown ({message})"

    def TCPhandle_request(self, message, address_tuple):
        # UNUSED FUNCTION
        # May be shared with UDPhandle_request as they are mostly the same
        dev = self.get_device(address_tuple=address_tuple)
        message = message.split()

        if len(message) == 0:
            dev.connexion = False
            dev.obj = None
            self.log.error(f"Device {address_tuple} disconnected")
            return

        if not dev.connexion:
            mes = self.authorize(dev, message, address_tuple)
            dev.send_command(mes)
            return

        if message[0] == "AUTH":
            #dev.send_command("Ja estas connectat.")
            return "Already connected!"
        elif message[0] == "VERSION":
            pass
        elif message[0] == "ORDER2":
            pass
        else:
            self.log.error(f"Instruction unknown ({message})")
            return "NOT OK"

    ##

    def add_TCPDevice(self, socket, addr):
        """ """ 
        #self.ID-> Afegir IDtest
        idn = len(self.devices)+1
        dev = d.TCPDevice(idn, f"TCP{idn}", socket, addr)
        self.topology[idn] = []
        self.devices.append(dev)
    
    def add_UDPDevice(self, socket, addr):
        """ """ 
        #self.ID-> Afegir IDtest
        idn = len(self.devices)+1
        dev = d.UDPDevice(idn, f"TCP{idn}", socket, addr)
        self.topology[idn] = []
        self.devices.append(dev)
        return dev

    def add_HTTPDevice(self, ip):
        """ """
        #self.ID-> Afegir ID
        idn = len(self.devices)+1
        dev = d.HTTPDevice(idn, f"HTTP{idn}", ip)
        self.topology[idn] = []
        self.devices.append(dev)

    def get_sockets(self):
        """ """
        # DEPRECATED: ONLY USED IN TCP
        return [dev.obj for dev in self.devices if dev.obj]

    ##############################################################################################

    @staticmethod
    def get_tty():
        """ Parses the output of a shell command to get the ttyUSBX numbers """

        # Access /dev/serial/by-id to get info about the serial devices
        result = os.popen(
            'find /dev/serial/by-id/ -maxdepth 1 -type l -ls | cut -d"/" -f5- '
        ).read()

        # Keep the last number of every line.
        values = [re.findall(r"[0-9]+$", line)[0] for line in result.splitlines()]

        return values

    @classmethod
    def get_USBDevices(self):
        """ Returns a list with the current USB devices """

        # Instantiate list
        devices = list()
        # Get tty numbers
        tty_numbers = self.get_tty()

        # Iterate every number and create a USBDevice for each
        for number in tty_numbers:
            # Create device
            new_dev = d.USBDevice(
                int(number),
                "/dev/ttyUSB" + number,
                serial.Serial("/dev/ttyUSB" + number, 115200, timeout=0.5),
            )
            # Add it to the list
            devices.append(new_dev)

        return devices

    @staticmethod
    def get_MockDevices(number, commissioner_device_id):
        """ Returns a list with n MockDevices """
        # Instantiate list
        devices = list()

        # For every number
        for i in range(number):
            new_dev = d.MockDevice(i, "Mock" + str(i), None)
            devices.append(new_dev)

        # Tags the commissioner device
        devices[commissioner_device_id].isCommissioner=True
        
        return devices

    @staticmethod
    def get_HTTPDevices():
        pass
    
    
