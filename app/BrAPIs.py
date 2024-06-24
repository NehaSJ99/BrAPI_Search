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
                'auth-required': auth_required
            }
    
    return server_info

def fetch_server_apis(url='https://brapi.org/servers'):
    soup = fetch_and_parse_html(url)
    if soup:
        return get_server_info(soup)
    return {}

if __name__ == '__main__':
    server_info = fetch_server_apis()
    print(server_info)
