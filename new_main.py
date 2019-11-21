import socket, select, logging

import yaml
import threading
import logging
import sys

sys.path.append('src/')
from src.manager import DeviceManager


            
if __name__ == "__main__":

	file = open("debug_config.yaml", 'r') 
	config = yaml.safe_load(file)

	# Main object
	PAEManager = DeviceManager(config)

	
    #external_server.run(debug=False)

    #print("This thing keeps working")
