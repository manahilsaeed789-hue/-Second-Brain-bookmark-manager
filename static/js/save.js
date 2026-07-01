document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`panel-${btn.dataset.tab}`).classList.add('active');
        });
    });

    const statusEl = document.getElementById('saveStatus');
    function showStatus(msg, type) {
        statusEl.textContent = msg;
        statusEl.className = `save-status ${type}`;
        statusEl.classList.remove('hidden');
    }

    // URL form
    document.getElementById('urlForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        showStatus('Saving and analyzing content with AI...', 'loading');
        try {
            const bm = await api('/api/bookmarks/url', {
                method: 'POST',
                body: JSON.stringify({
                    url: document.getElementById('urlInput').value,
                    notes: document.getElementById('urlNotes').value || null,
                }),
            });
            showStatus(`Saved: "${bm.title}" — Redirecting...`, 'success');
            setTimeout(() => window.location.href = `/bookmarks/${bm.id}`, 1500);
        } catch (err) {
            showStatus(err.message, 'error');
        }
    });

    // Note form
    document.getElementById('noteForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        showStatus('Saving and analyzing note...', 'loading');
        try {
            const bm = await api('/api/bookmarks/note', {
                method: 'POST',
                body: JSON.stringify({
                    title: document.getElementById('noteTitle').value,
                    content: document.getElementById('noteContent').value,
                }),
            });
            showStatus(`Saved: "${bm.title}" — Redirecting...`, 'success');
            setTimeout(() => window.location.href = `/bookmarks/${bm.id}`, 1500);
        } catch (err) {
            showStatus(err.message, 'error');
        }
    });

    // Paste form
    document.getElementById('pasteForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        showStatus('Saving and analyzing content...', 'loading');
        try {
            const bm = await api('/api/bookmarks/paste', {
                method: 'POST',
                body: JSON.stringify({
                    title: document.getElementById('pasteTitle').value || null,
                    content: document.getElementById('pasteContent').value,
                }),
            });
            showStatus(`Saved: "${bm.title}" — Redirecting...`, 'success');
            setTimeout(() => window.location.href = `/bookmarks/${bm.id}`, 1500);
        } catch (err) {
            showStatus(err.message, 'error');
        }
    });

    // File upload
    const fileDrop = document.getElementById('fileDrop');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');

    fileDrop.addEventListener('click', () => fileInput.click());
    fileDrop.addEventListener('dragover', (e) => { e.preventDefault(); fileDrop.classList.add('dragover'); });
    fileDrop.addEventListener('dragleave', () => fileDrop.classList.remove('dragover'));
    fileDrop.addEventListener('drop', (e) => {
        e.preventDefault();
        fileDrop.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect();
        }
    });
    fileInput.addEventListener('change', handleFileSelect);

    function handleFileSelect() {
        const file = fileInput.files[0];
        if (file) {
            document.getElementById('fileName').textContent = file.name;
            uploadBtn.disabled = false;
        }
    }

    document.getElementById('uploadForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const file = fileInput.files[0];
        if (!file) return;

        showStatus('Uploading and processing file...', 'loading');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/bookmarks/upload', { method: 'POST', body: formData });
            if (res.status === 401) { window.location.href = '/login'; return; }
            const bm = await res.json();
            if (!res.ok) throw new Error(bm.detail || 'Upload failed');
            showStatus(`Saved: "${bm.title}" — Redirecting...`, 'success');
            setTimeout(() => window.location.href = `/bookmarks/${bm.id}`, 1500);
        } catch (err) {
            showStatus(err.message, 'error');
        }
    });
});
