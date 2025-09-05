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

async function sendToServer(message) {
  typing(true);
  try {
    const res = await fetch('/api/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    // Try to parse JSON; if parsing fails, show raw text.
    let data = null;
    const raw = await res.text();
    try { data = JSON.parse(raw); } catch { data = { error: 'Non-JSON response', raw }; }

    typing(false);

    if (!res.ok) {
      bubble(data.error || `Server error ${res.status}`, 'bot');
      console.error('HTTP error', res.status, data);
      return;
    }

    // Accept either {bot: "..."} or {reply: "..."}
    const botText = (data && (data.bot ?? data.reply)) || '';
    console.log('server payload:', data);
    console.log('botText:', botText);

    if (!botText.trim()) {
      // Fallback so the UI always shows something
      bubble('(No response text returned. Please try again.)', 'bot');
      return;
    }

    bubble(botText, 'bot');

    if (data.done && data.results_url && resultsBtn) {
      resultsBtn.classList.remove('d-none');
      resultsBtn.href = data.results_url;
      input.disabled = true;
      sendBtn.disabled = true;
    }
  } catch (e) {
    typing(false);
    console.error('Network/JS error:', e);
    bubble('Network error. Check the console for details.', 'bot');
  }
}

let sending = false;
async function doSend() {
  if (sending) return;
  sending = true;

  const msg = (input?.value || '').trim();
  if (input) input.value = '';

  // Show user bubble (even for empty kickoff)
  if (msg === '') bubble('(starting)…', 'user');
  else bubble(msg, 'user');

  await sendToServer(msg);
  sending = false;
}

if (sendBtn) sendBtn.addEventListener('click', (e) => { e.preventDefault(); doSend(); });
if (input) {
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); doSend(); }
  });
}

// Auto-start interview: first question without typing anything
window.addEventListener('DOMContentLoaded', () => {
  // Kick off with an empty message — server will return the first question
  sendToServer('');
  if (input) input.focus();
});
console.info("[core/chat.js] loaded");
document.addEventListener('DOMContentLoaded', () => {
  console.info("[core/chat.js] DOM ready");
});