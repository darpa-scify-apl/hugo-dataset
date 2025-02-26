import logging

def get_logger(name: str, log_level: str = 'DEBUG') -> logging.Logger:
    """
    Configures and returns a logger instance.

    :param name: The name of the logger.
    :param log_level: The logging level (default is DEBUG).
    :return: Configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger(f"hugo_dataset.{name}")

    # Set the logging level
    logger.setLevel(log_level)  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

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
    return logger
