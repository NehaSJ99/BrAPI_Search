from flask import request, render_template, Blueprint, jsonify
import logging
from .BrAPIClientService import getGermplasmSearch, search_trait, search_trial, getGermplasmPedigree, getGermplasmProgeny
from .BrAPIs import fetch_server_apis
import json

main = Blueprint("main", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set log level as needed

server_info = {
    'T3/Wheat': {'server-title': 'T3/Wheat', 'api-urls': ['https://wheat.triticeaetoolbox.org/brapi/v2/'], 'auth-required': False, 'server_status': True},
    'T3/Oat': {'server-title': 'T3/Oat', 'api-urls': ['https://oat.triticeaetoolbox.org/brapi/v2/'], 'auth-required': False, 'server_status': True},
    'T3/Barley': {'server-title': 'T3/Barley', 'api-urls': ['https://barley.triticeaetoolbox.org/brapi/v2/'], 'auth-required': False, 'server_status': True}
}

@main.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html", server_info=server_info)

@main.route("/search", methods=['POST'])
def search():
    search_results = []

    search_param = request.form.get("query")
    selected_servers = request.form.getlist("servers[]")
    search_for = request.form.get("search_for")

    logging.info("On the Search Page")
    logging.info(f"Search Query: {search_param}")
    logging.info(f"Selected Servers: {selected_servers}")
    logging.info(f"Search For: {search_for}")

    if server_info:
        for server in selected_servers:
            base_url = server_info.get(server, {}).get('api-urls', [])[0]
            if base_url:
                if search_for == "germplasm":
                    results = getGermplasmSearch(search_param, base_url)
                elif search_for == "traits":
                    results = [search_trait(search_param, base_url)]
                elif search_for == "trials":
                    results = [search_trial(search_param, base_url)]
                else:
                    results = []

                if results:
                    for result in results:
                        result['server_name'] = server
                        result['base_url'] = base_url
                    search_results.extend(results)
                else:
                    logging.warning(f"No results found for search on server: {server}")
            else:
                logging.warning(f"No base URL found for server: {server}")
    else:
        logging.warning("Server Info not found")
    print(f'Search Results : {search_results}')
    print('********************************************')
    print(jsonify(search_results))
    #return jsonify(search_results)
    return search_results


@main.route("/details/<string:detail_type>/<string:detail_id>")
def details(detail_type, detail_id):
    logging.info(f"Detail Type: {detail_type}, Detail ID: {detail_id}")
    base_url = request.args.get("base_url")
    print(f'base url : {base_url}')
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
                return render_template("details.html", sample=searched_results_germplasm[0], detail_type=detail_type)
            
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
            return render_template("details.html", sample=searched_results, detail_type=detail_type)
    
    logging.warning("Sample not found")
    return "Sample not found", 404

@main.route("/germplasm/<germplasm_id>/pedigree")
def germplasm_pedigree(germplasm_id):
    logging.info(f"Germplasm Pedigree ID: {germplasm_id}")
    base_url = request.args.get("base_url")
    
    if germplasm_id and base_url:
        pedigree_info = getGermplasmPedigree(germplasm_id, base_url)
        if pedigree_info:
            logging.info(f"Pedigree Information found for : {germplasm_id}")
            logging.info(f"Going on pedigree page")
            return render_template("pedigree.html", pedigree=pedigree_info)
    
    logging.warning("Pedigree information not found")
    return "Pedigree information not found", 404

@main.route("/germplasm/<germplasm_id>/progeny")
def germplasm_progeny(germplasm_id):
    logging.info(f"Germplasm Progeny ID: {germplasm_id}")
    base_url = request.args.get("base_url")
    
    if germplasm_id and base_url:
        progeny_info = getGermplasmProgeny(germplasm_id, base_url)
        if progeny_info:
            logging.info(f"Progeny Information found for : {germplasm_id}")
            logging.info(f"Going on progeny page")
            return render_template("progeny.html", progeny=progeny_info)
    
    logging.warning("Progeny information not found")
    return "Progeny information not found", 404
