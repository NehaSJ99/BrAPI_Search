from flask import request, render_template, Blueprint
import logging
from .BrAPIClientService import getGermplasmSearch, search_trait, search_trial, getGermplasmPedigree, getGermplasmProgeny
from .BrAPIs import fetch_server_apis

main = Blueprint("main", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set log level as needed

@main.route("/")
def index():
    server_info = fetch_server_apis()  # Fetch server information
    return render_template("index.html", server_info=server_info)

@main.route("/search", methods=["POST"])
def search():
    search_param = request.form.get("query")
    selected_servers = request.form.getlist("servers[]")  # Get list of selected servers
    search_for = request.form.get("search_for")  # Get the selected search category

    logging.info("1. On the Search Page")
    logging.info(f"Search Query: {search_param}")
    logging.info(f"Selected Servers: {selected_servers}")
    logging.info(f"Search For: {search_for}")

    searched_results = []
    for server in selected_servers:
        server_info = fetch_server_apis()
        base_url = server_info.get(server, {}).get('api-urls', [])[0] if server in server_info else ''
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
                    if result:  # Check if result is not None
                        result['server_name'] = server  # Add server name to each result
                        result['base_url'] = base_url  # Ensure base_url is set for each result
                searched_results.extend(results)

    if searched_results:
        logging.info(f"Search Results found for : {search_param}")
        logging.info("2. Displaying results on Results page")
        return render_template("results.html", query=search_param, results=searched_results)
    else:
        logging.warning("No results found")
        return "No results found", 404

@main.route("/details/<string:detail_type>/<string:detail_id>")
def details(detail_type, detail_id):
    logging.info(f"Detail Type: {detail_type}, Detail ID: {detail_id}")
    base_url = request.args.get("base_url")
    
    if detail_type and detail_id and base_url:
        if detail_type == "germplasm":
            searched_results_germplasm = getGermplasmSearch(detail_id, base_url)
            if searched_results_germplasm:
                for result in searched_results_germplasm:
                    if result:  # Check if result is not None
                        result['base_url'] = base_url  # Ensure base_url is set for each result
                logging.info(f"Germplasm Details found for : {detail_id}")
                logging.info("3. Displaying details on Details page")
                return render_template("details.html", sample=searched_results_germplasm[0], detail_type=detail_type)
            
        elif detail_type == "trait":
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
