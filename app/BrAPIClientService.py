import requests

def getGermplasmSearch(search_param, base_url):
    url = f"{base_url}germplasm-search"
    searched_results = []

    try:
        res = requests.get(url, params={'query': search_param})
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        if res.status_code == 200:
            res_json = res.json()
            samples = res_json.get('result', {}).get('data', [])

            if samples:
                # Filter for exact matches in any relevant field
                exact_matches = [
                    sample for sample in samples if search_param in [
                        sample.get('germplasmName', ''),
                        sample.get('defaultDisplayName', ''),
                        sample.get('germplasmDbId', '')
                    ]
                ]
                searched_results.extend(exact_matches)

    except requests.exceptions.RequestException as e:
        print(f"Error in getGermplasmSearch: {e}")
        # Optionally, raise or handle the error as needed

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        # Handle specific HTTP error codes if necessary
    # Clean the searched results before returning
    cleaned_results = clean_data(searched_results)
    #print(f"Searched Results: {cleaned_results}")
    
    return cleaned_results


def getGermplasmPedigree(germplasm_id, base_url):
    #print("In getGermplasmPedigree function...")
    url = f"{base_url}/germplasm/{germplasm_id}/pedigree"
    #print(f'url : {url}')
    try:
        res = requests.get(url)
        res.raise_for_status()
        res_json = res.json()
        samples = res_json.get('result', {})
        if samples:
            #print(f'samples found')
            cleaned_results = clean_data(samples)
            #print(f"Searched Results: {cleaned_results}")
        return cleaned_results

    except requests.RequestException as e:
        print(f"Error fetching pedigree information: {e}")
        return None
    
    
def getGermplasmProgeny(germplasm_id, base_url):
    #print("In getGermplasmProgeny function...")
    url = f"{base_url}/germplasm/{germplasm_id}/progeny"
    #print(f'url : {url}')
    try:
        res = requests.get(url)
        res.raise_for_status()
        res_json = res.json()
        samples = res_json.get('result', {})
        if samples:
            #print(f'samples found')
            cleaned_results = clean_data(samples)
            #print(f"Searched Results: {cleaned_results}")
        return cleaned_results

    except requests.RequestException as e:
        print(f"Error fetching pedigree information: {e}")
        return None

def search_trait(trait_id, base_url):
    #print(f'trait id : {trait_id}, base_url : {base_url}')
    url = f"{base_url}traits/{trait_id}"
    #print(f'url:{url}')
    try:
        res = requests.get(url)
        res.raise_for_status()
        if res.status_code == 200:
            res_json = res.json()
            samples = res_json.get('result', {})
            if samples:
                print(f'samples found')

            return samples
        else:
            print(f"Error fetching trait: {res.status_code} {res.reason}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching trait: {e}")
        return None

def search_trial(trialDbId, base_url):
    url = f"{base_url}trials/{trialDbId}"
    print(f'url:{url}')
    try:
        res = requests.get(url)
        res.raise_for_status()
        if res.status_code == 200:
            res_json = res.json()
            samples = res_json.get('result', {})
            if samples:
                print(f'samples found')

            return samples
        else:
            print(f"Error fetching trait: {res.status_code} {res.reason}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching trait: {e}")
        return None


def clean_data(data):
    """
    Recursively remove attributes with values that are None, Null, NA, 'NA/NA', or empty.
    """
    na_values = [None, 'unknown', 'None', 'null', 'NA', 'NA/NA', '', [], {}, 0]
    
    if isinstance(data, list):
        cleaned_list = [clean_data(item) for item in data if item not in na_values]
        return [item for item in cleaned_list if item]
    elif isinstance(data, dict):
        cleaned_dict = {key: clean_data(value) for key, value in data.items() if value not in na_values}
        return {key: value for key, value in cleaned_dict.items() if value}
    else:
        return data

