#!/usr/bin/env python3
"""
Tender Tracker — main scraper.

Fetches each source in config.SOURCES, parses tender listings, filters
them against config.KEYWORDS, classifies by config.SERVICES, and writes:
  - data/tenders.json   (raw matched data, also keeps history)
  - docs/index.html     (the dashboard, viewable in a browser /
                          deployable to GitHub Pages)

Run:
    python scrapers/run.py

Schedule daily via cron or GitHub Actions (see .github/workflows/daily.yml).
"""

import sys
import os
import json
import datetime
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from scrapers.parsers import PARSERS, generic_fallback

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

TIMEOUT = 25


def fetch(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=True)
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.SSLError:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  [ERROR] {url} -> {e}")
            return None
    except Exception as e:
        print(f"  [ERROR] {url} -> {e}")
        return None


import re


def _normalize(text):
    """Lowercase and collapse reference codes / punctuation so 'BC' inside
    'TB-S/RFP/MABC/2026' doesn't false-match ' bc'. Returns text with
    non-alphanumeric chars replaced by spaces, padded with spaces."""
    cleaned = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return f" {cleaned} "


def matches_keywords(title):
    norm = _normalize(title)
    hits = []
    for kw in config.KEYWORDS:
        kw_clean = kw.strip().lower()
        if not kw_clean:
            continue
        # multi-word keywords: substring match on normalized text
        if " " in kw_clean:
            if kw_clean in norm:
                hits.append(kw_clean)
        else:
            # single-word keywords (e.g. "bc", "cms", "aeps", "dmt"):
            # require word-boundary match to avoid matching inside codes
            if re.search(rf"\b{re.escape(kw_clean)}\b", norm):
                hits.append(kw_clean)
    return hits


def classify_services(title):
    norm = _normalize(title)
    matched = []
    for service, kws in config.SERVICES.items():
        for kw in kws:
            kw_clean = kw.strip().lower()
            if not kw_clean:
                continue
            if " " in kw_clean:
                if kw_clean in norm:
                    matched.append(service)
                    break
            else:
                if re.search(rf"\b{re.escape(kw_clean)}\b", norm):
                    matched.append(service)
                    break
    return matched


def run():
    all_results = []
    run_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for source in config.SOURCES:
        print(f"Fetching: {source['name']} -> {source['url']}")
        html = fetch(source["url"])
        if html is None:
            all_results.append({
                "source": source["name"],
                "url": source["url"],
                "status": "fetch_failed",
                "tenders": [],
            })
            continue

        parser_fn = PARSERS.get(source["parser"], generic_fallback)
        try:
            items = parser_fn(html, source["url"])
        except Exception as e:
            print(f"  [PARSE ERROR] {source['name']} -> {e}, falling back to generic parser")
            try:
                items = generic_fallback(html, source["url"])
            except Exception as e2:
                print(f"  [GENERIC FALLBACK FAILED] {source['name']} -> {e2}")
                items = []

        # Filter + classify
        relevant = []
        for item in items:
            hits = matches_keywords(item["title"])
            if not hits:
                continue
            services = classify_services(item["title"])
            relevant.append({
                **item,
                "matched_keywords": hits,
                "relevant_services": services,
            })

        print(f"  -> {len(items)} items found, {len(relevant)} keyword matches")

        all_results.append({
            "source": source["name"],
            "url": source["url"],
            "status": "ok",
            "total_items_scanned": len(items),
            "tenders": relevant,
        })

    output = {
        "generated_at": run_time,
        "keywords": config.KEYWORDS,
        "services": list(config.SERVICES.keys()),
        "results": all_results,
    }

    os.makedirs(os.path.dirname(config.OUTPUT_JSON), exist_ok=True)
    with open(config.OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {config.OUTPUT_JSON}")

    # Generate dashboard HTML
    from scrapers.render_dashboard import render
    os.makedirs(os.path.dirname(config.OUTPUT_HTML), exist_ok=True)
    render(output, config.OUTPUT_HTML)
    print(f"Wrote {config.OUTPUT_HTML}")


if __name__ == "__main__":
    run()
