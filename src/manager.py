import os
import re
import serial
import time
import device_classes as d
import threading
import logging
import ot_functions as ot


class DeviceManager(object):
    """ """

    def __init__(self, config):
        """  """
        
        self.devices = list()
        self.topology = None
        self.commissioner_id = config['device']['commissioner_device_id']
        self.config = config 

        
        self.init_log(config)
        self.log = logging.getLogger("PAEManager") 
    
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
    
    def handle_request(self, message):
        self.log.warning(f"Instruction unknown ({message})")

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
    

    ################################################################################################
    # (TOPOLOGY RELATED FUNCTIONS)

    def getDevice(self, id):
        """ Returns a device given its id 
            Params:
            - id (integer)
            Return:
            - device (Device object)
        """
        # Find the device in the list
        # (N time log) maybe use binary search if needed ?
        result = next((dev for dev in self.devices if dev.id == id), None)

        # We check if it found the device, if not result will be None and
        # will evaluate to False in the if conditional
        if result:
            return result
        else:
            self.log.error('Device does not exist in the list! Check again')

    def all_to_one(self):
        """ Creates all to one topology
            Returns:
            - adjacency_dict : dictionary with the pairs id:[connected_ids]
              all the data are integers    
        """
        # Length check for the topology
        if len(self.devices) < 2:
            self.log.error('Can not create topology if < 2 devices')
            return

        # It is better to use the ids as they are integers and provide a
        # way to decouple the data structures (by means of a join). We exclude 
        # the commissioner from the list of ids.
        ids = [ device.id for device in self.devices if device.id != self.commissioner_id]

        # The commissioner is a defined id in the Yaml configuration
        commissioner_id = self.commissioner_id

        # Create adjacency list with all the current devices connectating
        # to the commissioner
        adjacency_dictionary = {idn: [commissioner_id] for idn in ids}

        # we add the entry for the commissioner and it's ready
        adjacency_dictionary[commissioner_id] = []

        return adjacency_dictionary

    def apply_topology(self):
        """ Applies the topology set in self.topology to the boards connected """

        # TODO: Implement manner to check if the nodes are already connected
        
        # Check that there's a topology set
        if not self.topology:
            self.log.error('There is no topology specified! Please indicate one and call the method again')
            return
        
        # A list of all the threads joining the network
        joiners=list()
        
        # Iterate through all the items in the adjacency dictionary, take
        # into account that the values are the Device id, so to act on them
        # it is needed to get the Device object
        for key, values in self.topology.items():
            # Get device by id
            joiner = self.getDevice(id=key)

            for device_id in values:
                # Get device by id
                commissioner = self.getDevice(id=device_id)

                # Check that the device is initalized to work as a commissioner
                if commissioner.isCommissioner:
                    ot.initialize_commissioner(commissioner)

                # Authenticate both devices
                joiners.append(threading.Thread(target=ot.authenticate, args=(commissioner, joiner)))
                joiners[-1].start()
                # self.authenticate(commissioner, joiner)
        
        # Wait for all the nodes to join the network
        [joiner.join() for joiner in joiners]
        self.log.info('All devices connected')

    
    def plot_graph(self):
        """ Plots the topology 
            It generates an image with the networkx library, stores it
            and opens the image.
        """
        log = logging.getLogger('matplotlib')
        log.setLevel(logging.ERROR)
        
        # Necessary imports
        from networkx import parse_adjlist, draw
        from matplotlib.pyplot import figure, savefig

        # Vars
        lines = []
        
        # networkx needs a list with the following structure:
        # ['1 connected nodes', '2 connected nodes', ... ]
        # It has a string for every node containing the chronological order
        # the connections it has.
        # Example all to one structure:
        # ['1 3', '2 3', '3 ']
        # In this example the first two nodes are connected to the 
        # third node. Note that the index starts at one
        for key,values in self.topology.items():
            # Generate the connections string
            intermed = ", ".join([str(j+1) for j in values])
            lines.append(f'{key+1} {intermed}')
        
        # Create networkx Graph from the adjacency list
        G = parse_adjlist(lines, nodetype = int)
        
        # Get a dict with the labels of every node
        labels = dict((n, self.getDevice(n-1).name) for n in G.nodes())
        
        # Asign a colour to each node. If is a commissioner node, blue will be assigned.
        # If is a joiner, green will be assigned
        colours=[]
        for n in G.nodes():
            if self.getDevice(n-1).isCommissioner:
                colours.insert(n,'b')
            else:
                colours.insert(n,'g')
        
        # Larger figure size
        figure(3,figsize=(12,12))
        
        # Draw graph
        draw(G, node_size=5000, with_labels=True, font_weight='bold', labels=labels, node_color=colours)
        
        # Export image and open with eog
        savefig(self.config['topology']['file_name'])
        os.system(f"eog {self.config['topology']['file_name']} &")
