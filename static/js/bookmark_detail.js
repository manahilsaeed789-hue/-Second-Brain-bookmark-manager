document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('bookmarkDetail');
    try {
        const bm = await api(`/api/bookmarks/${BOOKMARK_ID}`);

        const insights = (bm.key_insights || []).map(i => `<li>${escapeHtml(i)}</li>`).join('');
        const takeaways = (bm.actionable_takeaways || []).map(t => `<li>${escapeHtml(t)}</li>`).join('');
        const similar = (bm.similar_bookmarks || []).map(s => renderBookmarkItem(s)).join('');

        container.innerHTML = `
            <div class="detail-header">
                <h1>${escapeHtml(bm.title)}</h1>
                <div class="detail-meta">
                    <span>${bm.source_type.toUpperCase()}</span>
                    <span>${bm.reading_time_minutes} min read</span>
                    <span>${bm.word_count} words</span>
                    <span>${formatDate(bm.created_at)}</span>
                </div>
                <div style="margin-top:0.75rem">${renderTags(bm.tags)}</div>
            </div>

            <div class="detail-section">
                <h2>Summary</h2>
                <p>${escapeHtml(bm.short_summary || 'No summary available')}</p>
            </div>

            ${bm.detailed_summary ? `
            <div class="detail-section">
                <h2>Detailed Summary</h2>
                <p>${escapeHtml(bm.detailed_summary)}</p>
            </div>` : ''}

            ${insights ? `
            <div class="detail-section">
                <h2>Key Insights</h2>
                <ul class="insight-list">${insights}</ul>
            </div>` : ''}

            ${takeaways ? `
            <div class="detail-section">
                <h2>Actionable Takeaways</h2>
                <ul class="insight-list">${takeaways}</ul>
            </div>` : ''}

            <div class="detail-actions">
                ${bm.source_url ? `<a href="${escapeHtml(bm.source_url)}" target="_blank" class="btn btn-primary">Open Original</a>` : ''}
                <button class="btn btn-secondary" id="favBtn">${bm.is_favorite ? '★ Favorited' : '☆ Favorite'}</button>
                <button class="btn btn-danger" id="deleteBtn">Delete</button>
            </div>

            ${similar ? `
            <div class="detail-section" style="margin-top:2rem">
                <h2>Similar Content</h2>
                <div class="bookmark-list">${similar}</div>
            </div>` : ''}
        `;

        document.getElementById('favBtn')?.addEventListener('click', async () => {
            const res = await api(`/api/bookmarks/${BOOKMARK_ID}/favorite`, { method: 'PUT' });
            document.getElementById('favBtn').textContent = res.is_favorite ? '★ Favorited' : '☆ Favorite';
        });

        document.getElementById('deleteBtn')?.addEventListener('click', async () => {
            if (confirm('Delete this bookmark permanently?')) {
                await api(`/api/bookmarks/${BOOKMARK_ID}`, { method: 'DELETE' });
                window.location.href = '/bookmarks';
            }
        });
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><h3>Error loading bookmark</h3><p>${escapeHtml(err.message)}</p></div>`;
    }
});
