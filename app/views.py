from flask import request, render_template, Blueprint, jsonify, json, url_for, redirect
import logging
from logging.handlers import RotatingFileHandler
from .BrAPIClientService import getGermplasmSearch, search_trait, search_trial, getGermplasmPedigree, getGermplasmProgeny
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests


main = Blueprint("main", __name__)

# Initialize MongoDB client
myclient = MongoClient('mongodb://localhost:27017')
if myclient:
    logging.info(f"Connection established with string : {myclient}")
else:
    logging.info("Not abble to established a connection with mongo server")
db = myclient["brapidata"]
#print(db)

#loading the server's info
def load_server_info():
    file_path = 'server_info.json'
    try:
        with open(file_path, 'r') as f:
            server_info = json.load(f)
            logging.info(f"Server info loaded: {server_info}")
        return server_info
    except Exception as e:
        logging.info(f"Error loading server info: {e}")
        return {}

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set log level as needed


@main.route("/", methods=['GET', 'POST'])
def index():
    server_info = load_server_info()
    logging.info(f"Server info: {server_info}")
    #print('*******')
    print(server_info)
    return render_template("index.html", server_info=server_info)

@main.route('/about') 
def aboutPage(): 
    return render_template('about.html') 

@main.route('/contact') 
def contactPage(): 
    return render_template('contact.html')

@main.route("/search", methods=['POST'])
def search():
    server_info = load_server_info()
    search_results = []

    search_param = request.form.get("query")
    selected_servers = request.form.getlist("servers[]")
    search_for = request.form.get("search_for")
    mongo_db = 'brapidata'

    collection_name_list = []
    for server in selected_servers:
        col_name = server.replace("/", "_").lower() + "_" + search_for
        collection_name_list.append((col_name, server))

    logging.info("On the Search Page")
    logging.info(f"Search Query: {search_param}")
    logging.info(f"Selected Servers: {selected_servers}")
    logging.info(f"Search For: {search_for}")
    logging.info(f"Mongo database: {mongo_db}")
    logging.info(f"Collections: {collection_name_list}")

    # Define the search fields for different search types
    search_fields = {
        "traits": ["traitName", "traitDbId"],
        "germplasm": ["genus", "germplasmDbId", "germplasmName", "species", "defaultDisplayName", "accessionNumber","synonyms"],
        "trials": ["trialName", "trialDbId", "programName", "programDbId", "commonCropName"]
    }

    all_results = []
    total_count = 0

    # Fetch data from MongoDB based on the input
    if collection_name_list:
        for collection_name, server in collection_name_list:
            collection = db[collection_name]

            if search_for in search_fields:
                query_conditions = [{field: {"$regex": search_param, "$options": "i"}} for field in search_fields[search_for]]
                results = collection.find({"$or": query_conditions})

                # Add results to the list
                for result in results:
                    if 't3_barley' in collection_name:
                        server_title = server_info['T3/Barley']['server-title']
                        base_url = server_info['T3/Barley']['api-urls'][0]
                    elif 't3_oat' in collection_name:
                        server_title = server_info['T3/Oat']['server-title']
                        base_url = server_info['T3/Oat']['api-urls'][0]
                    elif 't3_wheat' in collection_name:
                        server_title = server_info['T3/Wheat']['server-title']
                        base_url = server_info['T3/Wheat']['api-urls'][0]
                    elif 'gatersleben_germplasm' in collection_name:
                        server_title = server_info['IPK Gatersleben']['server-title']
                        base_url = server_info['IPK Gatersleben']['api-urls'][0]
                    elif 'urgi' in collection_name:
                        server_title = server_info['URGI']['server-title']
                        base_url = server_info['URGI']['api-urls'][0]
                    elif 'graingenes' in collection_name:
                        server_title = server_info['GrainGenes']['server-title']
                        base_url = server_info['GrainGenes']['api-urls'][0]
                    else:
                        server_title = server
                        base_url = ''  # Default base URL if not found in the dictionary

                    result['server_name'] = server_title
                    result['base_url'] = base_url
                    result['_id'] = str(result['_id'])  # Convert ObjectId to string for JSON serialization
                    all_results.append(result)

    # Return all results without pagination
    return jsonify({
        "results": all_results,
        "total_count": len(all_results),
        "total_pages": 1,  # Since we're handling pagination on the client side
        "current_page": 1
    })


@main.route("/details/<string:detail_type>/<string:detail_id>")
def details(detail_type, detail_id):
    logging.info(f"Detail Type: {detail_type}, Detail ID: {detail_id}")
    base_url = request.args.get("base_url")
    server_name = request.args.get("server_name")
    print(f'base_url:{base_url}')
    
    if detail_type and detail_id and base_url:
        if detail_type == "germplasm":
            searched_results_germplasm = getGermplasmSearch(detail_id, base_url)
            print(f'searched_results_germplasm in Details page : {searched_results_germplasm}')
            if searched_results_germplasm:
                searched_results_germplasm['base_url'] = base_url  # Ensure base_url is set for each result
                
                # Check if pedigree endpoint exists
                if check_endpoint_exists(base_url, f"{detail_id}/pedigree"):
                    pedigree_info = getGermplasmPedigree(detail_id, base_url)
                    if pedigree_info:
                        print(f'pedigree_info : {pedigree_info}')
                        has_pedigree = bool(pedigree_info.get('siblings'))
                        searched_results_germplasm['pedigree'] = 'Yes' if has_pedigree else 'No'
                    else:
                        searched_results_germplasm['pedigree'] = 'No'
                else:
                    searched_results_germplasm['pedigree'] = 'Not Available'

                # Check if progeny endpoint exists
                if check_endpoint_exists(base_url, f"{detail_id}/progeny"):
                    progeny_info = getGermplasmProgeny(detail_id, base_url)
                    if progeny_info:
                        has_progeny = bool(progeny_info.get('progeny'))
                        searched_results_germplasm['progeny'] = 'Yes' if has_progeny else 'No'
                    else:
                        searched_results_germplasm['progeny'] = 'No'
                else:
                    searched_results_germplasm['progeny'] = 'Not Available'

                logging.info(f"Germplasm Details found for : {detail_id}")
                logging.info(f'Details ; {searched_results_germplasm}')
                logging.info("3. Displaying details on Details page")
                return render_template("details.html", sample=searched_results_germplasm, detail_type=detail_type, server_name=server_name, 
                                       has_pedigree=searched_results_germplasm['pedigree'], has_progeny=searched_results_germplasm['progeny'])
        
        elif detail_type == "trait":
            searched_results = search_trait(detail_id, base_url)
        elif detail_type == "trial":
            searched_results = search_trial(detail_id, base_url)
        else:
            logging.warning("Invalid detail type")
            return render_template("404.html")

        if searched_results:
            logging.info(f"Germplasm Details found for : {detail_id}")
            logging.info(f'Details ; {searched_results}')
            logging.info("3. Displaying results on Details page")
            return render_template("details.html", sample=searched_results, detail_type=detail_type, server_name=server_name)
    
    logging.warning("Sample not found")
    return render_template("404.html")

@main.route("/germplasm/<germplasm_id>/pedigree")
def germplasm_pedigree(germplasm_id):
    logging.info(f"Germplasm Pedigree ID: {germplasm_id}")
    base_url = request.args.get("base_url")
    server_name = request.args.get("server_name")
    germplasm_name = request.args.get("germplasm_name")
    if germplasm_id and base_url:
        pedigree_info = getGermplasmPedigree(germplasm_id, base_url)
        if pedigree_info:
            logging.info(f"Pedigree Information found for : {germplasm_id}")
            logging.info(pedigree_info)
            logging.info(f"Going on pedigree page")
            return render_template("pedigree.html", pedigree=pedigree_info, detail_type='germplasm', detail_id=germplasm_id, germplasm_name=germplasm_name, base_url=base_url, server_name=server_name)
    
    logging.warning("Pedigree information not found")
    return render_template("404.html")


@main.route("/germplasm/<germplasm_id>/progeny")
def germplasm_progeny(germplasm_id):
    logging.info(f"Germplasm Progeny ID: {germplasm_id}")
    base_url = request.args.get("base_url")
    server_name = request.args.get("server_name")
    germplasm_name = request.args.get("germplasm_name")

    if germplasm_id and base_url:
        progeny_info = getGermplasmProgeny(germplasm_id, base_url)
        if progeny_info:
            logging.info(f"Progeny Information found for : {germplasm_id}")
            logging.info(progeny_info)
            logging.info(f"Going on progeny page")
            return render_template("progeny.html", progeny=progeny_info, detail_type='germplasm', detail_id=germplasm_id, germplasm_name=germplasm_name, base_url=base_url, server_name=server_name)
    
    logging.warning("Progeny information not found")
    return render_template("404.html")

import requests
import logging

def check_endpoint_exists(base_url, endpoint):
    full_url = f"{base_url}{endpoint}"
    print(f'full_url: {full_url}')
    try:
        response = requests.get(full_url)  # Use GET request to fetch the response body
        if response.status_code == 200:
            try:
                # Attempt to parse the response as JSON
                response_json = response.json()
                return True
            except ValueError as e:
                logging.error(f"Error decoding JSON from {full_url}: {e}")
                return False
        else:
            logging.warning(f"Non-200 status code {response.status_code} from {full_url}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error checking endpoint {full_url}: {e}")
        return False

