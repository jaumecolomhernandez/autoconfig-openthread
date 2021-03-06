from abc import ABC, abstractmethod
from os import system
from datetime import datetime
import logging

class Device(ABC):
    """ Abstract class for the Device object. It exposes a common interface 
    for being used by the main program. It is further implemented
    by the USBDevice, HTTPDevice and MockDevice. """

    # TODO: Complete the method docstrings
    
    # TODO __str__
    @abstractmethod
    def __init__(self, id, name, obj):
        """"""
        self.id = id
        self.name = name
        self.obj = obj
        self.isCommissioner = False
        # Create a logger
        self.logger = logging.getLogger(name)
        self.msg_hist = []
        self.msg_hist_str = "MESSAGES RECEIVED : \n"
        self.addr_str = ''
        self.port = ''

    @abstractmethod
    def send_command(self):
        """"""
        pass

    @abstractmethod
    def read_answer(self):
        """"""
        pass

    def msg_list_to_str(self):
        tstamp = datetime.now().strftime('%H:%M:%S.%f')[:-4]
        s = f">> {tstamp} - {self.msg_hist[-1]} \n"  
        self.msg_hist_str += s

    def reset(self):
        self.send_command


class USBDevice(Device):
    """ Implementation of the Device class for USB connected platforms. """

    def __init__(self, id, name, obj):
        super().__init__(id, name, obj)

    def send_command(self, command, back=False, ending_ar=None, timeout=None):
        """ Sends command and reads the response """
        self.obj.write((command + "\n").encode())
        self.logger.info(f"Sent command: {command}")
        return self.read_answer(back, ending_ar, timeout)

    def read_answer(self, back=False, ending_ar=None, timeout=None):
        """ Implementation of the read_answer function. Reads the answer and
            analyzes the response.
            Params:
            - back: (bool) flag to return the received strings
            - ending_ar: (list) list containing custom endings
            - timeout: (int) tries before receiving message. Each try is 0.5 
            (defined in the pyserial configuration)
            Returns:
            (if back == True)
            - mes: (list) list containing the received strings from the serial 
        """

        # Initial variables
        ret = []  # Contains the response in case needed to return the data
        counter = 0  # Counts the number of timeouts (used if timeout flag is 1)

        # If specific ending indicated (ending_ar) changes the condition
        endings = ending_ar if ending_ar else ["> ", "Done\r\n"]

        data = ""
        # Iterate until we read the desired response
        while not (data in endings):
            # Read line from the serial port
            try:
                data = self.obj.readline().decode("ascii")
            except Exception as e:
                self.logger.error(f"There has been a problem with the string decodification", exc_info=e)


            # Store data if needed (back flag)
            ret.append(data)
            # Print the received data
            print(data, end="")

            # It checks that counter is a value and the condition
            if timeout and counter > timeout:
                # If we are over the timeout we will send \n to wake up the cli
                self.obj.write(("\n").encode())
                # And then return
                return

            # timeout counter increase
            counter = counter + 1
        if back:
            return ret

    def terminal(self):
        """ Opens terminal for each device """
        system(
            f"gnome-terminal -e 'python -m serial.tools.miniterm /dev/ttyUSB{self.id} 115200'"
        )

# TODO: Decouple the device logic from the manager

class TCPDevice(Device):
    """ Implementation of the Device class for TCP controlled platforms. """
    def __init__(self, id, name, obj, addr):
        super().__init__(-1, name, obj)
        self.addr = addr 
        self.connexion = False

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def send_command(self, command):
        """ Sends message through its own socket """
        return self.obj.send(command.encode('ascii'))

    def read_answer(self):
        """ALL THE RECEIVING IS DONE THROUGH THE UDPSERVER"""
        pass

class UDPDevice(Device):
    """ Implementation of the Device class for TCP controlled platforms. """
    def __init__(self, id, name, obj, addr):
        super().__init__(-1, name, obj)
        self.addr = addr
        self.addr_str = addr[0]
        self.connexion = False
        self.commands = []
        self.port = addr[1]

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def send_command(self, command, flags=''):
        """ Sends message through the socket server """
        # Only append if user expressed it # PROTOCOL!
        if 'C' in flags:
            self.commands.append(command)
        return self.obj.sendto(f'|{flags}|{command}|'.encode(), self.addr)

    def read_answer(self):
        """ALL THE RECEIVING IS DONE THROUGH THE UDPSERVER"""
        pass

class HTTPDevice(Device):
    """ Implementation of the Device class for HTTP controlled platforms. """
    def __init__(self, id, name, ip):
        super().__init__(id, name, None)
        self.raddr = ip

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def send_command(self, command, flags=''):
        pass

    def read_answer(self):
        pass

class MockDevice(Device):
    """ Implementation of the Device class for development purposes. """

    def __init__(self, id, name, obj):
        """ """
        super().__init__(id, name, obj)
    
    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def send_command(self, command, back=False, ending_ar=None, timeout=None):
        """ Dumb implementation of Mock device """
        self.logger.info(f"Sent command: {command}")
        # TODO: complete the data structures to closely relate the real ones
        # TODO: add random delays to better simulate a real device
        if command == "eui64":
            return "1234234"
        if command == "ipaddr":
            return "89:34:54:ab:23:ee"
        pass

    def read_answer(self, back=False, ending_ar=None, timeout=None):
        """ No implementation """
        pass

    def terminal(self):
        """ No implementation """
        self.logger.warning(f"There's no terminal for {self.name} device.")
