import requests
from bs4 import BeautifulSoup

def scrape_content(query):
    search_url = f"https://www.khanacademy.org/search?page_search_query={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    for item in soup.select('.search-result'):
        title = item.select_one('.search-result-title').get_text(strip=True)
        link = item.select_one('.search-result-link')['href']
        description = item.select_one('.search-result-description').get_text(strip=True)
        results.append({
            'title': title,
            'link': f"https://www.khanacademy.org{link}",
            'description': description
        })
    return results
