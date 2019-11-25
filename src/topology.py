import threading, os, logging
import ot_functions as ot

log = logging.getLogger(__name__)

def all_to_one(devices, commissioner_id):
    """ Creates all to one topology
        Returns:
        - adjacency_dict : dictionary with the pairs id:[connected_ids]
            all the data are integers    
    """
    # Length check for the topology
    if len(devices) < 2:
        log.error('Can not create topology if < 2 devices')
        return

    # It is better to use the ids as they are integers and provide a
    # way to decouple the data structures (by means of a join). We exclude 
    # the commissioner from the list of ids.
    ids = [ device.id for device in devices if device.id != commissioner_id]

    # The commissioner is a defined id in the Yaml configuration
    commissioner_id = commissioner_id

    # Create adjacency list with all the current devices connectating
    # to the commissioner
    adjacency_dictionary = {idn: [commissioner_id] for idn in ids}

    # we add the entry for the commissioner and it's ready
    adjacency_dictionary[commissioner_id] = []

    return adjacency_dictionary

def apply_topology(manager):
    """ Applies the topology set in manager.topology to the boards connected 
        Params:
        - manager: (DeviceManager) contains all the info needed to apply the state
    """

    # TODO: Implement manner to check if the nodes are already connected
    
    # Check that there's a topology set
    if not manager.topology:
        log.error('There is no topology specified! Please indicate one and call the method again')
        return
    
    # A list of all the threads joining the network
    joiners=list()
    
    # Iterate through all the items in the adjacency dictionary, take
    # into account that the values are the Device id, so to act on them
    # it is needed to get the Device object
    for key, values in manager.topology.items():
        # Get device by id
        joiner = manager.get_device(id_number=key)

        for device_id in values:
            # Get device by id
            commissioner = manager.get_device(id_number=device_id)

            # Check that the device is initalized to work as a commissioner
            if commissioner.isCommissioner:
                ot.initialize_commissioner(commissioner)

            # Authenticate both devices
            joiners.append(threading.Thread(target=ot.authenticate, args=(commissioner, joiner)))
            joiners[-1].start()
            # self.authenticate(commissioner, joiner)
    
    # Wait for all the nodes to join the network
    # join() is used to wait for a thread to finish
    [joiner.join() for joiner in joiners]

    log.info('All devices connected')



def plot_graph(manager):
    """ Plots the topology 
        It generates an image with the networkx library, stores it
        and opens the image.
    """
    #log = logging.getLogger('matplotlib')
    #log.setLevel(logging.ERROR)
    
    # Necessary imports
    from networkx import parse_adjlist, draw
    from matplotlib.pyplot import figure, savefig

    # Vars
    lines = []
    
    # networkx needs a list with the following structure:
    # ['1 connected nodes', '2 connected nodes', ... ]
    # It has a string for every node containing the chronological order
    # the connections it has.
    # Example all to one structure:
    # ['1 3', '2 3', '3 ']
    # In this example the first two nodes are connected to the 
    # third node. Note that the index starts at one
    for key,values in manager.topology.items():
        # Generate the connections string
        intermed = ", ".join([str(j+1) for j in values])
        lines.append(f'{key+1} {intermed}')
    print(lines)
    # Create networkx Graph from the adjacency list
    G = parse_adjlist(lines, nodetype = int)
    print(G.nodes())
    print(manager.devices)
    # Get a dict with the labels of every node
    labels = dict((n, manager.get_device(id_number=(n-1)).name) for n in G.nodes())
    print(labels)
    # Asign a colour to each node. If is a commissioner node, blue will be assigned.
    # If is a joiner, green will be assigned
    colours=[]
    for n in G.nodes():
        if manager.get_device(id_number=(n-1)).isCommissioner:
            colours.insert(n,'b')
        else:
            colours.insert(n,'g')
    
    # Larger figure size
    # figure(3,figsize=(12,12))
    
    # Draw graph
    draw(G, node_size=5000, with_labels=True, font_weight='bold', labels=labels, node_color=colours)
    
    # Export image and open with eog
    savefig(manager.config['topology']['file_name'])
    os.system(f"eog {manager.config['topology']['file_name']} &")