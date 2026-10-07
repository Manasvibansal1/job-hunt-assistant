import os
import requests

def fetch_jooble_jobs(keyword, location):
    """
    Fetches job listings from the Jooble REST API.
    Requires a free API key from https://jooble.org/api/about
    """
    api_key = os.environ.get("JOOBLE_API_KEY", "").strip()
    
    if not api_key:
        print("❌ Jooble Error: JOOBLE_API_KEY environment variable is missing or empty.")
        return []

    url = f"https://jooble.org/api/{api_key}"
    payload = {
        "keywords": keyword,
        "location": location,
        "page": 1
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        print(f"Jooble API Response Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            raw_jobs = data.get('jobs', [])
            print(f"Found {len(raw_jobs)} jobs from Jooble.")
            
            normalized_jobs = []
            for job in raw_jobs:
                normalized_jobs.append({
                    "PositionTitle": job.get('title', 'Unknown Position'),
                    "OrganizationName": job.get('company', 'Unknown Company'),
                    "Location": job.get('location', location),
                    "JobSummary": job.get('snippet', 'No summary available.'),
                    "Url": job.get('link', ''),
                    "PublicationStartDate": job.get('updated', 'Unknown'),
                    "Source": "Jooble"
                })
            return normalized_jobs
        else:
            print(f"Jooble API Error Text: {response.text}")
            return []
    except Exception as e:
        print(f"Exception fetching Jooble jobs: {e}")
        return []