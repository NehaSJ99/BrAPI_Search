import requests

def getGermplasmSearch(search_param, base_url):
    url = f"{base_url}/germplasm-search"
    searched_results = []

    try:
        res = requests.get(url, params={'query': search_param})
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        res_json = res.json()
        samples = res_json.get('result', {}).get('data', [])

        if samples:
            searched_results.extend(samples)

    except requests.exceptions.RequestException as e:
        print(f"Error in getGermplasmSearch: {e}")

    return searched_results
