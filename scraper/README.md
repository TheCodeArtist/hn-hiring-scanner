# HN Job Scraper

A lightweight script for scraping job postings from Hacker News "Who's hiring?" threads using the official Hacker News API.

## Overview

### `hn-api-scraper.py` - API-Based Scraper

This script uses the official Hacker News API to fetch job postings. It focuses purely on data collection without any AI/LLM processing.

**Features:**
- ✅ Uses official HN API (no HTML parsing)
- ✅ Async/concurrent requests for speed
- ✅ Comprehensive logging to file
- ✅ Configurable rate limiting
- ✅ Single JSON file output
- ✅ Support for both URL and thread ID input

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage with URL
python hn-api-scraper.py https://news.ycombinator.com/item?id=46857488

# Using just the thread ID
python hn-api-scraper.py 46857488

# Custom output file
python hn-api-scraper.py 46857488 --output jobs.json

# With rate limiting and concurrency control
python hn-api-scraper.py 46857488 --max-concurrent 20 --delay 0.05

# Limit number of posts (for testing)
python hn-api-scraper.py 46857488 --limit 50

# Verbose logging
python hn-api-scraper.py 46857488 -v

# All options
python hn-api-scraper.py 46857488 \
  --output my_jobs.json \
  --limit 100 \
  --max-concurrent 15 \
  --delay 0.1 \
  --log-file my_scraper.log \
  -v
```

### Command-line Arguments
- `url_or_id` (required): HN thread URL or thread ID
- `-o, --output`: Output JSON file path (default: `scraped_jobs.json`)
- `--limit`: Limit number of comments to fetch (for testing)
- `--max-concurrent`: Maximum concurrent API requests (default: 10)
- `--delay`: Delay between requests in seconds (default: 0.1)
- `--log-file`: Log file path (default: `scraper.log`)
- `-v, --verbose`: Enable verbose logging to console

### Output Format

The script saves all job postings to a single JSON file:

```json
[
  {
    "id": 43206327,
    "by": "username",
    "time": 1704067200,
    "text": "Full job posting text with HTML formatting...",
    "type": "comment",
    "parent": 43206326
  },
  ...
]
```

### Logging

All operations are logged to a file (default: `scraper.log`) including:
- Thread information
- Scraping progress
- Success/error rates
- Timing information
- Any errors encountered


## Examples

### Finding Latest Hiring Thread

Visit [Hacker News](https://news.ycombinator.com/) and search for "Ask HN: Who is hiring?" to find the latest thread.

### Quick Test

```bash
# Scrape just 10 posts for testing
python hn-api-scraper.py 46857488 --limit 10 -v
```

### Production Use

```bash
# Scrape with moderate rate limiting
python hn-api-scraper.py 46857488 \
  --output "jobs_$(date +%Y%m%d).json" \
  --max-concurrent 15 \
  --delay 0.1 \
  --log-file "scraper_$(date +%Y%m%d).log"
```

### `compare_jobs.py` - Job Comparison Tool

This script compares two JSON files containing HackerNews job postings and identifies entries that are new or have been updated.

**Features:**
- ✅ Identifies new job entries (entries with IDs not present in original file)
- ✅ Identifies updated entries (entries where the `text` field has changed)
- ✅ Comprehensive logging to file and console
- ✅ Detailed summary statistics
- ✅ JSON output with comparison metadata
- ✅ Error handling for malformed data

**Usage:**

```bash
# Basic comparison
python compare_jobs.py --original old_jobs.json --updated new_jobs.json

# Custom output and log files
python compare_jobs.py \
  --original old_jobs.json \
  --updated new_jobs.json \
  --output changes.json \
  --log comparison.log
```

**Command-line Arguments:**
- `--original` (required): Path to the original JSON file
- `--updated` (required): Path to the updated JSON file
- `--output`: Output JSON file path (default: `updated_entries.json`)
- `--log`: Log file path (default: `comparison.log`)

**Output Format:**

The script generates a JSON file with the following structure:

```json
{
  "comparison_date": "2026-02-10T13:24:04.626952+00:00",
  "original_file": "old_jobs.json",
  "updated_file": "new_jobs.json",
  "summary": {
    "total_original": 100,
    "total_updated": 108,
    "new_entries": 10,
    "updated_entries": 3,
    "unchanged_entries": 95
  },
  "new_entries": [
    {
      "by": "username",
      "id": 100004,
      "text": "New job posting...",
      ...
    }
  ],
  "updated_entries": [
    {
      "by": "username",
      "id": 100002,
      "text": "Updated job posting...",
      ...
    }
  ]
}
```

**Comparison Logic:**
- **New Entry**: An entry with an `id` that doesn't exist in the original file
- **Updated Entry**: An entry where the `id` exists in both files but the `text` field has changed (exact string match)
- **Unchanged Entry**: An entry where both `id` and `text` are identical

**Example Workflow:**

```bash
# 1. Scrape the current month's jobs
python hn-api-scraper.py 46857488 --output jan_2026.json

# ... wait a few days ...

# 2. Scrape again to get updates
python hn-api-scraper.py 46857488 --output jan_2026_updated.json

# 3. Find what changed
python compare_jobs.py \
  --original jan_2026.json \
  --updated jan_2026_updated.json \
  --output jan_changes.json
```

---

## License

MIT
