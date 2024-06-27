import requests

#BASE_URL = 'https://wheat.triticeaetoolbox.org/brapi/v2'
BASE_URL = 'https://barley.triticeaetoolbox.org/brapi/v2'


def searchGermplasm(data):
    url = f"{BASE_URL}/search/germplasm"
    print(f'URL : {url}')
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        res_json = res.json()
        searchResultsDbId = res_json.get('result', {}).get('searchResultsDbId')
        
        if searchResultsDbId:
            print(searchResultsDbId)
            return searchResultsDbId
        else:
            print("searchResultsDbId not found in response")
            return None

    except Exception as e:
        print(f"Error in searchGermplasm: {e}")
        return None

def getGermplasmDetails(searchResultsDbId):
    url = f"{BASE_URL}/search/germplasm/{searchResultsDbId}"
    print(f'URL : {url}')
    headers = {
        "Accept": "application/json"
    }
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        res_json = res.json()
        return res_json.get('result', {})
        
    except Exception as e:
        print(f"Error in getGermplasmDetails: {e}")
        return None

# Example usage
data = {
    "germplasmDbId": "",  # Example germplasmDbId
    "germplasmName": "003Q",   # Example germplasmName
}
#{'germplasmName': 'LNR14-0563', 'germplasmDbId': '1459456'}
#{'germplasmName': 'BW308', 'germplasmDbId': '1458950'}
searchResultsDbId = searchGermplasm(data)
if searchResultsDbId:
    germplasmDetails = getGermplasmDetails(searchResultsDbId)
    print(f"Germplasm Details: {germplasmDetails}")
else:
    print("Failed to retrieve searchResultsDbId")
