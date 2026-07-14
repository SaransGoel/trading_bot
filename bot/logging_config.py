import os
import logging
import sys

def setup_logger():
    """
    Configures the root logger to output to both the console and a log file.
    Creates a 'logs' directory if one does not exist.
    """
    # Create a logs directory in the project root
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, "trading_bot.log")

    # Define the format for the logs
    log_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File Handler: writes all logs (INFO and above) to the file
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    # Console Handler: outputs logs to the terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)

    # Get the root logger and add the handlers
    root_logger = logging.getLogger()
    
    # Prevent adding handlers multiple times if initialized more than once
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    return root_logger