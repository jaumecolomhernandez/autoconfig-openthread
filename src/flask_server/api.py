# IMPLEMENTACIÓ DE UNA API SUPER DUMB AMB PYTHON I FLASK. S'HA DE MILLORAR L'ESTAT GLOBAL

from flask import Flask, Blueprint, request, current_app

api_bp = Blueprint('api', __name__)

@api_bp.route("/api", methods=['GET', 'POST'])
def home_api():
    return "Welcome to PAEManager's API :)"

@api_bp.route("/api/devs", methods=['GET', 'POST'])
def get_devs():
    """ RETURNS CURRENT LIST OF DEVICES
    """
    ## AQUI SEGONA PART DEL HACK CUTRE PER A ACCEDIR A ESTAT GLOBAL EN FLASK
    ## Repetint les mateixes paraules que a init_app_old(), s'ha de pensar una manera 
    ## elegant aka correcta de fer això. Mirar app_context.
    ## Article que pot ser interessant: https://hackingandslacking.com/demystifying-flasks-application-context-c7bd31a53817
    return str(current_app.manager.devices)

@api_bp.route("/api/status", methods=['GET', 'POST'])
def get_status():
    """ RETURNS STATUS OF SERVER
    """
    return "Alive"

@api_bp.route("/api/topology", methods=['GET', 'POST'])
def get_topology():
    """ RETURNS TOPOLOGY OF NETWORK
    """
    return current_app.manager.topology

@api_bp.route("/api/topology_test", methods=['GET', 'POST'])
def get_topology_test():
    """ RETURNS TOPOLOGY OF NETWORK
    """
    topology = { 1 : [],
    2 : [1],
    3 : [1],
    4 : [1]
    }
    return topology

@api_bp.route("/api/whatismyip", methods=['GET', 'POST'])
def get_remote_ip():
    """ RETURNS IP OF REQUEST
    """
    return str(request.remote_addr)

@api_bp.route("/api/inforequest", methods=['GET', 'POST'])
def get_info_request():
    """ RETURNS REQUEST ARGS
    """
    print(request)
    return "This is everything request object got: "+str(dir(request))

@api_bp.route("/api/addmeimadevice", methods=['GET', 'POST'])
def add_new_dev():
    """ Adds a new device
    """
    current_app.manager.add_HTTPDevice(request.remote_addr)
    return "Succesfully added a new device guys!"

@api_bp.route("/api/get_history/<dev_id>", methods=['GET', 'POST'])
def get_hist(dev_id):   
    """ Gets the cmd history
    """
    print(int(dev_id))
    print(current_app.manager.devices)
    print(current_app.manager.get_device(id_number=int(dev_id)).msg_hist_str)
    return current_app.manager.get_device(id_number=int(dev_id)).msg_hist_str