#!/usr/bin/env python3
"""
Renders data/tenders.json into docs/index.html — a self-contained,
static dashboard (no server needed). Open in any browser, or deploy
the docs/ folder to GitHub Pages / any static host.
"""

import json
import html as html_lib
import datetime


def esc(s):
    return html_lib.escape(str(s or ""))


def render(data, output_path):
    generated = data.get("generated_at", "")
    try:
        dt = datetime.datetime.fromisoformat(generated.replace("Z", "+00:00"))
        generated_display = dt.strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        generated_display = generated

    services = data.get("services", [])
    results = data.get("results", [])

    total_matches = sum(len(r.get("tenders", [])) for r in results)
    sources_ok = sum(1 for r in results if r.get("status") == "ok")
    sources_failed = sum(1 for r in results if r.get("status") != "ok")

    # Build per-source sections
    source_sections = []
    for r in results:
        name = esc(r["source"])
        url = esc(r["url"])
        status = r.get("status")
        tenders = r.get("tenders", [])

        if status == "not_yet_run":
            source_sections.append(f"""
            <section class="source-block">
              <div class="source-head">
                <h3>{name}</h3>
                <span class="badge badge-empty">not yet run</span>
              </div>
              <p class="muted">Run <code>python scrapers/run.py</code> to fetch this source. Page: <a href="{url}" target="_blank" rel="noopener">{url}</a></p>
            </section>""")
            continue

        if status != "ok":
            source_sections.append(f"""
            <section class="source-block source-failed">
              <div class="source-head">
                <h3>{name}</h3>
                <span class="badge badge-fail">fetch failed</span>
              </div>
              <p class="muted">Could not reach <a href="{url}" target="_blank" rel="noopener">{url}</a>. The site may have changed structure, blocked automated access, or be temporarily down.</p>
            </section>""")
            continue

        if not tenders:
            source_sections.append(f"""
            <section class="source-block">
              <div class="source-head">
                <h3>{name}</h3>
                <span class="badge badge-empty">0 matches</span>
              </div>
              <p class="muted">Scanned {esc(r.get('total_items_scanned', 0))} items — none matched your keyword list today.</p>
            </section>""")
            continue

        rows = []
        for t in tenders:
            title = esc(t["title"])
            date = esc(t.get("date", ""))
            location = esc(t.get("location", ""))
            kws = ", ".join(esc(k.strip()) for k in t.get("matched_keywords", []))
            services_hit = t.get("relevant_services", [])
            services_html = "".join(f'<span class="tag">{esc(s)}</span>' for s in services_hit) or '<span class="tag tag-muted">Unclassified</span>'

            links_html = ""
            for link in t.get("links", []):
                links_html += f'<a class="doc-link" href="{esc(link["url"])}" target="_blank" rel="noopener">{esc(link["label"])}</a>'
            if not links_html:
                links_html = '<span class="muted">no documents found</span>'

            rows.append(f"""
              <tr>
                <td class="col-title">
                  <div class="title-text">{title}</div>
                  <div class="services-row">{services_html}</div>
                  <div class="kw-row">matched: {kws}</div>
                </td>
                <td class="col-meta">{date or '&mdash;'}</td>
                <td class="col-meta">{location or '&mdash;'}</td>
                <td class="col-docs">{links_html}</td>
              </tr>""")

        source_sections.append(f"""
            <section class="source-block">
              <div class="source-head">
                <h3>{name}</h3>
                <span class="badge badge-ok">{len(tenders)} match{'es' if len(tenders) != 1 else ''}</span>
                <a class="source-link" href="{url}" target="_blank" rel="noopener">view source &rarr;</a>
              </div>
              <table class="tender-table">
                <thead>
                  <tr><th>Tender</th><th>Date</th><th>Location</th><th>Documents</th></tr>
                </thead>
                <tbody>
                  {''.join(rows)}
                </tbody>
              </table>
            </section>""")

    sources_html = "\n".join(source_sections)

    # Quick search portals (GeM / CPPP)
    quick_search_html = """
        <section class="source-block quick-search">
          <div class="source-head"><h3>GeM (Government e-Marketplace)</h3></div>
          <p class="muted">GeM blocks automated scraping. Bids matching your registered categories appear directly in your seller dashboard. Use the search portal for manual checks.</p>
          <a class="doc-link" href="https://bidplus.gem.gov.in/all-bids" target="_blank" rel="noopener">Open GeM Bid Search &rarr;</a>
        </section>
        <section class="source-block quick-search">
          <div class="source-head"><h3>CPPP / eProcure</h3></div>
          <p class="muted">Central Public Procurement Portal requires an active session for search. Use the link below to search manually with your keywords.</p>
          <a class="doc-link" href="https://eprocure.gov.in/cppp/latestactivetendersnew/cpppdata" target="_blank" rel="noopener">Open CPPP Tender Search &rarr;</a>
        </section>"""

    keywords_html = ", ".join(esc(k.strip()) for k in data.get("keywords", []))

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tender Radar — Daily BFSI Opportunity Tracker</title>
<style>
  :root {{
    --bg: #0f1720;
    --panel: #16212e;
    --panel-border: #25333f;
    --text: #e7edf3;
    --muted: #8a9bab;
    --accent: #ffb454;
    --accent-dim: #4a3a22;
    --ok: #4caf7d;
    --fail: #e0654f;
    --mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    --sans: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    line-height: 1.5;
  }}
  header {{
    border-bottom: 1px solid var(--panel-border);
    padding: 28px clamp(16px, 4vw, 48px);
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
    align-items: flex-end;
    justify-content: space-between;
  }}
  .brand {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .brand .eyebrow {{
    font-family: var(--mono);
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
  }}
  .brand h1 {{
    margin: 0;
    font-size: clamp(24px, 4vw, 34px);
    font-weight: 700;
    letter-spacing: -0.01em;
  }}
  .meta-strip {{
    font-family: var(--mono);
    font-size: 13px;
    color: var(--muted);
    text-align: right;
  }}
  .stats {{
    display: flex;
    gap: 12px;
    padding: 20px clamp(16px, 4vw, 48px);
    flex-wrap: wrap;
  }}
  .stat {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 14px 20px;
    min-width: 140px;
  }}
  .stat .num {{
    font-family: var(--mono);
    font-size: 28px;
    font-weight: 700;
    color: var(--accent);
  }}
  .stat .label {{
    font-size: 12px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
  }}
  main {{
    padding: 8px clamp(16px, 4vw, 48px) 60px;
    max-width: 1400px;
    margin: 0 auto;
  }}
  .keywords-box {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 24px;
    font-size: 13px;
    color: var(--muted);
  }}
  .keywords-box strong {{ color: var(--text); }}
  .keywords-box .kwlist {{ font-family: var(--mono); color: var(--accent); }}
  h2.section-title {{
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--muted);
    border-bottom: 1px solid var(--panel-border);
    padding-bottom: 10px;
    margin: 36px 0 16px;
  }}
  .source-block {{
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
  }}
  .source-failed {{ border-color: rgba(224,101,79,0.35); }}
  .source-head {{
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 10px;
  }}
  .source-head h3 {{
    margin: 0;
    font-size: 17px;
    font-weight: 600;
  }}
  .badge {{
    font-family: var(--mono);
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 100px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  .badge-ok {{ background: rgba(76,175,125,0.15); color: var(--ok); border: 1px solid rgba(76,175,125,0.35); }}
  .badge-empty {{ background: rgba(138,155,171,0.1); color: var(--muted); border: 1px solid var(--panel-border); }}
  .badge-fail {{ background: rgba(224,101,79,0.15); color: var(--fail); border: 1px solid rgba(224,101,79,0.35); }}
  .source-link {{
    margin-left: auto;
    font-size: 12px;
    color: var(--muted);
    text-decoration: none;
    font-family: var(--mono);
  }}
  .source-link:hover {{ color: var(--accent); }}
  .muted {{ color: var(--muted); font-size: 13px; }}
  .muted a {{ color: var(--muted); }}
  table.tender-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }}
  .tender-table thead th {{
    text-align: left;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-weight: 600;
    padding: 8px 10px;
    border-bottom: 1px solid var(--panel-border);
  }}
  .tender-table td {{
    padding: 12px 10px;
    border-bottom: 1px solid var(--panel-border);
    vertical-align: top;
  }}
  .tender-table tr:last-child td {{ border-bottom: none; }}
  .col-title {{ width: 50%; }}
  .col-meta {{ width: 15%; font-family: var(--mono); font-size: 12px; color: var(--muted); white-space: nowrap; }}
  .col-docs {{ width: 20%; }}
  .title-text {{ font-weight: 500; margin-bottom: 6px; }}
  .services-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px; }}
  .tag {{
    font-family: var(--mono);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    background: var(--accent-dim);
    color: var(--accent);
    padding: 2px 8px;
    border-radius: 4px;
  }}
  .tag-muted {{ background: rgba(138,155,171,0.1); color: var(--muted); }}
  .kw-row {{ font-family: var(--mono); font-size: 11px; color: var(--muted); }}
  .doc-link {{
    display: block;
    font-size: 12px;
    color: var(--accent);
    text-decoration: none;
    margin-bottom: 4px;
    word-break: break-word;
  }}
  .doc-link:hover {{ text-decoration: underline; }}
  .quick-search a.doc-link {{ font-size: 13px; margin-top: 6px; }}
  footer {{
    padding: 24px clamp(16px, 4vw, 48px) 48px;
    color: var(--muted);
    font-size: 12px;
    font-family: var(--mono);
    border-top: 1px solid var(--panel-border);
  }}
  @media (max-width: 720px) {{
    .tender-table thead {{ display: none; }}
    .tender-table tr {{ display: block; padding: 10px 0; border-bottom: 1px solid var(--panel-border); }}
    .tender-table td {{ display: block; border: none; padding: 4px 0; width: 100% !important; }}
    .col-meta::before {{ content: attr(data-label) ': '; color: var(--muted); }}
  }}
</style>
</head>
<body>
<header>
  <div class="brand">
    <span class="eyebrow">Tender Radar</span>
    <h1>Daily BFSI Opportunity Tracker</h1>
  </div>
  <div class="meta-strip">
    Last run: {esc(generated_display)}<br>
    Sources checked: {sources_ok} ok / {sources_failed} failed
  </div>
</header>

<div class="stats">
  <div class="stat"><div class="num">{total_matches}</div><div class="label">Matching tenders</div></div>
  <div class="stat"><div class="num">{sources_ok}</div><div class="label">Sources reachable</div></div>
  <div class="stat"><div class="num">{len(services)}</div><div class="label">Service lines tracked</div></div>
</div>

<main>
  <div class="keywords-box">
    <strong>Keyword filters:</strong> <span class="kwlist">{keywords_html}</span><br>
    Edit <code>config.py</code> to add/remove keywords or sources, then re-run the scraper.
  </div>

  <h2 class="section-title">Bank &amp; Institution Tender Pages (auto-scanned)</h2>
  {sources_html}

  <h2 class="section-title">Government e-Procurement (manual search required)</h2>
  {quick_search_html}
</main>

<footer>
  Generated by Tender Radar &mdash; static dashboard, no server required.
  Run <code>python scrapers/run.py</code> to refresh, or schedule via GitHub Actions.
</footer>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
