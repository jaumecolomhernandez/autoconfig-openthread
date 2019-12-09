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
    
    def decode_msg(self, msg):
        args = msg.decode().split('|')
        #print(f"Decoded message -> Header: '{args[1]}' Payload: '{args[2]}'")
        if len(args) < 3:
            print("Bad formatted message")
            return "E", "RROR"
        return args[1], args[2]
        
    def send_message(self, message, addr, flags=''):
        """ """
        return self.server_socket.sendto(f'|{flags}|{message}|'.encode(), addr) 
    
    def handler(self, message, flags, addr):
        """ """
    
        self.log.info(f"Received message '{flags}' '{message}' from {addr}")
        
        # TODO: Afegir que manager retorni flags també
        # flags, message = self.manager.UDPhandle_request(message, addr)
        # Per a que funcioni s'han de canviar tots els return de 
        # UDP_HandleRequest de manager.py
        # Exemple: return '', f"Instruction unknown ({message})"
        message_r = self.manager.UDPhandle_request(message, flags, addr)
        
        return message_r
        

    def run_forever(self):
        """ """
        while True:
            # Receives message from available socket 
            raw_message, addr = self.server_socket.recvfrom(1024)
            
            # Send things
            flags, message = self.decode_msg(raw_message)

            # Handles response
            message_r = self.handler(message, flags, addr)

            # print(flags, message_r)
            # Sends response back (ALWAYS ?)
            if message_r:
                self.send_message(message_r, addr)