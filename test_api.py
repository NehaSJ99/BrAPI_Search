import requests

def getGermplasmData(base_url):
    url = f"{base_url}/germplasm"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        # Get JSON response
        data = response.json()
        
        # Extract the relevant data
        germplasm_data = data.get('result', {}).get('data', [])
        
        return germplasm_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching germplasm data: {e}")
        return None

def extractGermplasmDbIds(germplasm_data):
    germplasm_db_ids = [germplasm.get('germplasmName') for germplasm in germplasm_data if 'germplasmName' in germplasm]
    return germplasm_db_ids


import requests

def search_trait_by_id(trait_id, base_url):
    url = f"{base_url}/traits/{trait_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trait: {e}")
        return None

def search_trial_by_trialDbId(trialDbId, base_url):
    url = f"{base_url}/trials/{trialDbId}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching trial search result: {e}")
        return None
'''
# Example usage
#base_url = "https://cassavabase.org/brapi/v2"
base_url = "https://wheat.triticeaetoolbox.org/brapi/v2"
trait_id = "70403"
trialDbId = "9094"

trait_data = search_trait_by_id(trait_id, base_url)
if trait_data:
    print("Trait Data:", trait_data)

trial_search_result = search_trial_by_trialDbId(trialDbId, base_url)
if trial_search_result:
    print("--------------------------------------------")
    print("Trial Search Result:", trial_search_result)

'''
# Usage
base_url = "https://citrus.sgn.cornell.edu/brapi/v2"
germplasm_data = getGermplasmData(base_url)

if germplasm_data:
    germplasm_db_ids = extractGermplasmDbIds(germplasm_data)
    count_germplasm_db_ids = len(germplasm_db_ids)
    
    print(f"Total number of germplasmDbIds: {count_germplasm_db_ids}")
    print("germplasmDbIds:")
    for db_id in germplasm_db_ids:
        print(db_id)
else:
    print("No germplasm data found or an error occurred.")
