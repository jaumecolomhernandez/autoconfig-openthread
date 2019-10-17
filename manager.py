import os
import re
import serial
import time
import device_classes as d


class DeviceManager(object):
    """ """

    def __init__(self, config):
        self.devices = list()
        self.topology = None
        self.commissioner_id = config['device']['commissioner_device_id']    

    @staticmethod
    def get_tty():
        """ Parses the output of a shell command to get the ttyUSBX numbers """

        # Access /dev/serial/by-id to get info about the serial devices
        result = os.popen(
            'find /dev/serial/by-id/ -maxdepth 1 -type l -ls | cut -d"/" -f5- '
        ).read()

        # TODO: Implementation of logging module with NORMAL and DEBUG modes
        # print (result) # debug line

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
    def get_MockDevices(number):
        """ Returns a list with n MockDevices """
        # Instantiate list
        devices = list()

        # For every number
        for i in range(number):
            new_dev = d.MockDevice(i, "Mock" + str(i), None)
            devices.append(new_dev)

        return devices

    @staticmethod
    def get_HTTPDevices():
        pass

    #####################################################################################################
    # USER METHODS
    # TODO: implement async methods for all the functions!
    def initialize_commissioner(self, device):
        """ Initializes the board with the necessary commands """

        # initializer commands
        init_commands = [
            "dataset init new",
            "dataset",
            "dataset commit active",
            "panid 0xdead",
            "ifconfig up",
            "thread start",
            "ipaddr",
        ]

        # Call every command
        for command in init_commands:
            device.send_command(command)

        device.isCommissioner = True

    def authenticate(self, commissioner, joiner):
        """ Authenticates a joiner device in the commissioner network 
            Params:
            - commissioner: Device object
            -
            Returns:
            - 
        """

        if not commissioner.isCommissioner:
            print("ERROR: {commissioner} is no a Commissioner")

        # TODO: Further comment the function

        # get the eui64 from the joiner
        commands = joiner.send_command("eui64", back=True)
        euid = commands[2][:-2]

        time.sleep(1)
        joiner.send_command("scan")
        joiner.read_answer()

        commissioner.send_command("commissioner start")
        time.sleep(0.5)
        commissioner.send_command(f"commissioner joiner add {euid} AAAA")

        time.sleep(0.5)
        joiner.send_command("ifconfig up")
        joiner.send_command("panid 0xdead")
        joiner.send_command("joiner start AAAA")

        # scan the network
        joiner.send_command("scan")
        joiner.read_answer()

        # TODO Implement the loggin module with two levels
        print("Waiting for the joiner answer...")
        try:
            joiner.read_answer(ending_ar=["Join success\r\n"])
        except:
            print("Stopped by the user!")

        joiner.send_command("ifconfig up")
        joiner.send_command("thread start")

    def open_udp_communication(self, receiver):
        """ """
        # Open the commissioner's udp port
        receiver.send_command("udp open")
        receiver.send_command("udp bind :: 1212")

        ips = receiver.send_command("ipaddr", back=True)
        send_ip = ips[1][:-2]

        return send_ip

    def udp_connect(self, send_ip, sender):
        """ """
        sender.send_command("udp open")
        sender.send_command(f"udp connect {send_ip} 1212")

    def reset_device(self, device):
        """ Calls factoryreset method on the board """
        device.read_answer(timeout=4)
        device.send_command("factoryreset", timeout=3)

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
            print("ERROR: Device does not exist in the list! Check again")

    def all_to_one(self):
        """ Creates all to one topology
            Returns:
            - adjacency_dict : dictionary with the pairs id:[connected_ids]
              all the data are integers    
        """
        # Length check for the topology
        if len(self.devices) < 2:
            print("ERROR: Can't create topology if < 2 devices")
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
            print(
                "ERROR: There's no topology specified! Please indicate one \
and call the method again"
            )
            return

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
                if not commissioner.isCommissioner:
                    self.initialize_commissioner(commissioner)

                # Authenticate both devices
                self.authenticate(commissioner, joiner)

        print("All devices connected")

    
    def plot_graph(self):
        """ Plots the topology 
            It generates an image with the networkx library, stores it
            and opens the image.
        """

        # Necessary imports
        import networkx as nx
        import matplotlib.pyplot as plt

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
        G = nx.parse_adjlist(lines, nodetype = int)
        
        # Get a dict with the labels of every node
        labels = dict((n, self.self.getDevice(n-1).name) for n in G.nodes())
        
        # networkx call to generate the image
        nx.draw(G, with_labels=True, font_weight='bold', node_color="powderblue", labels=labels)
        
        # Export image and open with eog
        plt.savefig('foo.png')
        os.system("eog foo.png &")

    

