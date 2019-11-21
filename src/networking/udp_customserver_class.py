import socket, select, logging

import yaml
import threading
import logging
import sys


#TODO: Add configuration

class UDPServer:
    def __init__(self, host, port, paemanager, log):
        """ """
        self.host = host
        self.port = port       
        self.ID = -1
        self.connection = False
        self.server_socket = self.init_server(host, port)

        self.log = log
        self.manager = paemanager
    
    def init_server(self, host, port):
        """ """
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        # Sets option to reuse port For more info -> 
        # http://man7.org/linux/man-pages/man7/socket.7.html
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        # Attaches server to specific host and port
        server.bind((host, port))
        # Start listening maybe not needed 
        #server.listen(10)  

        return server

    def receive_message(self, socket_client):
        """ """
        return socket_client.recvfrom(1024)
            
    def send_message(self, message, addr):
        """ """
        return self.server_socket.sendto(message.encode(), addr) 
        

    def handler(self, message, addr):
        self.log.info(f"Missatge rebut -> {message} {addr}")
                    
        message_r = self.manager.UDPhandle_request(message, addr)
        if message_r: 
            return message_r
        else: 
            return "NO ANSWER"

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
                # Receives message from available socket 
                message, addr = self.receive_message(sock)
                # Handles response
                message_r = self.handler(message, addr)
                print(message_r)
                # Sends response back (ALWAYS)
                self.send_message(message_r, addr)