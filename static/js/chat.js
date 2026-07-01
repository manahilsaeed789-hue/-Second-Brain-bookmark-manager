document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chatForm');
    const input = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');

    function addMessage(role, content, sources) {
        const div = document.createElement('div');
        div.className = `chat-message ${role}`;
        let sourcesHtml = '';
        if (sources && sources.length) {
            sourcesHtml = `<div class="chat-sources">Sources: ${sources.map(s => s.title).join(', ')}</div>`;
        }
        div.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>${sourcesHtml}`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msg = input.value.trim();
        if (!msg) return;

        addMessage('user', msg);
        input.value = '';
        input.disabled = true;

        const loading = document.createElement('div');
        loading.className = 'chat-message assistant';
        loading.innerHTML = '<div class="message-content">Thinking...</div>';
        messages.appendChild(loading);

        try {
            const data = await api('/api/chat', {
                method: 'POST',
                body: JSON.stringify({ message: msg }),
            });
            loading.remove();
            addMessage('assistant', data.answer, data.sources);
        } catch (err) {
            loading.remove();
            addMessage('assistant', `Error: ${err.message}`);
        }

        input.disabled = false;
        input.focus();
    });
});
