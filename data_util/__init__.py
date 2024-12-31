"""Initialise logging for the package"""

import logging

# Create the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logging level for this logger

# Create handlers
file_handler = logging.FileHandler("utility.log")
stream_handler = logging.StreamHandler()  # Handler for console output

# Create formatters and add them to handlers
formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)  # Add console handler
