// static/js/chat.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chatForm');
  const input = document.getElementById('messageInput');
  const chat = document.getElementById('chat');

  function addMessage(text, who='teddy') {
    const el = document.createElement('div');
    el.className = 'bubble ' + (who === 'user' ? 'user' : 'teddy');
    el.textContent = text;
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
  }

  function addTyping() {
    const el = document.createElement('div');
    el.className = 'bubble teddy typing';
    el.textContent = '...';
    el.id = 'typing-indicator';
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
  }

  function removeTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    addMessage(text, 'user');
    input.value = '';
    addTyping();

    try {
      const resp = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await resp.json();
      removeTyping();
      if (resp.ok && data.reply) {
        addMessage(data.reply, 'teddy');
      } else {
        addMessage('Sorry — Teddy is sleepy. (' + (data.error || resp.statusText) + ')', 'teddy');
      }
    } catch (err) {
      removeTyping();
      addMessage('Network error: ' + err.message, 'teddy');
    }
  });
});
