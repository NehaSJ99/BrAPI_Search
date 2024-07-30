import pymongo
import requests
import logging
from datetime import datetime, timedelta
import os
import time
import json
from dotenv import load_dotenv  # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_server_info():
    server_info = {}
    
    # List of environment variable names for server info
    #env_vars = ['SERVER_INFO_T3_WHEAT', 'SERVER_INFO_T3_BARLEY', 'SERVER_INFO_T3_OAT']
    env_vars = ['SERVER_INFO_URGI']
    
    for var in env_vars:
        server_info_json = os.getenv(var, '{}')
        
        if server_info_json:
            try:
                # Extract server name parts and reconstruct the server name
                server_name_parts = var.split('_')[2:]  # Extract server name parts
                server_name = '/'.join(server_name_parts)  # Reconstruct server name
                
                # Load JSON data
                server_data = json.loads(server_info_json)
                server_info[server_name] = server_data
                
            except json.JSONDecodeError:
                print(f"Error decoding JSON from environment variable {var}")
                logging.error(f"Error decoding JSON from environment variable {var}")
    
    return server_info

def get_log_file_path(server_name):
    log_directory = 'upsert_data'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    log_file_name = f'upsert_data_{server_name.lower().replace("/", "_")}.log'
    return os.path.join(log_directory, log_file_name)

def configure_logger(server_title):
    log_file = get_log_file_path(server_title)
    # Clear existing log file before each server's upsertion
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Configure logging for the current server
    logger = logging.getLogger(server_title)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.handlers = []  # Clear any existing handlers
    logger.addHandler(handler)
    return logger

def fetch_data(api_url):
    page = 0
    total_pages = 1  # Initialize with 1 to enter the loop
    all_data = []
    total_count = 0  # Initialize total_count
    data_fetched = 0  # Initialize data_fetched
    delay = 5  # Set the delay time in seconds
    
    while page < total_pages:
        print(f'Fetching page: {page}')
        url = f"{api_url}?page={page}&pageSize=1000"
        print(f'URL: {url}')
        try:
            response = requests.get(url, verify=False)  # Disable SSL certificate verification
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            print(response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                page_data = data.get('result', {}).get('data', [])
                all_data.extend(page_data)
                data_fetched = len(all_data)
                
                total_pages = data.get('metadata', {}).get('pagination', {}).get('totalPages', total_pages)
                total_count = data.get('metadata', {}).get('pagination', {}).get('totalCount', total_count)
                page += 1
                print(f'Total pages: {total_pages}')
                print(f'Total count: {total_count}')
                
                # Stop fetching if all pages are retrieved
                if data_fetched >= total_count:
                    break

                # Add a delay before fetching the next page
                time.sleep(delay)

            else:
                print(f"Error fetching data: {response.status_code} {response.reason}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data on page {page + 1}: {e}")
            logging.error(f"Error fetching data from {api_url}: {e}")
            return []

    # Check if the total fetched data matches the total count
    if data_fetched == total_count:
        return all_data
    else:
        logging.warning(f"Data count mismatch: Fetched {data_fetched}, Expected {total_count}")
        return []

def insert_data(data, collection_name, logger):
    client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    db = client["brapidata"]
    collection = db[collection_name]

    # Get the count of documents before insertion
    initial_count = collection.count_documents({})
    
    # Add timestamp for new data
    current_time = datetime.now()
    for item in data:
        item["updated_at"] = current_time

    # Insert new data
    result = collection.insert_many(data, ordered=False)
    inserted_count = len(result.inserted_ids)
    
    # Get the count of documents after insertion
    after_insert_count = collection.count_documents({})
    
    print(f'Inserted {inserted_count} documents into: {collection_name}')
    logger.info(f'Inserted {inserted_count} documents into: {collection_name}')
    logger.info(f'Total count before insertion: {initial_count}')
    logger.info(f'Total count after insertion: {after_insert_count}')
    
    return inserted_count

def delete_old_documents(collection_name, logger):
    client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    db = client["brapidata"]
    collection = db[collection_name]

    # Get the count of documents before deletion
    after_insert_count = collection.count_documents({})
    
    # Define the cutoff date for documents to be deleted
    cutoff_date = datetime.now() - timedelta(days=1)
    
    # Delete documents older than the cutoff date
    result = collection.delete_many({"updated_at": {"$lt": cutoff_date}})
    deleted_count = result.deleted_count
    
    # Get the count of documents after deletion
    final_count = collection.count_documents({})
    
    print(f'Deleted {deleted_count} documents from: {collection_name}')
    logger.info(f'Deleted {deleted_count} documents from: {collection_name}')
    logger.info(f'Total count before deletion: {after_insert_count}')
    logger.info(f'Total count after deletion: {final_count}')

def upsert_all_data():
    start_time = time.time()
    logging.info(f'Starting upsertion at {datetime.now()}')

    server_info = load_server_info()

    try:
        for server, info in server_info.items():
            server_title = info.get('server-title')
            if not server_title:
                print(f"Error: Missing 'server-title' for server '{server}'")
                logging.error(f"Error: Missing 'server-title' for server '{server}'")
                continue
            
            logger = configure_logger(server_title)

            base_name = server_title.replace("/", "_").lower()

            for data_type, api_url in info.get('api-urls', {}).items():
                collection_name = f"{base_name}_{data_type}"
                
                print(f'Fetching data for: {collection_name}')
                logger.info(f'Fetching data for: {collection_name}')
                
                data = fetch_data(api_url)
                
                if data:
                    print(f'Inserting data for: {collection_name}')
                    logger.info(f'Inserting data for: {collection_name}')
                    inserted_count = insert_data(data, collection_name, logger)
                    
                    if inserted_count > 0:
                        print(f'Deleting old documents from: {collection_name}')
                        logger.info(f'Deleting old documents from: {collection_name}')
                        delete_old_documents(collection_name, logger)
                    else:
                        print(f'No new data to insert for: {collection_name}')
                        logger.warning(f'No new data to insert for: {collection_name}')
                else:
                    print(f'No data fetched for: {collection_name}')
                    logger.warning(f'No data fetched for: {collection_name}')

    except Exception as e:
        logging.error(f"Error during upsertion: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info(f'Completed upsertion at {datetime.now()}')
    logging.info(f'Total time taken: {elapsed_time:.2f} seconds')
    print(f'Total time taken: {elapsed_time:.2f} seconds')

if __name__ == "__main__":
    upsert_all_data()
