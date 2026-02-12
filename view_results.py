"""Quick script to view job search results from the database."""
import db

jobs = db.get_recent_jobs(limit=500)
print(f"\nTotal jobs in database: {len(jobs)}\n")
print(f"{'Company':<25} {'Title':<45} {'Score':<8} {'Rec':<10} {'Remote':<8} {'Last Seen':<12}")
print("-" * 110)
for j in jobs:
    company = j.get("company", "N/A")[:24]
    title = j.get("title", "N/A")[:44]
    score = j.get("match_score", "N/A")
    rec = j.get("recommendation", "N/A")
    remote = "Yes" if j.get("is_remote") else "No"
    last_seen = j.get("last_seen", "N/A")[:11]
    print(f"{company:<25} {title:<45} {score:<8} {rec:<10} {remote:<8} {last_seen:<12}")

print(f"\nCompanies: {', '.join(db.get_companies())}")
print(f"Scrape dates: {', '.join(db.get_scrape_dates())}")
