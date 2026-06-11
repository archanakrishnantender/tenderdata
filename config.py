"""
Configuration for the Tender Tracker.
Edit KEYWORDS, SERVICES, and SOURCES to customize what gets tracked.
"""

# ----------------------------------------------------------------------
# KEYWORDS — tender titles/descriptions are matched (case-insensitive)
# against this list. A tender is flagged as "RELEVANT" if ANY keyword
# is found in its title.
# ----------------------------------------------------------------------
KEYWORDS = [
    # Core BC / Financial Inclusion
    "business correspondent", "banking correspondent", "bc",
    "financial inclusion", "corporate bc",
    # AEPS / Micro ATM / DMT
    "aeps", "micro atm", "micro-atm", "dmt", "domestic money transfer",
    "aadhaar enabled payment",
    # Merchant acquisition / QR / POS / Soundbox
    "merchant acquisition", "merchant onboarding", "qr deployment",
    "qr code", "pos deployment", "point of sale", "soundbox", "sound box",
    # CMS
    "cash management service", "cash management services", "cms",
    "cash collection service", "cash pickup",
    # API / Tech
    "api integration", "technology service provider", "fintech",
    "digital banking", "core banking",
    # Loans & Insurance
    "loan sourcing", "insurance distribution", "corporate agent",
    "bancassurance",
]

# ----------------------------------------------------------------------
# SERVICES — your company's offerings, used to map a matched tender to
# the relevant service line in the dashboard report.
# ----------------------------------------------------------------------
SERVICES = {
    "Business Correspondent Services": ["business correspondent", "banking correspondent", "corporate bc", "financial inclusion", "bc"],
    "AEPS": ["aeps", "aadhaar enabled payment"],
    "DMT": ["dmt", "domestic money transfer"],
    "QR Deployment": ["qr deployment", "qr code"],
    "Soundbox Deployment": ["soundbox", "sound box"],
    "POS Deployment": ["pos deployment", "point of sale", "micro atm", "micro-atm"],
    "CMS": ["cash management service", "cash management services", "cms", "cash collection service", "cash pickup"],
    "API Integration": ["api integration", "technology service provider", "fintech", "digital banking", "core banking"],
    "Loan Sourcing": ["loan sourcing"],
    "Insurance Distribution": ["insurance distribution", "corporate agent", "bancassurance"],
}

# ----------------------------------------------------------------------
# SOURCES — official, publicly-accessible procurement/tender pages.
# Each entry has a parser key (see scrapers/parsers.py) telling the
# scraper how to read that site's HTML structure.
# ----------------------------------------------------------------------
SOURCES = [
    {
        "name": "SBI",
        "url": "https://sbi.bank.in/web/sbi-in-the-news/procurement-news/archived-tenders",
        "parser": "sbi",
    },
    {
        "name": "SBI - Current Procurement News",
        "url": "https://sbi.bank.in/web/sbi-in-the-news/procurement-news",
        "parser": "sbi",
    },
    {
        "name": "Bank of Baroda",
        "url": "https://www.bankofbaroda.in/tenders",
        "parser": "bob",
    },
    {
        "name": "NABARD",
        "url": "https://www.nabard.org/tenders.aspx",
        "parser": "nabard",
    },
    {
        "name": "SIDBI",
        "url": "https://www.sidbi.in/en/tenders",
        "parser": "sidbi",
    },
    {
        "name": "Punjab National Bank",
        "url": "https://www.pnbindia.in/Tenders.html",
        "parser": "pnb",
    },
    {
        "name": "Canara Bank",
        "url": "https://canarabank.com/Tenders",
        "parser": "canara",
    },
    {
        "name": "Bank of India",
        "url": "https://bankofindia.co.in/tenders",
        "parser": "boi",
    },
    {
        "name": "Union Bank of India",
        "url": "https://www.unionbankofindia.co.in/english/tenders.aspx",
        "parser": "union",
    },
]

# ----------------------------------------------------------------------
# QUICK-SEARCH LINKS — for portals that CANNOT be scraped automatically
# (GeM, CPPP/eProcure require login/captcha/JS sessions). The dashboard
# shows one-click pre-filled search links for these instead.
# ----------------------------------------------------------------------
QUICK_SEARCH_PORTALS = [
    {
        "name": "GeM (Government e-Marketplace)",
        "note": "Login required for full bid search. Use Seller Dashboard > Bids/RA for category-matched tenders.",
        "links": [
            {"label": "GeM Bid Search", "url": "https://bidplus.gem.gov.in/all-bids"},
        ],
    },
    {
        "name": "CPPP / eProcure (Govt e-Procurement)",
        "note": "Central Public Procurement Portal. Search requires session; use the search page directly.",
        "links": [
            {"label": "CPPP Tender Search", "url": "https://eprocure.gov.in/cppp/latestactivetendersnew/cpppdata"},
        ],
    },
]

# Output paths
OUTPUT_JSON = "data/tenders.json"
OUTPUT_HTML = "docs/index.html"
