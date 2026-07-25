import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db", "jobs.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the jobs table if it doesn't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            url TEXT UNIQUE,
            salary_min REAL,
            salary_max REAL,
            source TEXT,
            date_fetched TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database ready at {DB_PATH}")


def save_jobs(jobs, source="adzuna"):
    """Insert a list of job dicts into the jobs table. Skips duplicates by URL."""
    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    for job in jobs:
        try:
            cursor.execute("""
                INSERT INTO jobs (title, company, location, description, url, salary_min, salary_max, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.get("title"),
                job.get("company"),
                job.get("location"),
                job.get("description"),
                job.get("url"),
                job.get("salary_min"),
                job.get("salary_max"),
                source,
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            # URL already exists, skip duplicate
            pass

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} new jobs (duplicates skipped)")


if __name__ == "__main__":
    init_db()