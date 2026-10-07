import requests
from utils.config import USAJOBS_API_KEY, USAJOBS_USER_AGENT

def fetch_usajobs(keyword, location, results_per_page=5):
    url = "https://data.usajobs.gov/api/search"
    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": USAJOBS_USER_AGENT,
        "Authorization-Key": USAJOBS_API_KEY
    }
    params = {
        "Keyword": keyword,
        "LocationName": location,
        "ResultsPerPage": results_per_page
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        # Extract search result items safely
        items = data.get('SearchResult', {}).get('SearchResultItems', [])
        return items
    else:
        print(f"Error fetching jobs: {response.status_code} - {response.text}")
        return []