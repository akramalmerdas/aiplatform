// static/chat.js — robust client for /api/message

const chatWindow = document.getElementById('chat-window');
const input = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const resultsBtn = document.getElementById('results-btn') || null;

function bubble(text, who = 'bot') {
  if (!chatWindow) return;
  const div = document.createElement('div');
  div.className = `msg ${who}`;
  div.innerText = text || '';
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function typing(on = true) {
  if (!chatWindow) return;
  let t = document.getElementById('typing');
  if (on) {
    if (!t) {
      t = document.createElement('div');
      t.id = 'typing';
      t.className = 'msg bot typing';
      t.innerText = 'Assistant is typing…';
      chatWindow.appendChild(t);
    }
  } else if (t) {
    t.remove();
  }
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function toast(text, type = 'error') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = text;
  document.body.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    setTimeout(() => t.remove(), 500);
  }, 3000);
}

async function sendToServer(message) {
  typing(true);
  sendBtn.disabled = true;
  input.disabled = true;

  try {
    const res = await fetch('/api/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    typing(false);
    let data = null;
    const raw = await res.text();
    try {
      data = JSON.parse(raw);
    } catch {
      data = { error: 'Non-JSON response from server', raw };
    }

    if (!res.ok) {
      toast(data.error || `Server error: ${res.status}`);
      console.error('HTTP error', res.status, data);
      // Re-enable input on error
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
      return;
    }

    const botText = data.bot || data.reply || '';
    if (!botText.trim()) {
      bubble('(No response text returned. Please try again.)', 'bot');
    } else {
      bubble(botText, 'bot');
    }

    if (data.done && data.results_url && resultsBtn) {
      resultsBtn.classList.remove('d-none');
      resultsBtn.href = data.results_url;
      // Keep input disabled
    } else {
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  } catch (e) {
    typing(false);
    console.error('Network/JS error:', e);
    toast('Network error. Check console for details.');
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

let sending = false;
async function doSend() {
  if (sending || input.disabled) return;
  sending = true;

  const msg = (input?.value || '').trim();
  if (input) input.value = '';

  if (msg) {
      bubble(msg, 'user');
  }

  await sendToServer(msg);
  sending = false;
}

if (sendBtn) sendBtn.addEventListener('click', (e) => { e.preventDefault(); doSend(); });
if (input) {
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); doSend(); }
  });
}

// Auto-start interview
window.addEventListener('DOMContentLoaded', () => {
  bubble('(Starting interview…)', 'user');
  sendToServer('');
  if (input) input.focus();
});
