import pymongo
import requests

def write_data(mydict):
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["brapidata"]
    mycol = mydb["t3_wheat_germplasm"]
    x = mycol.insert_many(mydict)
    # Print list of the _id values of the inserted documents
    print(x.inserted_ids)

def read_data():
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["brapidata"]
    mycol = mydb["t3_wheat_germplasm"]
    x = mycol.find()
    for id in x:
         print(id)
    
def drop_collection():
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient["brapidata"]
    mycol = mydb["t3_wheat_germplasm"]
    mycol.drop()

def get_germplasm_data(base_url):
    page = 0
    total_pages = 2  # Initialize with 1 to enter the loop
    germplasm_data = []

    while page < total_pages:
        print(f'into the page:{page}')
        url = f"{base_url}germplasm?page={page+1}"
        print(f'url : {url}')
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            # Get JSON response
            data = response.json()
            
            # Extract the relevant data
            page_data = data.get('result', {}).get('data', [])
            germplasm_data.extend(page_data)
            
            # Update total pages based on the response
            # total_pages = data.get('metadata', {}).get('pagination', {}).get('totalPages', total_pages)
            page += 1
            print(f'total pages : {total_pages}')

        except requests.exceptions.RequestException as e:
            print(f"Error fetching germplasm data on page {page+1}: {e}")
            break

    return germplasm_data

base_url = 'https://cassavabase.org/brapi/v2/'
#germplasm_data = get_germplasm_data(base_url)
#write_data(germplasm_data)
read_data()
#drop_collection()
