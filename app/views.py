from flask import request, render_template, Blueprint
from .BrAPIClientService import getGermplasmSearch
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

    print(f"Search Query: {search_param}")
    print(f"Selected Servers: {selected_servers}")

    searched_results = []
    for server in selected_servers:
        server_info = fetch_server_apis()
        base_url = server_info[server]['api-urls'][0] if server in server_info else ''
        if base_url:
            results = getGermplasmSearch(search_param, base_url)
            if results:
                for result in results:
                    result['server_name'] = server  # Add server name to each result
                    result['base_url'] = base_url  # Ensure base_url is set for each result
                searched_results.extend(results)

    return render_template("results.html", query=search_param, results=searched_results)

@main.route("/details/<germplasm_id>")
def details(germplasm_id):
    #print("Into Details....\n")
    base_url = request.args.get("base_url")
    #print("base url\n", base_url)
    if germplasm_id and base_url:
        searched_results = getGermplasmSearch(germplasm_id, base_url)
        if searched_results:
            return render_template("details.html", sample=searched_results[0])
    return "Sample not found", 404
