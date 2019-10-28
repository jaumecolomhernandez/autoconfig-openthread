import logging
import yaml

def main():

    # Read the configuration file
    file = open("config.yaml", 'r') 
    config = yaml.safe_load(file)

    # Create a custom logger, defining from which level the logger will handle errors
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create handlers. One to display by console, another to writte on a file
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('file.log', mode='w')
    
    # Defining from which level each handler handle errors
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.INFO)

    # Read the format from de config.yalm and create a Formatter
    format = logging.Formatter(config['logger']['format'],  datefmt='%m/%d/%Y %I:%M:%S %p')
    
    # Add the Formatter to the handlers
    c_handler.setFormatter(format)
    f_handler.setFormatter(format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
