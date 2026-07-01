document.addEventListener('DOMContentLoaded', async () => {
    try {
        const data = await api('/api/dashboard');

        document.getElementById('totalBookmarks').textContent = data.total_bookmarks;
        document.getElementById('totalCategories').textContent = data.total_categories;
        document.getElementById('readingTime').textContent = data.total_reading_time_minutes;

        const recent = document.getElementById('recentBookmarks');
        recent.innerHTML = data.recent_bookmarks.length
            ? data.recent_bookmarks.map(renderBookmarkItem).join('')
            : '<p class="card-desc">No bookmarks yet. <a href="/save">Save your first one!</a></p>';

        const trending = document.getElementById('trendingTags');
        trending.innerHTML = data.trending_tags.length
            ? data.trending_tags.map(t => `<span class="tag-chip">${escapeHtml(t.name)}<span class="count">${t.count}</span></span>`).join('')
            : '<p class="card-desc">Tags will appear as you save content</p>';

        document.getElementById('rediscovery').innerHTML = data.daily_rediscovery.length
            ? data.daily_rediscovery.map(renderBookmarkItem).join('')
            : '<p class="card-desc">Save more content to discover hidden gems</p>';

        document.getElementById('revisit').innerHTML = data.recommended_revisit.length
            ? data.recommended_revisit.map(renderBookmarkItem).join('')
            : '<p class="card-desc">Your recommended reads will appear here</p>';

        const km = document.getElementById('knowledgeMap');
        km.innerHTML = data.knowledge_map.length
            ? data.knowledge_map.map(n => `
                <div class="knowledge-node">
                    <div class="knowledge-node-name">${escapeHtml(n.tag)}</div>
                    <div class="knowledge-node-count">${n.count} items · ${n.type}</div>
                </div>`).join('')
            : '<p class="card-desc">Your knowledge map will grow with your saves</p>';
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
});
