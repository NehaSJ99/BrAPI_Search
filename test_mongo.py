import pymongo
import requests
from app.BrAPIs import fetch_server_apis

def write_data(mydict, server_name):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["brapidata"]
    mycol = mydb[server_name]
    x = mycol.insert_many(mydict)
    print(f'Data inserted successfully for: {server_name}')
    # Print list of the _id values of the inserted documents
    print(x.inserted_ids)

def read_data(server_name):
    print(server_name)
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["brapidata"]
    mycol = mydb[server_name]
    count_col = mycol.count_documents({})
    print(f'Count of collection: {count_col}')

def drop_collection(server_name):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["brapidata"]
    mycol = mydb[server_name]
    mycol.drop()

def find_data(server_name, data):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["brapidata"]
    mycol = mydb[server_name]
    count = mycol.count_documents({'species': data})
    return count

def get_germplasm_data(base_url):
    page = 0
    total_pages = 1  # Initialize with 1 to enter the loop
    germplasm_data = []

    while page < total_pages:
        print(f'Fetching page: {page}')
        url = f"{base_url}germplasm?page={page + 1}"
        print(f'URL: {url}')
        try:
            response = requests.get(url, verify=False)  # Disable SSL certificate verification
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            if response.status_code == 200:
                # Get JSON response
                data = response.json()
                
                # Extract the relevant data
                page_data = data.get('result', {}).get('data', [])
                germplasm_data.extend(page_data)
                
                # Update total pages based on the response
                # total_pages = data.get('metadata', {}).get('pagination', {}).get('totalPages', total_pages)
                page += 1
                print(f'Total pages: {total_pages}')
            
            else:
                print(f"Error fetching trait: {response.status_code} {response.reason}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching germplasm data on page {page + 1}: {e}")
            break

    return germplasm_data

server_info = fetch_server_apis()

def read_all_data():
    for server in server_info:
        server_name = server_info.get(server, {}).get('server-title')
        read_data(server_name)

def write_all_data():
    for server in server_info:
        server_name = server_info.get(server, {}).get('server-title')
        api = server_info.get(server, {}).get('api-urls', [])[0]

        germplasm_data = get_germplasm_data(api)
        if germplasm_data:
            print(f'Found data for: {server_name}')
            write_data(germplasm_data, server_name)
        else:
            print(f'No data found')

def drop_all_collections():
    for server in server_info:
        server_name = server_info.get(server, {}).get('server-title')
        drop_collection(server_name)

def find_in_all(data):
    for server in server_info:
        server_name = server_info.get(server, {}).get('server-title')
        count = find_data(server_name, data)
        if count > 0:
            print(f'Found {count} records for "{data}" in {server_name}')
        else:
            print(f'No records found for "{data}" in {server_name}')

# Example usage:
# read_all_data()
# write_all_data()
# drop_all_collections()
keyword = input("Enter the keyword to search: ")
find_in_all(keyword)