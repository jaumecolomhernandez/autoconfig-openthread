import logging
import yaml

# Read the configuration file
file = open("config.yaml", 'r') 
config = yaml.safe_load(file)
config['open_terms']

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log', mode='w')
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
format=logging.Formatter(config['logger']['format'],  datefmt='%m/%d/%Y %I:%M:%S %p')
c_handler.setFormatter(format)
f_handler.setFormatter(format)


# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)



