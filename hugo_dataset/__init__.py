import logging

# Create a logger
logger = logging.getLogger("hugo_dataset")

# Set the logging level
logger.setLevel(logging.DEBUG)  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

try:
    # Add RichHandler for beautifully formatted output
    from rich.logging import RichHandler
    rich_handler = RichHandler(rich_tracebacks=True)  # Enable rich tracebacks
    logger.addHandler(rich_handler)

    # Optional: Customize format
    formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(formatter)
except:
    pass

