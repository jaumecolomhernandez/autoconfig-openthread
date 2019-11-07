import socket, select, logging

import yaml
import threading
import logging
import sys

sys.path.append('src/')
from src.manager import DeviceManager

class TCPServer:
    def __init__(self, host, port):
        """ """
        self.host = host
        self.port = port       
        self.ID = -1
        self.connection = False
        self.server_socket = self.init_server(host, port)
    
    def init_server(self, host, port):
        """ """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # Sets option to reuse port For more info -> 
        # http://man7.org/linux/man-pages/man7/socket.7.html
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        # Attaches server to specific host and port
        server.bind((host, port))
        # Start listening 
        server.listen(10)  

        return server

    def receive_message(self, socket_client):
        """ """
        return socket_client.recv(1024).decode('ascii')
            
    def send_message(self, sock, message):
        """ """
        return sock.send(message.encode('ascii'))

    def handler(self, message, sock):
        print(message)

    def run_forever(self):
        """ """
        while 1:
            # Gets current sockets in the system
            open_sockets = PAEManager.get_sockets()
            open_sockets.append(self.server_socket)
            
            # Select loop for polling the different sockets For more info ->
            # https://docs.python.org/3.8/library/select.html
            read_sockets, _, _ = select.select(open_sockets, [], [])

            for sock in read_sockets: 
                # In case the server is receiving data it means that there is a new connection
                if(sock == self.server_socket):
                    
                    client_sock, client_addr = self.server_socket.accept() 
                    # Creates new device in the PAEManager
                    PAEManager.add_TCPDevice(client_sock, client_addr[0], client_addr[1])
                    # todo: Ficar gestio de dispositius connectats, 

                    log.info(f"Adding new device {client_addr} to PAEManager")
                    client_sock.send(f"Socket {client_addr} added to the server".encode("ascii"))
                    
                # If not, it is an active device
                else:
                    message = self.receive_message(sock)
                    add = sock.getpeername()
                    if len(message) == 0:
                        # Case null error
                        PAEManager.handle_request(message, add)
                    else:
                        log.info(f"Received: {message} from {add}")
                        #todo: canviar lu de la ID per aqui. Mirar com canviar el device des d'aqui
                        PAEManager.handle_request(message, add)

                    
                    
#                   
if __name__ == "__main__":

    file = open("debug_config.yaml", 'r') 
    config = yaml.safe_load(file)

    # Main object
    PAEManager = DeviceManager(config)

    # Server object/s
    internal_server = TCPServer('localhost', 12342)
    external_server = None  # TODO: Attach HTPP server (maybe flask) 

    # Get a logger
    log = logging.getLogger("Server")

    log.info("LOG STARTED")

    # And start server
    iserver_thread = threading.Thread(target=internal_server.run_forever)
    iserver_thread.start()


    #print("This thing keeps working")
