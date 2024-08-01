import json
import requests
import logging

total_pages = 10
for page in range(total_pages):
    url = f"https://urgi.versailles.inra.fr/faidare/brapi/v1/germplasm?page={page}&pageSize=1000"
    print(f'url:{url}')
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        # Process your data
        print(f"Successfully fetched page {page}")
    else:
        print(f"Error fetching page {page}: {response.status_code}")
        break  # Stop if an error occurs
