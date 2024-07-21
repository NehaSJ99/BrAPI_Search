from flask import request, render_template, Blueprint, jsonify
import logging
from .BrAPIClientService import getGermplasmSearch, search_trait, search_trial, getGermplasmPedigree, getGermplasmProgeny
from .BrAPIs import fetch_server_apis
from pymongo import MongoClient
from bson.objectid import ObjectId


main = Blueprint("main", __name__)

server_info = {
    'T3/Wheat': {'server-title': 'T3/Wheat', 'api-urls': ['https://wheat.triticeaetoolbox.org/brapi/v2/'], 'auth-required': False, 'server_status': True},
    'T3/Oat': {'server-title': 'T3/Oat', 'api-urls': ['https://oat.triticeaetoolbox.org/brapi/v2/'], 'auth-required': False, 'server_status': True},
    'T3/Barley': {'server-title': 'T3/Barley', 'api-urls': ['https://barley.triticeaetoolbox.org/brapi/v2/'], 'auth-required': False, 'server_status': True}
}

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set log level as needed

# Initialize MongoDB client
myclient = MongoClient('mongodb://127.0.0.1:27017')
if myclient:
    print(f"Connection established with string : {myclient}")
else:
    print("Not abble to established a connection with mongo server")
db = myclient["brapidata"]
print(db)

@main.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html", server_info=server_info)

@main.route('/about') 
def aboutPage(): 
    return render_template('about.html') 

@main.route('/contact') 
def contactPage(): 
    return render_template('contact.html')

@main.route("/search", methods=['POST'])
def search():
    search_results = []

    search_param = request.form.get("query")
    selected_servers = request.form.getlist("servers[]")
    search_for = request.form.get("search_for")
    mongo_db = 'brapidata'

    collection_name_list = []
    for server in selected_servers:
        col_name = server.replace("/", "_").lower() + "_" + search_for
        collection_name_list.append((col_name, server))  # Store collection name and server as tuple

    logging.info("On the Search Page")
    logging.info(f"Search Query: {search_param}")
    logging.info(f"Selected Servers: {selected_servers}")
    logging.info(f"Search For: {search_for}")
    logging.info(f"Mongo database: {mongo_db}")
    logging.info(f"Collections: {collection_name_list}")

    # Define the search fields for different search types
    search_fields = {
        "traits": ["traitName", "traitDbId"],
        "germplasm": ["genus", "germplasmDbId", "germplasmName", "species", "defaultDisplayName", "accessionNumber"],
        "trials" : ["trialName","trialDbId", "programName", "programDbId", "commonCropName"]
    }

    # Fetch data from MongoDB based on the input
    if collection_name_list:
        for collection_name, server in collection_name_list:
            collection = db[collection_name]

            # Determine which fields to search based on the search_for parameter
            if search_for in search_fields:
                query_conditions = [{field: {"$regex": search_param, "$options": "i"}} for field in search_fields[search_for]]
                results = collection.find({
                    "$or": query_conditions
                })

                for result in results:
                    # Add server name and base URL to each result if collection name matches
                    if 't3_barley' in collection_name:
                        server_title = server_info['T3/Barley']['server-title']
                        base_url = server_info['T3/Barley']['api-urls'][0]
                    elif 't3_oat' in collection_name:
                        server_title = server_info['T3/Oat']['server-title']
                        base_url = server_info['T3/Oat']['api-urls'][0]
                    elif 't3_wheat' in collection_name:
                        server_title = server_info['T3/Wheat']['server-title']
                        base_url = server_info['T3/Wheat']['api-urls'][0]
                    else:
                        server_title = server
                        base_url = ''  # Default base URL if not found in the dictionary

                    result['server_name'] = server_title
                    result['base_url'] = base_url
                    result['_id'] = str(result['_id'])  # Convert ObjectId to string for JSON serialization
                    search_results.append(result)
                    #print(search_results)
    return jsonify(search_results)

@main.route("/details/<string:detail_type>/<string:detail_id>")
def details(detail_type, detail_id):
    logging.info(f"Detail Type: {detail_type}, Detail ID: {detail_id}")
    base_url = request.args.get("base_url")
    server_name = request.args.get("server_name")
    print(f'base url : {base_url}')
    print(f'server_name : {server_name}')
    if detail_type and detail_id and base_url:
        if detail_type == "germplasm":
            searched_results_germplasm = getGermplasmSearch(detail_id, base_url)
            if searched_results_germplasm:
                for result in searched_results_germplasm:
                    result['base_url'] = base_url  # Ensure base_url is set for each result
                    pedigree_info = getGermplasmPedigree(detail_id, base_url)
                    if pedigree_info.get('siblings'):
                        result['pedigree'] = 'Yes'
                    else:
                        result['pedigree'] = 'No'

                    progeny_info = getGermplasmProgeny(detail_id, base_url)
                    if progeny_info.get('progeny'):
                        result['progeny'] = 'Yes'
                    else:
                        result['progeny'] = 'No'

                logging.info(f"Germplasm Details found for : {detail_id}")
                logging.info("3. Displaying details on Details page")
                return render_template("details.html", sample=searched_results_germplasm[0], detail_type=detail_type, server_name=server_name)
            
        elif detail_type == "trait":
            print(f' Start Searching for : {detail_type} : {detail_id} in url : {base_url}')
            searched_results = search_trait(detail_id, base_url)
        elif detail_type == "trial":
            searched_results = search_trial(detail_id, base_url)
        else:
            logging.warning("Invalid detail type")
            return "Invalid detail type", 404

        if searched_results:
            logging.info(f"Germplasm Details found for : {detail_id}")
            logging.info("3. Displaying results on Details page")
            print(searched_results)
            return render_template("details.html", sample=searched_results, detail_type=detail_type, server_name=server_name)
    
    logging.warning("Sample not found")
    return "Sample not found", 404

@main.route("/germplasm/<germplasm_id>/pedigree")
def germplasm_pedigree(germplasm_id):
    logging.info(f"Germplasm Pedigree ID: {germplasm_id}")
    base_url = request.args.get("base_url")
    server_name = request.args.get("server_name")
    if germplasm_id and base_url:
        pedigree_info = getGermplasmPedigree(germplasm_id, base_url)
        if pedigree_info:
            logging.info(f"Pedigree Information found for : {germplasm_id}")
            logging.info(f"Going on pedigree page")
            return render_template("pedigree.html", pedigree=pedigree_info, detail_type='germplasm', detail_id=germplasm_id, base_url=base_url, server_name=server_name)
    
    logging.warning("Pedigree information not found")
    return render_template("404.html")

@main.route("/germplasm/<germplasm_id>/progeny")
def germplasm_progeny(germplasm_id):
    logging.info(f"Germplasm Progeny ID: {germplasm_id}")
    base_url = request.args.get("base_url")
    server_name = request.args.get("server_name")
    germplasm_name = request.args.get("germplasm_name")

    print(germplasm_name)
    if germplasm_id and base_url:
        progeny_info = getGermplasmProgeny(germplasm_id, base_url)
        if progeny_info:
            logging.info(f"Progeny Information found for : {germplasm_id}")
            logging.info(f"Going on progeny page")
            return render_template("progeny.html", progeny=progeny_info, detail_type='germplasm', detail_id=germplasm_id, germplasm_name=germplasm_name, base_url=base_url, server_name=server_name)
    
    logging.warning("Progeny information not found")
    return render_template("404.html")
