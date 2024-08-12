import json
import logging

class custom_logger:
   
    # In-memory log storage
    logs = []
    log_limit = 100

    @staticmethod
    def info(message, tracking_code):
        logging.info(message)
        custom_logger.add_to_memory_logs('INFO', message, tracking_code)
   
    @staticmethod
    def error(message, tracking_code):
        logging.error(message)
        custom_logger.add_to_memory_logs('ERROR', message,  tracking_code)

    @staticmethod
    def add_to_memory_logs(level, message, tracking_code):
        log_entry = {
            'tracking_code': tracking_code,
            'time': logging.Formatter('%(asctime)s').format(logging.LogRecord('custom_logger', logging.INFO, '', 0, '', '', '')),
            'level': level,
            'message': message
        }
        custom_logger.logs.append(log_entry)
        if len(custom_logger.logs) > custom_logger.log_limit:
            custom_logger.logs.pop(0)

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
