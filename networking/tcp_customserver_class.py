import socket, select, logging

import yaml
import threading
import logging
import sys

# WARNING: THIS IS DEPRECATED CODE. MAY NOT WORK WITH CURRENT STATE

class TCPServer:
    def __init__(self, host, port, paemanager, log):
        """ """
        self.host = host
        self.port = port       
        self.ID = -1
        self.connection = False
        self.server_socket = self.init_server(host, port)

        self.manager = paemanager
        self.log = log
    
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
            open_sockets = self.manager.get_sockets()
            open_sockets.append(self.server_socket)
            
            # Select loop for polling the different sockets For more info ->
            # https://docs.python.org/3.8/library/select.html
            read_sockets, _, _ = select.select(open_sockets, [], [])

            for sock in read_sockets: 
                # In case the server is receiving data it means that there is a new connection
                if(sock == self.server_socket):
                    
                    client_sock, client_addr = self.server_socket.accept() 
                    # Creates new device in the self.manager
                    self.manager.add_TCPDevice(client_sock, client_addr[0], client_addr[1])
                    # todo: Ficar gestio de dispositius connectats, 

                    self.log.info(f"Adding new device {client_addr} to self.manager")
                    client_sock.send(f"Socket {client_addr} added to the server".encode("ascii"))
                    
                # If not, it is an active device
                else:
                    message = self.receive_message(sock)
                    # TODO: Here there is a critical bug. When disconecting a unix client via a ctrl-c
                    # the getpeername() function returns error after a few empty responses, thus 
                    # breaking the app. This needs to be fixed 
                    add = sock.getpeername()
                    if len(message) == 0:
                        # Case null error
                        self.manager.handle_request(message, add)
                    else:
                        self.log.info(f"Received: {message} from {add}")
                        #todo: canviar lu de la ID per aqui. Mirar com canviar el device des d'aqui
                        self.manager.handle_request(message, add)

