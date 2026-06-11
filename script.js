document.addEventListener('DOMContentLoaded', () => {
  fetchData();
});

async function fetchData() {
  try {
    // Add cache busting
    const res = await fetch(`data/tenders.json?t=${new Date().getTime()}`);
    if (!res.ok) throw new Error('Failed to load data');
    const data = await res.json();
    renderDashboard(data);
  } catch (err) {
    document.getElementById('sources-container').innerHTML = `
      <div class="glass-panel" style="padding: 2rem; text-align: center; color: var(--error);">
        Failed to load data. Please make sure the scraper has run and generated data/tenders.json.
      </div>
    `;
    console.error(err);
  }
}

function renderDashboard(data) {
  // Render Date
  const dateObj = new Date(data.generated_at);
  const dateStr = isNaN(dateObj) ? data.generated_at : dateObj.toLocaleString('en-US', {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short'
  });
  document.getElementById('last-updated').textContent = dateStr;

  // Render Keywords
  const keywordsContainer = document.getElementById('keywords-list');
  keywordsContainer.innerHTML = '';
  (data.keywords || []).forEach(kw => {
    const span = document.createElement('span');
    span.className = 'keyword-tag';
    span.textContent = kw;
    keywordsContainer.appendChild(span);
  });

  // Calculate Stats
  const results = data.results || [];
  let totalMatches = 0;
  let sourcesOk = 0;
  let sourcesFailed = 0;

  results.forEach(r => {
    if (r.status === 'ok') {
      sourcesOk++;
      totalMatches += (r.tenders || []).length;
    } else if (r.status !== 'not_yet_run') {
      sourcesFailed++;
    }
  });

  // Render Stats
  document.getElementById('stats-grid').innerHTML = `
    <div class="glass-panel stat-card">
      <div class="stat-value">${totalMatches}</div>
      <div class="stat-label">Matching Tenders</div>
    </div>
    <div class="glass-panel stat-card">
      <div class="stat-value">${sourcesOk}</div>
      <div class="stat-label">Sources Reachable</div>
    </div>
    <div class="glass-panel stat-card">
      <div class="stat-value">${(data.services || []).length}</div>
      <div class="stat-label">Service Lines Tracked</div>
    </div>
  `;

  // Render Sources
  const sourcesContainer = document.getElementById('sources-container');
  sourcesContainer.innerHTML = '';

  results.forEach(r => {
    const section = document.createElement('section');
    section.className = `glass-panel source-card ${r.tenders && r.tenders.length > 0 ? 'has-data' : ''}`;

    let badgeClass = 'badge-neutral';
    let badgeText = 'Unknown';
    let contentHtml = '';

    if (r.status === 'not_yet_run') {
      badgeText = 'Not yet run';
      contentHtml = `<div style="padding: 1.5rem; color: var(--text-muted);">Run the scraper to fetch this source.</div>`;
    } else if (r.status !== 'ok') {
      badgeClass = 'badge-error';
      badgeText = 'Fetch Failed';
      contentHtml = `<div style="padding: 1.5rem; color: var(--text-muted);">Could not reach source. Site may have changed or blocked access.</div>`;
    } else if (!r.tenders || r.tenders.length === 0) {
      badgeClass = 'badge-neutral';
      badgeText = '0 Matches';
      contentHtml = `<div style="padding: 1.5rem; color: var(--text-muted);">Scanned ${r.total_items_scanned || 0} items — none matched your keywords today.</div>`;
    } else {
      badgeClass = 'badge-success';
      badgeText = `${r.tenders.length} Match${r.tenders.length !== 1 ? 'es' : ''}`;
      
      let tendersHtml = '<div class="tenders-list">';
      r.tenders.forEach(t => {
        const kws = (t.matched_keywords || []).join(', ');
        const services = (t.relevant_services || []).length 
          ? (t.relevant_services || []).map(s => `<span class="service-tag">${escapeHtml(s)}</span>`).join('')
          : '<span class="service-tag" style="opacity:0.5">Unclassified</span>';
        
        const docs = (t.links || []).length
          ? (t.links || []).map(l => `<a href="${escapeHtml(l.url)}" target="_blank" class="doc-link">📄 ${escapeHtml(l.label)}</a>`).join('')
          : '<span style="color: var(--text-muted); font-size: 0.85rem;">No documents</span>';

        tendersHtml += `
          <div class="tender-item">
            <div class="tender-main">
              <h4>${escapeHtml(t.title)}</h4>
              <div class="tags-row">${services}</div>
              <div class="match-info">Matched: ${escapeHtml(kws)}</div>
            </div>
            <div class="tender-meta">
              <div class="meta-item">📅 ${escapeHtml(t.date || '---')}</div>
              <div class="meta-item">📍 ${escapeHtml(t.location || '---')}</div>
            </div>
            <div class="tender-docs">
              ${docs}
            </div>
          </div>
        `;
      });
      tendersHtml += '</div>';
      contentHtml = tendersHtml;
    }

    section.innerHTML = `
      <div class="source-header">
        <div class="source-title-group">
          <h3>${escapeHtml(r.source)}</h3>
          <span class="badge ${badgeClass}">${badgeText}</span>
        </div>
        <a href="${escapeHtml(r.url)}" target="_blank" class="source-link">View Source ↗</a>
      </div>
      ${contentHtml}
    `;

    sourcesContainer.appendChild(section);
  });
}

function escapeHtml(unsafe) {
  if (!unsafe) return '';
  return (unsafe + '')
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
}
