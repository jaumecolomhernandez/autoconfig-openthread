import socket, select, logging

import yaml
import threading
import logging
import sys

sys.path.append('src/')
from src.manager import DeviceManager

sys.path.append('flask_server/')
from flask_server.main import app as FlaskServer
from flask_server.main import init_app_old

from src.tcp_customserver_class import TCPServer

                    
#        
if __name__ == "__main__":

    file = open("debug_config.yaml", 'r') 
    config = yaml.safe_load(file)

    # Main object
    PAEManager = DeviceManager(config)

    # Server object/s
    internal_server = TCPServer('localhost', 12342, PAEManager, logging.getLogger("TCPServer"))

    external_server = FlaskServer  # TODO: Make this a class # TODO Think new way of initializing this
    init_app_old(PAEManager, logging.getLogger("FlaskServer"))

    # TODO: (OPENTHREAD) Test the case where there is no range and transmission involves a two hop travel

    # Get a logger
    log = logging.getLogger("MAIN")
    log.info("LOG STARTED")


    # And start server/s
    iserver_thread = threading.Thread(target=internal_server.run_forever)
    iserver_thread.start()

    eserver_thread = threading.Thread(target=external_server.run)
    eserver_thread.start()
    #external_server.run(debug=False)

    #print("This thing keeps working")
