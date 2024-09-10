import logging

LOG_FILE = ''

def read_log_file(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('log_file='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        logging.error(f"Properties file not found: {file_path}")
    except Exception as e:
        logging.error(f"Error reading properties file: {e}")
    return None

log_file_location = read_log_file('/etc/properties/videogen.properties')
if log_file_location:
    LOG_FILE = log_file_location
else:
    raise ValueError("Log file is not available. Please check the properties file.")

logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',                  # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    level=logging.DEBUG            # Log level (DEBUG for detailed logs)
)
