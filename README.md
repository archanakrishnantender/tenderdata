# Tender Radar — Daily BFSI Opportunity Tracker

A small, self-hosted system that checks bank/financial-institution tender
pages every day, filters them against your service keywords (BC, AEPS,
DMT, QR, Soundbox, POS, CMS, API Integration, Loan Sourcing, Insurance
Distribution, etc.), and produces a static dashboard you (and your team)
can bookmark and check daily.

## What this does

- **Scrapes** the public tender/procurement pages of SBI and other listed
  banks (`config.py` → `SOURCES`)
- **Filters** every tender title against your keyword list
  (`config.py` → `KEYWORDS`)
- **Classifies** matches by which of your services they relate to
  (`config.py` → `SERVICES`)
- **Outputs** `data/tenders.json` (raw data) which the `index.html` 
  dashboard automatically loads and displays — open this in any browser!
- For **GeM and CPPP/eProcure**, which block automated scraping, the
  dashboard shows direct links to search those portals manually —
  GeM tenders matching your registered seller categories will also
  appear automatically in your GeM Seller Dashboard.

## Important: this needs to run where it has internet access

This package was built inside a sandboxed environment that cannot reach
bank websites. The scraper itself works correctly (tested against real
SBI data), but **you need to run it somewhere with normal internet
access** — your laptop, a small server, or for free: GitHub Actions.

---

## Option 1 — Run it yourself (simplest, manual)

1. Install Python 3.9+ if you don't have it.
2. Open a terminal in this folder and run:
   ```
   pip install -r requirements.txt
   python scrapers/run.py
   ```
3. Open `index.html` in your browser. That's your dashboard.
4. Re-run `python scrapers/run.py` whenever you want fresh data
   (e.g. once a day).

To automate the daily run on your own machine:
- **Windows**: use Task Scheduler to run
  `python C:\path\to\tender-tracker\scrapers\run.py` daily.
- **Mac/Linux**: add a cron entry:
  ```
  0 8 * * * cd /path/to/tender-tracker && python3 scrapers/run.py
  ```

---

## Option 2 — Free live dashboard via GitHub (recommended for "live")

This runs the scraper automatically every day on GitHub's servers and
publishes the dashboard as a public webpage via GitHub Pages — no
server of your own needed.

1. Create a free GitHub account if you don't have one.
2. Create a new repository (can be private or public) and upload all
   files in this folder to it.
3. In the repo, go to **Settings → Pages** → set "Source" to
   **GitHub Actions**.
4. Go to the **Actions** tab → you'll see "Daily Tender Scrape" →
   click **Run workflow** to trigger it manually the first time.
5. After it completes, your dashboard will be live at:
   `https://<your-username>.github.io/<repo-name>/`
6. From then on, it runs automatically every day at 03:00 UTC
   (~8:30 AM IST) and updates the page.

To change the schedule time, edit `.github/workflows/daily.yml`,
the `cron` line (uses UTC time).

---

## Customizing

### Add/remove keywords
Edit `config.py` → `KEYWORDS`. Matching is case-insensitive and uses
word boundaries, so "BC" won't accidentally match inside codes like
"MABC".

### Add/remove your services
Edit `config.py` → `SERVICES`. Each service maps to a list of keywords;
when a tender title matches any of them, it's tagged with that service
in the dashboard.

### Add more bank/institution sources
Edit `config.py` → `SOURCES`. Each entry needs:
```python
{
    "name": "Bank Name",
    "url": "https://bank-website.com/tenders-page",
    "parser": "generic",   # use "generic" unless you write a custom parser
}
```
The `"generic"` parser scans the page for tender-related links/rows and
works reasonably well on most static tender-listing pages. If a specific
bank's page isn't being parsed well, a custom parser can be added in
`scrapers/parsers.py` (the SBI parser is a working example).

### Sites that may need adjustment
Bank websites change their HTML structure periodically. If a source
shows "fetch failed" or "0 matches" when you expect results, check:
1. Open the URL in a browser — has the page moved?
2. Update the URL in `config.py` if needed.
3. If the generic parser isn't catching tenders, a dedicated parser
   function may be needed (see `parse_sbi` in `scrapers/parsers.py`
   as a template).

---

## GeM & CPPP — why these aren't auto-scraped

- **GeM (gem.gov.in)**: Bid search requires a logged-in session and uses
  dynamic JavaScript with anti-bot protection. The legitimate, reliable
  way to see relevant tenders is through your **GeM Seller Dashboard**
  (Bids/RA section) once your company is registered under the relevant
  categories — matching bids appear there automatically.
- **CPPP/eProcure (eprocure.gov.in)**: Similarly requires session-based
  search and discourages automated access per its terms of use.

The dashboard provides direct links to both portals' search pages for
quick manual checks as part of your daily routine.

---

## File structure

```
tender-tracker/
├── config.py                  # keywords, services, sources — edit this
├── requirements.txt
├── scrapers/
│   ├── run.py                 # main scraper — run this
│   ├── parsers.py             # per-site HTML parsers
│   └── render_dashboard.py    # builds docs/index.html
├── data/
│   └── tenders.json           # latest scrape results (raw data)
├── docs/
│   └── index.html             # the dashboard — open in browser
└── .github/workflows/daily.yml  # auto-run + auto-publish (GitHub Actions)
```
