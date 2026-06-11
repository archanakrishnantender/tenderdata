"""
Parsers for each source's tender listing page.

Each parser function takes raw HTML (str) and the base URL, and returns
a list of dicts:
    {
        "title": str,
        "date": str,        # best-effort, "" if not found
        "links": [ {"label": str, "url": str}, ... ],
        "location": str,    # best-effort, "" if not found
    }

If a bank changes its website structure, only that parser needs updating.
A generic fallback parser is provided for unknown/changed structures —
it pulls all links containing common tender keywords from the page.
"""

from urllib.parse import urljoin
from bs4 import BeautifulSoup


def _abs_url(base, href):
    if not href:
        return ""
    return urljoin(base, href)


def parse_sbi(html, base_url):
    """SBI procurement/archived-tenders page: markdown-like table with
    Location | Tender Description | Start Date | End Date | [docs]"""
    soup = BeautifulSoup(html, "lxml")
    results = []
    table = soup.find("table")
    if not table:
        return generic_fallback(html, base_url)

    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        if len(cells) < 4:
            continue
        location = cells[0].get_text(strip=True)
        if location.lower() in ("location", ""):
            continue
        title_cell = cells[1]
        title = title_cell.get_text(" ", strip=True)
        start_date = cells[2].get_text(strip=True) if len(cells) > 2 else ""
        end_date = cells[3].get_text(strip=True) if len(cells) > 3 else ""

        links = []
        # links may be in cell 4 or scattered within title cell
        for c in cells[1:]:
            for a in c.find_all("a", href=True):
                label = a.get_text(strip=True) or "Document"
                links.append({"label": label, "url": _abs_url(base_url, a["href"])})

        if not title:
            continue

        results.append({
            "title": title,
            "date": f"{start_date} - {end_date}".strip(" -"),
            "links": links,
            "location": location,
        })
    return results


def parse_bob(html, base_url):
    return generic_fallback(html, base_url)


def parse_nabard(html, base_url):
    return generic_fallback(html, base_url)


def parse_sidbi(html, base_url):
    return generic_fallback(html, base_url)


def parse_pnb(html, base_url):
    return generic_fallback(html, base_url)


def parse_canara(html, base_url):
    return generic_fallback(html, base_url)


def parse_boi(html, base_url):
    return generic_fallback(html, base_url)


def parse_union(html, base_url):
    return generic_fallback(html, base_url)


def generic_fallback(html, base_url):
    """
    Generic fallback: scan every link/row on the page. Useful for sites
    whose structure isn't specifically mapped, or has changed. Less
    precise than dedicated parsers, but ensures something is captured.

    Strategy:
      - Look for <a> tags whose text or href looks tender-related
        (mentions 'tender', 'rfp', 'eoi', 'procurement', 'notice', '.pdf')
      - Group by nearest table row / list item for context (date, location)
    """
    soup = BeautifulSoup(html, "lxml")
    results = []
    seen_titles = set()

    candidates_keywords = ["tender", "rfp", "eoi", "procurement", "notice",
                            "expression of interest", "empanelment", "bid"]

    # Try table rows first
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            text = row.get_text(" ", strip=True)
            if not text or len(text) < 8:
                continue
            lower = text.lower()
            if not any(k in lower for k in candidates_keywords):
                continue
            links = []
            for a in row.find_all("a", href=True):
                label = a.get_text(strip=True) or "Document"
                links.append({"label": label, "url": _abs_url(base_url, a["href"])})
            title = text[:300]
            if title in seen_titles:
                continue
            seen_titles.add(title)
            results.append({"title": title, "date": "", "links": links, "location": ""})

    if results:
        return results

    # Fall back to scanning standalone links/list items
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        lower_text = text.lower()
        lower_href = href.lower()
        if any(k in lower_text for k in candidates_keywords) or \
           (href.lower().endswith(".pdf") and any(k in lower_text for k in candidates_keywords)):
            if not text or text in seen_titles:
                continue
            seen_titles.add(text)
            results.append({
                "title": text[:300],
                "date": "",
                "links": [{"label": "Document" if not text else text, "url": _abs_url(base_url, href)}],
                "location": "",
            })

    return results


PARSERS = {
    "sbi": parse_sbi,
    "bob": parse_bob,
    "nabard": parse_nabard,
    "sidbi": parse_sidbi,
    "pnb": parse_pnb,
    "canara": parse_canara,
    "boi": parse_boi,
    "union": parse_union,
    "generic": generic_fallback,
}
