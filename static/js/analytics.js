document.addEventListener('DOMContentLoaded', async () => {
    try {
        const data = await api('/api/analytics');
        const container = document.getElementById('analyticsContent');

        const searches = data.most_searched_topics.map(s =>
            `<li><span>${escapeHtml(s.query)}</span><span>${s.count}x</span></li>`
        ).join('') || '<li><span>No searches yet</span></li>';

        const insights = data.weekly_insights.map(i =>
            `<div class="insight-box">${escapeHtml(i)}</div>`
        ).join('');

        const tagDist = data.tags_distribution.map(t =>
            `<li><span>${escapeHtml(t.type)}</span><span>${t.count}</span></li>`
        ).join('') || '<li><span>No tags yet</span></li>';

        container.innerHTML = `
            <div class="analytics-card">
                <h3>Most Searched Topics</h3>
                <ul class="analytics-list">${searches}</ul>
            </div>
            <div class="analytics-card">
                <h3>Overview</h3>
                <ul class="analytics-list">
                    <li><span>Most Saved Category</span><span>${escapeHtml(data.most_saved_category || 'N/A')}</span></li>
                    <li><span>Time Spent Reading</span><span>${data.total_time_spent_hours}h</span></li>
                </ul>
            </div>
            <div class="analytics-card">
                <h3>Weekly Insights</h3>
                ${insights || '<p class="card-desc">Insights will appear as you use the app</p>'}
            </div>
            <div class="analytics-card">
                <h3>Tag Distribution</h3>
                <ul class="analytics-list">${tagDist}</ul>
            </div>
        `;
    } catch (err) {
        console.error('Analytics load error:', err);
    }
});
