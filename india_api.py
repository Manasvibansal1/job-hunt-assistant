import requests
import os

def fetch_india_jobs(keyword, location="New Delhi", results_per_page=5):
    """Fetches job listings from Adzuna's India marketplace and standardizes them."""
    app_id = os.getenv("ADZUNA_APP_ID", "")
    app_key = os.getenv("ADZUNA_APP_KEY", "")
    
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results_per_page,
        "what": keyword,
        "where": location,
        "content-type": "application/json"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            raw_jobs = data.get('results', [])
            
            # Map fields to match the exact schema expected by your orchestrator
            standardized_jobs = []
            for job in raw_jobs:
                company_info = job.get('company', {})
                company_name = company_info.get('display_name', 'Unknown Organization') if isinstance(company_info, dict) else 'Unknown Organization'
                
                standardized_jobs.append({
                    "PositionTitle": job.get('title', 'Unknown Position'),
                    "OrganizationName": company_name,
                    "UserArea": {
                        "Details": {
                            "JobSummary": job.get('description', 'No description available.')
                        }
                    }
                })
            return standardized_jobs
        else:
            print(f"Error fetching India jobs: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Exception during India job fetch: {e}")
        return []