import os
import json
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load server URLs from environment variable
servers_info_json = os.getenv('SERVERS_INFO_JSON', '{}')
try:
    SERVER_INFO = json.loads(servers_info_json)
except json.JSONDecodeError:
    SERVER_INFO = {}
    logging.error("Error decoding JSON from environment variable 'SERVERS_INFO_JSON'")

# Set up logging
log_file = '/data/htdocs/brapi_flask/app/check_servers.log'
if not os.path.exists(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file))

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_server_status(url):
    try:
        response = requests.get(url, timeout=10)  # Set a timeout for the request
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Request to {url} failed: {e}")
        return False

def update_server_info():
    updated_info = {}
    for server_name, url in SERVER_INFO.items():
        status = check_server_status(url)
        updated_info[server_name] = {
            'server-title': server_name,
            'api-urls': [url + '/brapi/v2/'],  # Append '/brapi/v2/' to the URL
            'auth-required': False,
            'server_status': status
        }
    
    file_path = '/data/htdocs/brapi_flask/app/server_info.json'
    try:
        with open(file_path, 'w') as f:
            json.dump(updated_info, f, indent=4)
        logging.info(f"Server info updated successfully in {file_path}")
    except Exception as e:
        logging.error(f"Error writing server info to JSON file: {e}")

if __name__ == "__main__":
    update_server_info()
