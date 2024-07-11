import requests
from bs4 import BeautifulSoup

def fetch_and_parse_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch or parse {url}: {str(e)}")
        return None

def get_server_info(soup):
    server_info = {}
    
    # Find all server containers
    servers = soup.find_all('div', class_='row brapp-box justify-content-center')
    
    for server in servers:
        # Extract the server title
        title_tag = server.find('h2', class_='server-title')
        if title_tag:
            server_title = title_tag.text.strip()
            if '.' in server_title:
                server_title = server_title.split('.')[0]
            if '(' in server_title:
                server_title = server_title.split('(')[0]
            
            # Extract the API URLs
            api_urls = []
            code_tags = server.find_all('code', class_='server-v2-url')
            for tag in code_tags:
                api_urls.append(tag.text.strip())
            
            # Check for authentication requirement
            auth_required = False
            badge_text = server.find(class_='badge-text')
            if badge_text and 'Auth Required' in badge_text.text:
                auth_required = True
            
            # Create a nested dictionary with 'server-title', 'api-urls', and 'auth-required' keys
            server_info[server_title] = {
                'server-title': server_title,
                'api-urls': api_urls,
                'auth-required': auth_required,
            }
    #print(server_info)
    #print(len(server_info))
    available_servers = check_server_status(server_info)
    #print(available_servers)
    filtered_server_info = filter_server_info(available_servers)
    #print(filtered_server_info)
    #print(len(filtered_server_info))
    return filtered_server_info

def fetch_server_apis(url='https://brapi.org/servers'):
    soup = fetch_and_parse_html(url)
    if soup:
        return get_server_info(soup)
    return {}

def filter_server_info(server_info):
    filtered_server_info = {key: value for key, value in server_info.items() if value['api-urls'] and value['server_status'] == True}
    return filtered_server_info

def check_server_status(server_info):
    for server in server_info:
        if len(server_info.get(server, {}).get('api-urls', [])) > 0:
            server_url = server_info.get(server, {}).get('api-urls', [])[0] if server in server_info else ''
            #print(server_url)
            url = f"{server_url}germplasm"
            try:
                res = requests.get(url)
                #print(res.status_code)
                if res.status_code == 200:
                    server_info[server]['server_status'] = True
                else:
                    server_info[server]['server_status'] = False
            except requests.RequestException as e:
                print(f"Error in getGermplasmSearch: {e}")
                server_info[server]['server_status'] = False
        else:
            server_info[server]['server_status'] = False
    return server_info

if __name__ == '__main__':
    servers = fetch_server_apis()
    #print(servers)
    #print(servers)
