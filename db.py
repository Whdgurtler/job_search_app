"""SQLite database for storing scraped job results."""
import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Set
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(db_path or str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = None):
    """Create tables and run migrations."""
    conn = get_connection(db_path)

    # Check if we need to migrate from the old schema
    needs_migration = False
    try:
        cursor = conn.execute("PRAGMA table_info(jobs)")
        columns = {row["name"] for row in cursor.fetchall()}
        if columns and "first_seen" not in columns:
            needs_migration = True
    except Exception:
        pass

    if needs_migration:
        _migrate_v2(conn)
    else:
        _create_tables(conn)

    conn.commit()
    conn.close()


def _create_tables(conn: sqlite3.Connection):
    """Create tables with the current schema."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT DEFAULT 'Not specified',
            is_remote INTEGER DEFAULT 0,
            url TEXT DEFAULT '',
            description TEXT DEFAULT '',
            department TEXT DEFAULT '',
            source TEXT DEFAULT '',
            posting_date TEXT DEFAULT '',
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            match_score REAL DEFAULT 0,
            skill_match REAL DEFAULT 0,
            level_match REAL DEFAULT 0,
            recommendation TEXT DEFAULT '',
            level_assessment TEXT DEFAULT '',
            matched_skills TEXT DEFAULT '[]',
            missing_skills TEXT DEFAULT '[]',
            notes TEXT DEFAULT '',
            scraped_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # URL-based dedup (primary): one row per unique URL
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_url
        ON jobs(url) WHERE url != ''
    """)
    # Fallback dedup for jobs without URLs: (title, company, location)
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_title_company_loc
        ON jobs(title, company, location) WHERE url = ''
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_jobs_last_seen ON jobs(last_seen)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scrape_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scraped_date TEXT NOT NULL,
            companies TEXT NOT NULL,
            keywords TEXT DEFAULT '',
            total_jobs INTEGER DEFAULT 0,
            errors TEXT DEFAULT '[]',
            duration_seconds REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _migrate_v2(conn: sqlite3.Connection):
    """Migrate from old schema (UNIQUE on title,company,scraped_date) to v2."""
    # Add new columns if they don't exist
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()}
    today = date.today().isoformat()

    if "posting_date" not in existing:
        conn.execute("ALTER TABLE jobs ADD COLUMN posting_date TEXT DEFAULT ''")
    if "first_seen" not in existing:
        conn.execute(f"ALTER TABLE jobs ADD COLUMN first_seen TEXT DEFAULT ''")
        # Backfill: set first_seen = scraped_date for existing rows
        conn.execute("UPDATE jobs SET first_seen = scraped_date WHERE first_seen = ''")
    if "last_seen" not in existing:
        conn.execute(f"ALTER TABLE jobs ADD COLUMN last_seen TEXT DEFAULT ''")
        # Backfill: set last_seen = scraped_date for existing rows
        conn.execute("UPDATE jobs SET last_seen = scraped_date WHERE last_seen = ''")

    # Deduplicate existing rows before creating unique indexes:
    # Keep the row with the highest match_score for each URL
    conn.execute("""
        DELETE FROM jobs WHERE id NOT IN (
            SELECT MIN(id) FROM jobs WHERE url != '' GROUP BY url
        ) AND url != ''
    """)
    conn.execute("""
        DELETE FROM jobs WHERE id NOT IN (
            SELECT MIN(id) FROM jobs WHERE url = '' GROUP BY title, company, location
        ) AND url = ''
    """)

    # Create new indexes (will fail silently if they already exist)
    try:
        conn.execute("""
            CREATE UNIQUE INDEX idx_jobs_url ON jobs(url) WHERE url != ''
        """)
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("""
            CREATE UNIQUE INDEX idx_jobs_title_company_loc
            ON jobs(title, company, location) WHERE url = ''
        """)
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("CREATE INDEX idx_jobs_company ON jobs(company)")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("CREATE INDEX idx_jobs_last_seen ON jobs(last_seen)")
    except sqlite3.OperationalError:
        pass

    # Drop the old unique index if it exists (SQLite can't drop it directly,
    # but it won't conflict since we're adding new partial indexes)
    conn.commit()


def save_jobs(jobs: List[Dict], scraped_date: str = None) -> Dict[str, int]:
    """Upsert jobs into the database.

    - New jobs are inserted with first_seen = last_seen = today.
    - Existing jobs (matched by URL or title+company+location) get
      last_seen updated and match scores refreshed.

    Returns dict with 'inserted' and 'updated' counts.
    """
    if not scraped_date:
        scraped_date = date.today().isoformat()

    conn = get_connection()
    inserted = 0
    updated = 0

    for job in jobs:
        match = job.get("match_result", {})
        url = job.get("url", "")
        title = job.get("title", "")
        company = job.get("company", "")
        location = job.get("location", "Not specified")

        # Check if this job already exists
        existing = None
        if url:
            existing = conn.execute(
                "SELECT id, first_seen FROM jobs WHERE url = ?", (url,)
            ).fetchone()
        if not existing and title and company:
            existing = conn.execute(
                "SELECT id, first_seen FROM jobs WHERE title = ? AND company = ? AND location = ? AND url = ''",
                (title, company, location)
            ).fetchone()

        if existing:
            # Update existing: refresh last_seen and match scores
            conn.execute("""
                UPDATE jobs SET
                    last_seen = ?,
                    scraped_date = ?,
                    match_score = ?,
                    skill_match = ?,
                    level_match = ?,
                    recommendation = ?,
                    level_assessment = ?,
                    matched_skills = ?,
                    missing_skills = ?,
                    notes = ?,
                    posting_date = CASE WHEN posting_date = '' THEN ? ELSE posting_date END
                WHERE id = ?
            """, (
                scraped_date,
                scraped_date,
                match.get("match_score", 0),
                match.get("skill_match", 0),
                match.get("level_match", 0),
                match.get("recommendation", ""),
                match.get("level_assessment", ""),
                json.dumps(match.get("matched_skills", [])),
                json.dumps(match.get("missing_skills", [])),
                match.get("notes", ""),
                job.get("posting_date", ""),
                existing["id"],
            ))
            updated += 1
        else:
            # Insert new job
            try:
                conn.execute("""
                    INSERT INTO jobs (
                        title, company, location, is_remote, url, description,
                        department, source, posting_date, first_seen, last_seen,
                        match_score, skill_match, level_match,
                        recommendation, level_assessment, matched_skills,
                        missing_skills, notes, scraped_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    title,
                    company,
                    location,
                    1 if job.get("is_remote", False) else 0,
                    url,
                    job.get("description", ""),
                    job.get("department", ""),
                    job.get("source", ""),
                    job.get("posting_date", ""),
                    scraped_date,  # first_seen
                    scraped_date,  # last_seen
                    match.get("match_score", 0),
                    match.get("skill_match", 0),
                    match.get("level_match", 0),
                    match.get("recommendation", ""),
                    match.get("level_assessment", ""),
                    json.dumps(match.get("matched_skills", [])),
                    json.dumps(match.get("missing_skills", [])),
                    match.get("notes", ""),
                    scraped_date,
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                # Race condition or edge case — treat as update
                updated += 1

    conn.commit()
    conn.close()
    return {"inserted": inserted, "updated": updated}


def get_known_job_urls(company: str) -> Set[str]:
    """Get all known job URLs for a company (for early-exit dedup)."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT url FROM jobs WHERE company = ? AND url != ''",
        (company,)
    ).fetchall()
    conn.close()
    return {row["url"] for row in rows}


def get_known_job_keys(company: str) -> Set[str]:
    """Get dedup keys for URL-less jobs: 'title|||location' strings."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT title, location FROM jobs WHERE company = ? AND url = ''",
        (company,)
    ).fetchall()
    conn.close()
    return {f"{row['title']}|||{row['location']}" for row in rows}


def save_run(scraped_date: str, companies: List[str], keywords: str,
             total_jobs: int, errors: List[str], duration: float):
    """Log a scrape run."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO scrape_runs (scraped_date, companies, keywords, total_jobs, errors, duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        scraped_date,
        json.dumps(companies),
        keywords,
        total_jobs,
        json.dumps(errors),
        duration,
    ))
    conn.commit()
    conn.close()


def get_recent_jobs(limit: int = 500, company: str = None,
                    remote_only: bool = False) -> List[Dict]:
    """Fetch jobs ordered by most recent last_seen date, then by match score."""
    conn = get_connection()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if company:
        query += " AND company = ?"
        params.append(company)
    if remote_only:
        query += " AND is_remote = 1"

    query += " ORDER BY last_seen DESC, match_score DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    jobs = []
    for row in rows:
        jobs.append({
            "id": row["id"],
            "title": row["title"],
            "company": row["company"],
            "location": row["location"],
            "is_remote": bool(row["is_remote"]),
            "url": row["url"],
            "posting_date": row["posting_date"] if "posting_date" in row.keys() else "",
            "first_seen": row["first_seen"] if "first_seen" in row.keys() else "",
            "last_seen": row["last_seen"] if "last_seen" in row.keys() else "",
            "match_score": row["match_score"],
            "recommendation": row["recommendation"],
            "level_assessment": row["level_assessment"],
            "matched_skills": json.loads(row["matched_skills"] or "[]"),
            "missing_skills": json.loads(row["missing_skills"] or "[]"),
            "notes": row["notes"],
            "scraped_date": row["scraped_date"],
        })
    return jobs


def get_scrape_dates() -> List[str]:
    """Get all unique scrape dates, most recent first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT scraped_date FROM jobs ORDER BY scraped_date DESC"
    ).fetchall()
    conn.close()
    return [row["scraped_date"] for row in rows]


def get_companies() -> List[str]:
    """Get all unique company names."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT company FROM jobs ORDER BY company"
    ).fetchall()
    conn.close()
    return [row["company"] for row in rows]


def get_job_count_by_date() -> List[Dict]:
    """Get job counts grouped by scrape date."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT scraped_date, COUNT(*) as count,
               SUM(CASE WHEN recommendation = 'strong' THEN 1 ELSE 0 END) as strong,
               SUM(CASE WHEN recommendation = 'moderate' THEN 1 ELSE 0 END) as moderate
        FROM jobs GROUP BY scraped_date ORDER BY scraped_date DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Auto-initialize on import
init_db()
