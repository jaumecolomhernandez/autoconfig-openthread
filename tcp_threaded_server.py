import socket
import threading
import socketserver

import yaml
import threading
import logging
import sys

sys.path.append('src/')
import src.ot_functions as ot
from src.manager import DeviceManager

# TODO: Pass PAEManager as reference
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # Read request content
        data = str(self.request.recv(1024), 'ascii')
        
        # Log
        log.info(f'Received:{data}|From:{self.client_address}')

        # Manager callback
        PAEManager.handle_request(data)

        # Create and send response
        response = bytes(f"{data.upper()}",'ascii')
        self.request.sendall(response)

# TODO: Overwrite handler call function to pass PAEManager as object, and logger or maybe inherit from it
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, conect_tuple, request_h):
        # Example overload
        super().__init__(conect_tuple, request_h)
        self.object = 2    
    pass

def run_server():
    HOST, PORT = "localhost", 12344

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

        server.serve_forever()


if __name__ == "__main__":

    file = open("debug_config.yaml", 'r') 
    config = yaml.safe_load(file)

    # Main object
    PAEManager = DeviceManager(config)

    # Get a logger
    log = logging.getLogger("Server")

    # And start server
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # TODO: Attach HTPP server (maybe flask) 

    print("This thing keeps working")