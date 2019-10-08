import os
import re
import serial
import time
import device_classes as d

class DeviceManager(object):
    """ """

    # TODO: Implement singleton pattern ?

    def __init__(self):
        self.devices = list()
        self.topology = None

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
        values = [re.findall(r'[0-9]+$',line)[0] for line in result.splitlines()]
        
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
            new_dev = d.MockDevice(
                i,
                "Mock"+str(i),
                None
            )
            devices.append(new_dev)
        
        return devices

    @staticmethod
    def get_HTTPDevices():
        pass

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
    
    def authenticate(self, commissioner, joiner):
        """ Authenticates a joiner device in the commissioner network 
            Params:
            - commissioner: Device object
            -
            Returns:
            - 
        """

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

