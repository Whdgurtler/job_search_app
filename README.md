# Job Search Agent

AI-powered job search agent that finds and matches jobs from LinkedIn, Indeed, and company career pages to your resume.

## Features

- **Multi-Source Scraping**: LinkedIn, Indeed, and company career pages
- **AI Matching**: Uses embeddings and LLM to match jobs to your resume
- **Stretch Jobs**: Identifies jobs 1-2 levels above your current position
- **Sector Search**: Discover companies by sector (e.g., "fintech", "AI/ML")
- **Smart Scraping**: Handles complex JavaScript-heavy career pages
- **Web Interface**: Easy-to-use Gradio web UI
- **Resume Parsing**: Extracts skills, experience, and job level from your resume

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional)

For best results with LLM features, add an API key to `.env`:

```bash
# Recommended: Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Or use OpenAI
OPENAI_API_KEY=sk-your-key-here

# Or use HuggingFace (local model download)
HUGGINGFACE_API_KEY=hf_your-key-here
```

**Note**: The system works without API keys, just with reduced AI features.

### 3. Run the Web Interface

```bash
python app.py
```

Open http://localhost:7860 in your browser.

### 4. Search for Jobs

**Option A: Web Interface**
1. Upload your resume
2. Enter job keywords (e.g., "Data Scientist")
3. Select sources (LinkedIn, Indeed, Company Pages)
4. Click "Search Jobs"

**Option B: Python Code**

```python
from agent import JobSearchAgent

agent = JobSearchAgent()

# Search by keywords
jobs = agent.search_jobs(
    resume_source="resume.pdf",
    keywords="Data Scientist",
    companies=["Google", "Meta"],  # Optional
    include_stretch=True,  # Include jobs 1-2 levels above
    top_k=20
)

# Or search by sector
jobs = agent.search_jobs_by_sector(
    resume_source="resume.pdf",
    sector="fintech",
    company_characteristics={"stage": "Series B+"},
    location="San Francisco",
    remote_only=True
)

# View results
for job in jobs:
    print(f"{job['title']} at {job['company']}")
    print(f"  Match: {job['match_score']:.0%}")
    print(f"  Level: {job['level_assessment']}")
```

## Project Structure

```
job-search-agent/
├── agent.py                    # Main agent class
├── job_scraper.py             # Job scraping engine
├── company_discovery.py       # Sector-based company discovery
├── smart_career_scraper.py    # AI-powered scraper for complex sites
├── company_career_finder.py   # Company career page scraper
├── resume_parser.py           # Resume parsing and skill extraction
├── job_level_classifier.py    # Job level classification
├── job_validator.py           # AI job validation
├── llm_analyzer.py            # LLM integration
├── embedding_matcher.py       # Semantic job matching
├── app.py                     # Gradio web interface
├── config.py                  # Configuration settings
│
├── docs/                      # Documentation
│   ├── QUICK_START.md
│   ├── SECTOR_SEARCH_GUIDE.md
│   ├── SMART_SCRAPER_GUIDE.md
│   └── LLM_SETUP_FIX.md
│
├── examples/                  # Usage examples
│   ├── sector_search_example.py
│   ├── quick_test.py
│   └── run_search.py
│
├── tests/                     # Test files
└── output_data/               # Scraped job data
```

## Key Features

### 1. Smart Career Scraping

Handles complex JavaScript-heavy career pages (Block, Airbnb, Stripe, etc.):
- AI-powered page structure analysis
- Automatic category detection and filtering
- Keyword-based relevance filtering
- Multi-strategy extraction

### 2. Sector-Based Search

Discover companies by industry sector:
```python
jobs = agent.search_jobs_by_sector(
    resume_source="resume.pdf",
    sector="AI/ML",  # Or: fintech, crypto, healthtech, etc.
    company_characteristics={
        "size": "medium",           # startup, small, medium, large
        "stage": "Series B+",       # Seed, Series A, B, C+
        "remote_friendly": True
    },
    location="Remote",
    max_companies=20
)
```

### 3. Job Level Classification

Automatically identifies job levels:
- Individual Contributor: Intern → Junior → Mid → Senior → Staff → Principal
- Management: Team Lead → Manager → Director → VP → C-Suite

### 4. Resume Matching

Multi-factor matching algorithm:
- Skill overlap (35%)
- Semantic similarity (25%)
- Level fit (25%)
- Growth potential (15%)

### 5. Stretch Jobs

Identifies jobs 1-2 levels above your current position:
- Good skill match (65%+)
- Clear growth path
- Manageable skill gap

## Configuration

Edit `config.py` to customize:

```python
# LLM Provider
LLM_PROVIDER = "anthropic"  # or "openai", "huggingface"
LLM_MODEL = "claude-3-5-haiku-20241022"

# Local Model (free, no API key needed)
USE_LOCAL_MODEL = True
LLM_MODEL = "Qwen/Qwen2.5-3B-Instruct"

# Matching Weights
WEIGHTS = {
    "skill_match": 0.35,
    "semantic_similarity": 0.25,
    "level_fit": 0.25,
    "growth_potential": 0.15
}
```

## Troubleshooting

### HuggingFace 410 Error

The HuggingFace Inference API is deprecated. Solutions:
1. Add Anthropic/OpenAI API key (recommended)
2. Set `USE_LOCAL_MODEL = True` to download models locally
3. Continue without LLM (basic features still work)

See [docs/LLM_SETUP_FIX.md](docs/LLM_SETUP_FIX.md) for details.

### Category Headers Instead of Jobs

The smart scraper now filters out department categories automatically.
See [docs/CATEGORY_FILTERING_COMPLETE.md](docs/CATEGORY_FILTERING_COMPLETE.md).

### No Relevant Jobs Found

- Try broader keywords
- Remove location restrictions
- Disable keyword filtering: `keywords=""`

## Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started quickly
- **[Sector Search Guide](docs/SECTOR_SEARCH_GUIDE.md)** - Search by industry
- **[Smart Scraper Guide](docs/SMART_SCRAPER_GUIDE.md)** - Handle complex sites
- **[LLM Setup Guide](docs/LLM_SETUP_FIX.md)** - Configure AI features

## Requirements

- Python 3.8+
- Chrome/Chromium (for Selenium)
- 4GB+ RAM
- Optional: GPU for local models

## License

MIT License

## Contributing

Pull requests welcome! Please ensure:
- Code follows existing style
- Tests pass
- Documentation updated

## Credits

Built with:
- Selenium & BeautifulSoup (web scraping)
- Sentence Transformers (embeddings)
- Anthropic Claude / OpenAI GPT (LLM)
- Gradio (web interface)
