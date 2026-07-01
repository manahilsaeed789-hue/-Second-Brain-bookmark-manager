document.addEventListener('DOMContentLoaded', async () => {
    try {
        const collections = await api('/api/collections');
        const grid = document.getElementById('collectionsGrid');

        if (collections.length === 0) {
            grid.innerHTML = '<div class="empty-state"><h3>No collections yet</h3><p>Collections are auto-created when you save content</p></div>';
            return;
        }

        grid.innerHTML = collections.map(c => `
            <div class="collection-card">
                <div class="collection-header">
                    <div class="collection-dot" style="background:${c.color}"></div>
                    <h3>${escapeHtml(c.name)}</h3>
                </div>
                <p>${escapeHtml(c.description || '')}</p>
                <div class="collection-count">${c.bookmark_count} bookmark${c.bookmark_count !== 1 ? 's' : ''}</div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Collections load error:', err);
    }
});
