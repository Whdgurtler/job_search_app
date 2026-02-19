"""Test scraping workflow end-to-end"""
import requests
import time

API_URL = "http://localhost:8000/api/v1"

# Test user from dev mode
headers = {}  # Dev mode doesn't need auth headers

print("=== Testing Job Scraper Backend ===\n")

# 1. Create a scrape config
print("1. Creating scrape config...")
config_payload = {
    "name": "Test Scrape - Airbnb",
    "keywords": "software engineer python",
    "companies": ["Airbnb"],
    "employment_areas": [],
    "location": "Remote",
    "is_default": True
}

response = requests.post(f"{API_URL}/scrape-configs", json=config_payload, headers=headers)
print(f"   Status: {response.status_code}")
if response.ok:
    config = response.json()
    config_id = config["id"]
    print(f"   Config created: {config_id}")
    print(f"   Name: {config['name']}")
else:
    print(f"   Error: {response.text}")
    exit(1)

# 2. List configs
print("\n2. Listing scrape configs...")
response = requests.get(f"{API_URL}/scrape-configs", headers=headers)
print(f"   Status: {response.status_code}")
if response.ok:
    configs = response.json()
    print(f"   Found {len(configs)} config(s)")
    for cfg in configs:
        print(f"     - {cfg['name']} (ID: {cfg['id'][:8]}...)")

# 3. Trigger scrape
print("\n3. Triggering scrape...")
trigger_payload = {
    "config_id": config_id,
}

response = requests.post(f"{API_URL}/scrapes/trigger", json=trigger_payload, headers=headers)
print(f"   Status: {response.status_code}")
if response.ok:
    run = response.json()
    run_id = run["id"]
    print(f"   Scrape run created: {run_id}")
    print(f"   Status: {run['status']}")
    print(f"   Companies: {run['companies']}")
else:
    print(f"   Error: {response.text}")
    exit(1)

# 4. Poll status
print("\n4. Polling scrape status...")
for i in range(30):  # Poll for up to 5 minutes
    time.sleep(10)
    response = requests.get(f"{API_URL}/scrapes/{run_id}/status", headers=headers)
    if response.ok:
        status = response.json()
        print(f"   [{i*10}s] Status: {status['status']}, Jobs: {status.get('jobs_found', 0)} found, {status.get('jobs_new', 0)} new")
        
        if status["status"] in ["completed", "failed"]:
            if status["status"] == "failed":
                print(f"   Error: {status.get('error_message')}")
            break
    else:
        print(f"   Error checking status: {response.text}")
        break

# 5. Get final scrape run details
print("\n5. Getting scrape run details...")
response = requests.get(f"{API_URL}/scrapes/{run_id}", headers=headers)
if response.ok:
    run = response.json()
    print(f"   Final status: {run['status']}")
    print(f"   Jobs found: {run.get('jobs_found', 0)}")
    print(f"   Jobs new: {run.get('jobs_new', 0)}")
    print(f"   Duration: {run.get('duration_seconds', 0):.1f}s")
    if run.get('error_message'):
        print(f"   Error: {run['error_message']}")

# 6. List jobs
print("\n6. Listing scraped jobs...")
response = requests.get(f"{API_URL}/jobs", headers=headers)
if response.ok:
    jobs = response.json()
    print(f"   Found {len(jobs)} job(s)")
    for job in jobs[:5]:  # Show first 5
        print(f"     - {job['title']} at {job['company_name']}")
        print(f"       Location: {job.get('location', 'N/A')}")
        print(f"       Posted: {job.get('posted_date', 'N/A')}")
        if job.get('match_score'):
            print(f"       Match: {job['match_score']}%")

print("\n=== Test Complete ===")
