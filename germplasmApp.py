import requests

#BASE_URL = 'https://test-server.brapi.org/brapi/v1'
#BASE_URL = ''

def getGermplasmSearch(search_term):
    url = BASE_URL + '/germplasm-search'
    
    try:
        res = requests.get(url)
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        status_code = res.status_code
        #print(f"Status Code: {status_code}")
        
        res_json = res.json()
        #print(res_json)
        samples = res_json.get('result', {}).get('data', [])
        
        if samples:
            #print(f"Number of samples found: {len(samples)}")
            # Filter samples based on search term dynamically
            filtered_samples = [
                sample for sample in samples
                if any(search_term.lower() in str(value).lower() for value in sample.values())
            ]
            return filtered_samples

    except Exception as e:
        print(f"Error in getGermplasmSearch: {e}")
        return None

# Example usage
search_term = 'G000002'   
filtered_samples = getGermplasmSearch(search_term)
print(filtered_samples)
