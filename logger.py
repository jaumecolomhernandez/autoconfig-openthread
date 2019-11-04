import logging
import yaml

def init():

    # Read the configuration file
    file = open("config.yaml", 'r') 
    config = yaml.safe_load(file)

    # Create a custom logger, defining from which level the logger will handle errors
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a handler to display by console
    handler = logging.StreamHandler()
    
    # Defining the level of the handler, reading from the config.yalm
    handler.setLevel(config['logger']['level'])

    # Read the format from de config.yalm and create a Formatter
    format = logging.Formatter(config['logger']['format'],  datefmt='%m/%d/%Y %I:%M:%S')
    
    # Add the Formatter to the handler
    handler.setFormatter(format)

    # Add handler to the logger
    logger.addHandler(handler)
