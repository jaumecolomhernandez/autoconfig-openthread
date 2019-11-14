import logging
import time

log = logging.getLogger(__name__)

# TODO: Implement function to get state from the devices. i.e. parsing the router and child functions
# TODO: Think about other common use functions and implement them 

def initialize_commissioner(device):
    """ Initializes the board with the necessary commands """

    # initializer commands
    init_commands = [
        "dataset init new",
        "dataset",
        "dataset commit active",
        "panid 0xdead",
        "ifconfig up",
        "thread start",
        "ipaddr",
    ]
    # Call every command
    for command in init_commands:
        device.send_command(command)

    device.isCommissioner = True

def authenticate(commissioner, joiner):
    """ Authenticates a joiner device in the commissioner network 
        Params:
        - commissioner: Device object
        -
        Returns:
        - 
    """

    if not commissioner.isCommissioner:
        log.error('{commissioner.name} is not a Commissioner')

    # TODO: Further comment the function

    # get the eui64 from the joiner
    commands = joiner.send_command("eui64", back=True)
    euid = commands[2][:-2]

    time.sleep(0.5)
    joiner.send_command("scan")
    joiner.read_answer()

    commissioner.send_command("commissioner start")
    time.sleep(0.5)
    commissioner.send_command(f"commissioner joiner add {euid} AAAA")

    time.sleep(0.5)
    joiner.send_command("ifconfig up")
    joiner.send_command("panid 0xdead")
    joiner.send_command("joiner start AAAA")

    # scan the network
    joiner.send_command("scan")
    joiner.read_answer()

    log.info('Waiting for the joiner answer...')
    try:
        joiner.read_answer(ending_ar=["Join success\r\n"])
    except:
        log.warning('Stopped by the user!')
        # print("Stopped by the user!")

    joiner.send_command("ifconfig up")
    joiner.send_command("thread start")

def open_udp_communication(receiver):
    """ """
    # Open the commissioner's udp port
    receiver.send_command("udp open")
    receiver.send_command("udp bind :: 1212")

    ips = receiver.send_command("ipaddr", back=True)
    send_ip = ips[1][:-2]

    return send_ip

def udp_connect(send_ip, sender):
    """ """
    sender.send_command("udp open")
    sender.send_command(f"udp connect {send_ip} 1212")

def reset_device(device):
    """ Calls factoryreset method on the board """
    device.read_answer(timeout=4)
    device.send_command("factoryreset", timeout=3)