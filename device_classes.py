from abc import ABC, abstractmethod
from os import system
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
        self.logger = logging.getLogger(__name__)
    
    def __str__(self):
        if self.isCommissioner:
            return(f"{self.name} Commissioner")
        else:
            return(f"{self.name} Joiner")

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def send_command(self):
        """"""
        pass

    @abstractmethod
    def read_answer(self):
        """"""
        pass

    def reset(self):
        self.send_command


class USBDevice(Device):
    """ Implementation of the Device class for USB connected platforms. """

    def __init__(self, id, name, obj):
        super().__init__(id, name, obj)

    def send_command(self, command, back=False, ending_ar=None, timeout=None):
        # Sends command and reads the response
        self.obj.write((command + "\n").encode())
        return self.read_answer(back, ending_ar, timeout)

    def read_answer(self, back=False, ending_ar=None, timeout=None):
        """ Implementation of the read_answer function. Reads the answer and
            analyzes the response.
            Params:
            - 
            -
            -
            Returns:
            - 
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
        """"""
        system(
            f"gnome-terminal -e 'python -m serial.tools.miniterm /dev/ttyUSB{self.id} 115200'"
        )


class HTTPDevice(Device):
    """ Implementation of the Device class for HTTP controlled platforms. """

    def __init__(self, id, name, obj):
        super().__init__(id, name, obj)

    def send_command(self):
        pass

    def read_answer(self):
        pass


class MockDevice(Device):
    """ Implementation of the Device class for development purposes. """

    def __init__(self, id, name, obj):
        """ """
        super().__init__(id, name, obj)

    def send_command(self, command, back=False, ending_ar=None, timeout=None):
        """ """
        self.logger.info(f"{self.name} - Sent command: {command}")
        # TODO: complete the data structures to closely relate the real ones
        # TODO: add random delays to better simulate a real device
        if command == "eui64":
            return "1234234"
        if command == "ipaddr":
            return "89:34:54:ab:23:ee"
        pass

    def read_answer(self, back=False, ending_ar=None, timeout=None):
        """ """
        pass

    def terminal(self):
        """ """
        self.logger.info(f"{self.name} - There's no terminal for {self.name} device.")
