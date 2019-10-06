#! /env/python

import serial
import os
import time

def get_devices():
    # This function parses the output of a shell command to get the ttyUSBX numbers
    result = os.popen('find /dev/serial/by-id/ -maxdepth 1 -type l -ls | cut -d"/" -f5- ').read()
    print (result)
    values = [line[-1] for line in result.splitlines()]
    return values

def read_answer(serial_d, back=False, ending_ar=None, timeout=None):
    # Reads and analyzes the response

    # Initial variables
    ret = []
    counter = 0

    # Check if using the default values or different
    # this is used to check the connection successful
    if ending_ar:
        endings = ending_ar
    else:
        endings = ["> ", "Done\r\n"]
    
    data = ""
    while not (data in endings):
        data = serial_d.readline().decode('ascii')
        ret.append(data)
        # Prints the received data
        print(data, end="")

        # It checks that counter is a value and the condition
        if timeout and counter>timeout:
            # If we are over the timeout we will send \n to wake up the cli
            serial_d.write(("\n").encode())
            return

        counter = counter + 1
        
    if back:
        return ret

def send_command(serial_d, command, back=False, ending_ar=None, timeout=None):
    # Sends command and reads the response
    serial_d.write((command+"\n").encode())
    return read_answer(serial_d, back, ending_ar, timeout)


if __name__ == '__main__':

    usbs = get_devices()

    commissioner = serial.Serial('/dev/ttyUSB'+usbs[0], 115200, timeout=0.5)
    joiner = serial.Serial('/dev/ttyUSB'+usbs[1], 115200, timeout=0.5)

    read_answer(joiner, timeout=4)
    send_command(joiner, "factoryreset", timeout=3)
    time.sleep(0.5)
    read_answer(commissioner, timeout=4)
    send_command(commissioner, "factoryreset", timeout=3)

    # initialize the commissioner
    init_commands = [
        "dataset init new",
        "dataset",
        "dataset commit active",
        "panid 0xdead",
        "ifconfig up",
        "thread start",
        "ipaddr"]

    for command in init_commands:
        send_command(commissioner, command)

    # get the eui64 from the joiner
    commands = send_command(joiner, "eui64", back=True)
    euid = commands[2][:-2]

    time.sleep(1)
    send_command(joiner, "scan")
    read_answer(joiner)

    send_command(commissioner, "commissioner start")
    time.sleep(0.5)
    send_command(commissioner, f"commissioner joiner add {euid} AAAA")
    
    time.sleep(0.5)
    send_command(joiner, "ifconfig up")
    send_command(joiner, "panid 0xdead")
    send_command(joiner, "joiner start AAAA")

    # scan the network
    send_command(joiner, "scan")
    read_answer(joiner)

    # Open the commissioner's udp port
    send_command(commissioner, "udp open")
    send_command(commissioner, "udp bind :: 1212")

    ips = send_command(commissioner, "ipaddr", back=True)
    send_ip = ips[1][:-2]

    print("Waiting for the joiner answer...")
    try:
        read_answer(joiner, ending_ar=["Join success\r\n"])
    except:
        print("Stopped by the user!")
    
    send_command(joiner, "thread start")

    send_command(joiner, "udp open")
    send_command(joiner, f"udp connect {send_ip} 1212")


    os.system(f"gnome-terminal -e 'python -m serial.tools.miniterm /dev/ttyUSB{usbs[0]} 115200'")
    os.system(f"gnome-terminal -e 'python -m serial.tools.miniterm /dev/ttyUSB{usbs[1]} 115200'")