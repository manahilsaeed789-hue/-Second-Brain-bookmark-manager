document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('searchInput');
    const resultsEl = document.getElementById('searchResults');

    async function performSearch(query) {
        if (!query.trim()) return;
        resultsEl.innerHTML = '<div class="loading">Searching your knowledge base...</div>';

        try {
            const data = await api('/api/search', {
                method: 'POST',
                body: JSON.stringify({ query, limit: 10 }),
            });

            if (data.results.length === 0) {
                resultsEl.innerHTML = '<div class="empty-state"><h3>No results found</h3><p>Try different keywords or save more content on this topic</p></div>';
                return;
            }

            resultsEl.innerHTML = data.results.map(r => `
                <div class="search-result" onclick="window.location.href='/bookmarks/${r.bookmark.id}'">
                    <div class="search-result-header">
                        <h3>${escapeHtml(r.bookmark.title)}</h3>
                        <span class="similarity-badge">${(r.similarity_score * 100).toFixed(0)}% match</span>
                    </div>
                    <p>${escapeHtml(r.bookmark.short_summary || '')}</p>
                    <div style="margin-top:0.5rem">${renderTags(r.bookmark.tags)}</div>
                </div>
            `).join('');
        } catch (err) {
            resultsEl.innerHTML = `<div class="empty-state"><p>${escapeHtml(err.message)}</p></div>`;
        }
    }

    document.getElementById('searchBtn').addEventListener('click', () => performSearch(input.value));
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') performSearch(input.value); });

    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.q;
            performSearch(chip.dataset.q);
        });
    });
});
