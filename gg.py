import json
import requests
import logging

url = "https://urgi.versailles.inra.fr/faidare/brapi/v1/germplasm?page=0&pageSize=1000"
response = requests.get(url, verify=False)

if response.status_code == 200:
    try:
        data = response.json()
        print(len(data))
        page_data = data.get('result', {}).get('data', [])
        print(len(page_data))
        # Process your data here
    except json.JSONDecodeError as e:
        logging.error(f"Error during upsertion: {e}")
        logging.error(f"Response content: {response.text[:1000]}")
else:
    logging.error(f"Error: Received status code {response.status_code}")
