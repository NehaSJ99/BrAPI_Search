from flask import request, render_template, Blueprint
from .BrAPIClientService import getGermplasmSearch, search_trait, search_trial, getGermplasmPedigree, getGermplasmProgeny
from .BrAPIs import fetch_server_apis

main = Blueprint("main", __name__)

@main.route("/")
def index():
    server_info = fetch_server_apis()  # Fetch server information
    return render_template("index.html", server_info=server_info)

@main.route("/search", methods=["POST"])
def search():
    search_param = request.form.get("query")
    selected_servers = request.form.getlist("servers[]")  # Get list of selected servers
    search_for = request.form.get("search_for")  # Get the selected search category

    print(f"Search Query: {search_param}")
    print(f"Selected Servers: {selected_servers}")
    print(f"Search For: {search_for}")

    searched_results = []
    for server in selected_servers:
        server_info = fetch_server_apis()
        base_url = server_info[server]['api-urls'][0] if server in server_info else ''
        if base_url:
            if search_for == "germplasm":
                results = getGermplasmSearch(search_param, base_url)
            elif search_for == "traits":
                results = [search_trait(search_param, base_url)]
                #print(f'results : {results}')
            elif search_for == "trials":
                results = [search_trial(search_param, base_url)]
            else:
                results = []

            if len(results) > 0:
                for result in results:
                    if result:  # Check if result is not None
                        result['server_name'] = server  # Add server name to each result
                        result['base_url'] = base_url  # Ensure base_url is set for each result
                searched_results.extend(results)
                #print(f'searched_results : {searched_results}')

    if searched_results and searched_results[0] is not None:
        return render_template("results.html", query=search_param, results=searched_results)
    else:
        return "No results found", 404

@main.route("/details/<string:detail_type>/<string:detail_id>")
def details(detail_type, detail_id):
    #print(f'In details....')
    print(detail_type, detail_id)
    base_url = request.args.get("base_url")
    #print(f'Printitng base_url : {base_url}')
    if detail_type and detail_id and base_url:
        if detail_type == "germplasm":
            searched_results_germplasm = getGermplasmSearch(detail_id, base_url)
            if searched_results_germplasm:
                for result in searched_results_germplasm:
                    if result:  # Check if result is not None
                        result['base_url'] = base_url  # Ensure base_url is set for each result
                searched_results_germplasm.extend(result)
                return render_template("details.html", sample=searched_results_germplasm[0], detail_type=detail_type)
            
        elif detail_type == "trait":
            searched_results = search_trait(detail_id, base_url)
        elif detail_type == "trial":
            searched_results = search_trial(detail_id, base_url)
        else:
            return "Invalid detail type", 404

        if searched_results:
            return render_template("details.html", sample=searched_results, detail_type=detail_type)
    return "Sample not found", 404 

@main.route("/germplasm/<germplasm_id>/pedigree")
def germplasm_pedigree(germplasm_id):
    #print("In the germplasm_pedigree route...")
    base_url = request.args.get("base_url")
    #print(f'bas url for pefigree : {base_url}')
    if germplasm_id and base_url:
        pedigree_info = getGermplasmPedigree(germplasm_id, base_url)
        #print(f'pedigree_info : {pedigree_info}')
        if pedigree_info:
            return render_template("pedigree.html", pedigree=pedigree_info)
    return "Pedigree information not found", 404

@main.route("/germplasm/<germplasm_id>/progeny")
def germplasm_progeny(germplasm_id):
    #print("In the germplasm_progeny route...")
    base_url = request.args.get("base_url")
    #print(f'bas url for progeny : {base_url}')
    if germplasm_id and base_url:
        progeny_info = getGermplasmProgeny(germplasm_id, base_url)
        if progeny_info:
            print(f'Progeny info : {progeny_info}')
            return render_template("progeny.html", progeny=progeny_info)
    return "Pedigree information not found", 404