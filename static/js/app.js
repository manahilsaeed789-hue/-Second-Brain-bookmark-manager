/** Second Brain — Core Application JS */

// Theme management
(function initTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
})();

document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
        });
    }

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await fetch('/api/auth/logout', { method: 'POST' });
            window.location.href = '/login';
        });
    }
});

// Utility functions
async function api(url, options = {}) {
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    });
    if (res.status === 401) {
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Request failed');
    return data;
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function renderTags(tags) {
    if (!tags || !tags.length) return '';
    return tags.map(t => `<span class="tag">${escapeHtml(t.name || t)}</span>`).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderBookmarkItem(bm) {
    return `
        <div class="bookmark-item" onclick="window.location.href='/bookmarks/${bm.id}'">
            <div class="bookmark-item-info">
                <div class="bookmark-item-title">${escapeHtml(bm.title)}</div>
                <div class="bookmark-item-meta">${bm.reading_time_minutes} min read · ${formatDate(bm.created_at)}</div>
            </div>
        </div>`;
}

function renderBookmarkCard(bm) {
    return `
        <div class="bookmark-card" onclick="window.location.href='/bookmarks/${bm.id}'">
            <h3>${escapeHtml(bm.title)}</h3>
            <p>${escapeHtml(bm.short_summary || 'No summary available')}</p>
            <div style="margin-top:0.75rem">${renderTags(bm.tags)}</div>
            <div class="bookmark-card-footer">
                <span class="bookmark-card-meta">${bm.source_type} · ${bm.reading_time_minutes} min</span>
                <span class="bookmark-card-meta">${formatDate(bm.created_at)}</span>
            </div>
        </div>`;
}
