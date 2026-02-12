"""Company discovery module - find companies by sector and characteristics."""
from typing import List, Dict, Optional
from llm_analyzer import LLMAnalyzer
import json
import re


class CompanyDiscovery:
    """Discover and filter companies by sector and characteristics."""

    # Known companies by sector (curated list)
    SECTOR_COMPANIES = {
        "banking": [
            # Big 4
            "JPMorgan Chase", "Bank of America", "Wells Fargo", "Citigroup",
            # Major investment banks
            "Goldman Sachs", "Morgan Stanley",
            # Large national banks
            "Capital One", "US Bank", "PNC", "TD Bank", "Truist",
            "American Express", "Discover", "Charles Schwab", "BNY Mellon",
            "State Street", "Citizens Financial", "HSBC", "BMO Harris",
            "Fifth Third Bank", "KeyBank", "Ally Financial",
            # Super regional banks
            "Huntington", "Regions", "M&T Bank", "Northern Trust",
            "Synchrony", "First Citizens", "Comerica",
            "Zions Bancorporation", "Western Alliance", "East West Bank",
            "Webster Bank", "Frost Bank", "Flagstar Bank", "Synovus",
            "BOK Financial", "First Horizon", "Associated Bank",
        ],
        "fintech": [
            "Stripe", "Block (Square)", "Coinbase", "Robinhood", "Plaid", "Chime",
            "Affirm", "SoFi", "PayPal", "Venmo", "Cash App", "Brex", "Ramp",
            "Marqeta", "Checkout.com", "Adyen", "Revolut", "Klarna"
        ],
        "technology": [
            "Google", "Meta", "Amazon", "Microsoft", "Apple", "Netflix", "Uber",
            "Airbnb", "Spotify", "Reddit", "Discord", "Snap", "Twitter", "LinkedIn",
            "Salesforce", "Oracle", "Adobe", "Intuit", "Atlassian", "Zoom"
        ],
        "data": [
            "Databricks", "Snowflake", "Palantir", "Confluent", "MongoDB", "Elastic",
            "Datadog", "Splunk", "dbt Labs", "Fivetran", "Airbyte", "Census"
        ],
        "ai": [
            "OpenAI", "Anthropic", "Cohere", "Hugging Face", "Scale AI", "Weights & Biases",
            "Replicate", "Midjourney", "Runway", "Character.AI", "Jasper"
        ],
        "crypto": [
            "Coinbase", "Kraken", "Gemini", "Circle", "Chainalysis", "Alchemy",
            "OpenSea", "Uniswap", "Polygon", "Consensys"
        ],
        "cloud": [
            "Amazon Web Services", "Google Cloud", "Microsoft Azure", "Cloudflare",
            "DigitalOcean", "Linode", "Vercel", "Netlify", "Heroku", "Fly.io"
        ],
        "cybersecurity": [
            "CrowdStrike", "Palo Alto Networks", "Okta", "Zscaler", "SentinelOne",
            "Snyk", "Wiz", "Lacework", "1Password", "Duo Security"
        ],
        "ecommerce": [
            "Shopify", "Amazon", "eBay", "Etsy", "Wayfair", "Instacart", "DoorDash",
            "Uber Eats", "Postmates", "Grubhub", "Toast"
        ],
        "healthcare": [
            "Epic Systems", "Cerner", "Optum", "Change Healthcare", "Oscar Health",
            "Ro", "Hims & Hers", "23andMe", "Color", "Tempus"
        ],
        "insurance": [
            "Lemonade", "Root Insurance", "Hippo", "Next Insurance", "Pie Insurance",
            "Corvus Insurance", "Coalition", "At-Bay"
        ],
        "real_estate": [
            "Zillow", "Redfin", "Opendoor", "Compass", "CoStar", "Realtor.com",
            "Reonomy", "VTS", "Cadre"
        ],
        "gaming": [
            "Roblox", "Epic Games", "Unity", "Riot Games", "Activision Blizzard",
            "Electronic Arts", "Take-Two Interactive", "Zynga", "Discord"
        ],
        "media": [
            "Netflix", "Disney", "Spotify", "Paramount", "Warner Bros Discovery",
            "NBCUniversal", "Vox Media", "BuzzFeed", "Vice Media"
        ],
        "travel": [
            "Airbnb", "Booking.com", "Expedia", "Tripadvisor", "Hopper", "Kayak",
            "Priceline", "Hotels.com", "GetYourGuide"
        ],
        "education": [
            "Coursera", "Udemy", "Duolingo", "Khan Academy", "Chegg", "2U",
            "Guild Education", "Outlier", "Masterclass"
        ],
        "enterprise_software": [
            "Salesforce", "ServiceNow", "Workday", "SAP", "Oracle", "Adobe",
            "Atlassian", "Monday.com", "Asana", "Notion", "Airtable", "Zapier"
        ],
        "infrastructure": [
            "HashiCorp", "Terraform", "Docker", "Kubernetes", "Jenkins", "GitLab",
            "GitHub", "CircleCI", "Datadog", "New Relic", "PagerDuty"
        ],
        "consumer": [
            "Nike", "Adidas", "Warby Parker", "Allbirds", "Casper", "Away",
            "Glossier", "Peloton", "Mirror", "Tonal"
        ]
    }

    def __init__(self, llm: Optional[LLMAnalyzer] = None):
        """Initialize company discovery."""
        self.llm = llm or LLMAnalyzer()

    def get_companies_by_sector(
        self,
        sector: str,
        max_companies: int = 50,
        use_llm: bool = True
    ) -> List[str]:
        """
        Get list of companies in a specific sector.

        Args:
            sector: Industry sector (e.g., 'banking', 'fintech', 'technology')
            max_companies: Maximum number of companies to return
            use_llm: If True, use LLM to expand the list beyond curated companies

        Returns:
            List of company names
        """
        sector_lower = sector.lower().replace(" ", "_")

        # Start with curated list
        companies = []

        # Check if we have a curated list for this sector
        if sector_lower in self.SECTOR_COMPANIES:
            companies = self.SECTOR_COMPANIES[sector_lower].copy()
            print(f"Found {len(companies)} curated companies in {sector}")

        # If we want more companies or don't have a curated list, use LLM
        if use_llm and (not companies or len(companies) < max_companies):
            print(f"Using LLM to find additional {sector} companies...")
            llm_companies = self._llm_find_companies(sector, max_companies)

            # Merge with curated list
            for company in llm_companies:
                if company not in companies:
                    companies.append(company)

        return companies[:max_companies]

    def _llm_find_companies(self, sector: str, max_companies: int) -> List[str]:
        """Use LLM to find companies in a sector."""
        prompt = f"""List {max_companies} well-known companies in the {sector} sector.

Focus on:
- Companies actively hiring for technical roles
- Mix of large enterprises and high-growth startups
- Companies with publicly accessible career pages
- US-based or with significant US presence

Return ONLY a JSON array of company names, no explanations:
["Company 1", "Company 2", "Company 3", ...]

Limit: {max_companies} companies maximum."""

        try:
            response = self.llm.analyze(prompt, max_tokens=1000)

            if not response:
                return []

            # Extract JSON array from response
            json_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if json_match:
                companies_json = '[' + json_match.group(1) + ']'
                companies = json.loads(companies_json)
                return [c.strip() for c in companies if isinstance(c, str)]

            return []
        except Exception as e:
            print(f"   LLM company discovery error: {e}")
            return []

    def filter_companies(
        self,
        companies: List[str],
        characteristics: Optional[Dict] = None
    ) -> List[str]:
        """
        Filter companies by characteristics.

        Args:
            companies: List of company names
            characteristics: Optional dict with filtering criteria:
                - size: "startup", "mid", "large", "enterprise"
                - stage: "seed", "series_a", "series_b", "series_c", "public"
                - remote_friendly: True/False
                - locations: List of preferred locations
                - min_employees: Minimum employee count
                - max_employees: Maximum employee count
                - tech_stack: List of required technologies
                - exclude: List of companies to exclude

        Returns:
            Filtered list of companies
        """
        if not characteristics:
            return companies

        filtered = companies.copy()

        # Apply exclusion filter
        if 'exclude' in characteristics:
            exclude_lower = [e.lower() for e in characteristics['exclude']]
            filtered = [c for c in filtered if c.lower() not in exclude_lower]

        # Apply size filter using LLM
        if 'size' in characteristics or 'stage' in characteristics or 'min_employees' in characteristics:
            print(f"Filtering {len(filtered)} companies by characteristics...")
            filtered = self._llm_filter_companies(filtered, characteristics)

        return filtered

    def _llm_filter_companies(
        self,
        companies: List[str],
        characteristics: Dict
    ) -> List[str]:
        """Use LLM to filter companies by characteristics."""
        criteria = []

        if 'size' in characteristics:
            criteria.append(f"Company size: {characteristics['size']}")
        if 'stage' in characteristics:
            criteria.append(f"Funding stage: {characteristics['stage']}")
        if 'min_employees' in characteristics:
            criteria.append(f"At least {characteristics['min_employees']} employees")
        if 'max_employees' in characteristics:
            criteria.append(f"No more than {characteristics['max_employees']} employees")
        if 'remote_friendly' in characteristics and characteristics['remote_friendly']:
            criteria.append("Known for remote-friendly culture")
        if 'locations' in characteristics:
            criteria.append(f"Offices in: {', '.join(characteristics['locations'])}")

        criteria_text = "\n- ".join(criteria)

        prompt = f"""From this list of companies, select those that match ALL these criteria:
- {criteria_text}

Companies to filter:
{json.dumps(companies, indent=2)}

Return ONLY a JSON array of company names that match ALL criteria:
["Company 1", "Company 2", ...]

If unsure, include the company. Be generous in interpretation."""

        try:
            response = self.llm.analyze(prompt, max_tokens=1500)

            if not response:
                return companies  # Return all if LLM fails

            # Extract JSON array
            json_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if json_match:
                filtered_json = '[' + json_match.group(1) + ']'
                filtered = json.loads(filtered_json)
                filtered_companies = [c.strip() for c in filtered if isinstance(c, str)]

                print(f"   Filtered from {len(companies)} to {len(filtered_companies)} companies")
                return filtered_companies

            return companies
        except Exception as e:
            print(f"   LLM filtering error: {e}, returning all companies")
            return companies

    def discover_companies(
        self,
        sector: str,
        characteristics: Optional[Dict] = None,
        max_companies: int = 50,
        use_llm: bool = True
    ) -> List[str]:
        """
        Main method: discover and filter companies in one step.

        Args:
            sector: Industry sector
            characteristics: Filtering criteria (optional)
            max_companies: Maximum companies to return
            use_llm: Whether to expand the list with the LLM

        Returns:
            List of filtered company names
        """
        print(f"\nDiscovering companies in {sector} sector...")

        # Get companies by sector
        companies = self.get_companies_by_sector(
            sector,
            max_companies * 2,
            use_llm=use_llm
        )  # Get more for filtering

        # Apply filters if provided
        if characteristics:
            companies = self.filter_companies(companies, characteristics)

        # Limit to max
        companies = companies[:max_companies]

        print(f"Final company list: {len(companies)} companies")
        return companies


def main():
    """Test company discovery."""
    discovery = CompanyDiscovery()

    # Example 1: Banking sector
    print("=" * 70)
    print("EXAMPLE 1: Banking Sector")
    print("=" * 70)
    banking_companies = discovery.discover_companies(
        sector="banking",
        max_companies=10
    )
    print(f"\nBanking companies: {', '.join(banking_companies)}")

    # Example 2: Fintech with filters
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Fintech - Startups Only")
    print("=" * 70)
    fintech_startups = discovery.discover_companies(
        sector="fintech",
        characteristics={
            "size": "startup",
            "remote_friendly": True
        },
        max_companies=10
    )
    print(f"\nFintech startups: {', '.join(fintech_startups)}")

    # Example 3: Technology sector, excluding FAANG
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Technology - Excluding FAANG")
    print("=" * 70)
    tech_companies = discovery.discover_companies(
        sector="technology",
        characteristics={
            "exclude": ["Google", "Meta", "Amazon", "Apple", "Netflix"]
        },
        max_companies=15
    )
    print(f"\nTech companies (no FAANG): {', '.join(tech_companies)}")


if __name__ == "__main__":
    main()
