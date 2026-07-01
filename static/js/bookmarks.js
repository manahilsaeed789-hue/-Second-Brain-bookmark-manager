document.addEventListener('DOMContentLoaded', async () => {
    try {
        const bookmarks = await api('/api/bookmarks');
        const list = document.getElementById('bookmarksList');
        const empty = document.getElementById('emptyState');

        if (bookmarks.length === 0) {
            list.classList.add('hidden');
            empty.classList.remove('hidden');
        } else {
            list.innerHTML = bookmarks.map(renderBookmarkCard).join('');
        }
    } catch (err) {
        console.error('Bookmarks load error:', err);
    }
});
