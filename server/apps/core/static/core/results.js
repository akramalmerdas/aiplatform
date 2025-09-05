// results.js — fetch plan, render Markdown, build TOC, exports, theme toggle

const $ = (s) => document.querySelector(s);

const docEl = $('#doc');
const tocEl = $('#toc');
const refsEl = $('#refs-list');
const loadingEl = $('#loading');
const alertEl = $('#alert');

async function fetchPlan() {
  const res = await fetch('/api/last-plan', { method: 'GET' });
  const data = await res.json().catch(() => ({}));
  return (data && data.plan) || '';
}

function renderMarkdown(md) {
  // Configure marked for safe-ish HTML
  marked.setOptions({
    breaks: true,
    gfm: true
  });
  const html = marked.parse(md);
  docEl.innerHTML = html;
}

function buildTOC() {
  tocEl.innerHTML = '';
  const headings = docEl.querySelectorAll('h1, h2');
  let sectionCount = 0;
  headings.forEach((h, i) => {
    if (!h.id) h.id = 'h-' + i;
    const a = document.createElement('a');
    a.href = `#${h.id}`;
    a.innerHTML = (h.tagName === 'H1')
      ? `${h.textContent}`
      : `<small>${h.textContent}</small>`;
    tocEl.appendChild(a);
    sectionCount++;
  });
  $('#sectioncount').textContent = sectionCount || '–';
}

function extractReferences() {
  refsEl.innerHTML = '';
  const links = Array.from(docEl.querySelectorAll('a[href]'))
    .map(a => a.getAttribute('href'))
    .filter(href => href && /^https?:\/\//i.test(href));

  const dedup = [...new Set(links)];
  dedup.forEach((url) => {
    const li = document.createElement('li');
    li.innerHTML = `<a href="${url}" target="_blank" rel="noopener">${url}</a>`;
    refsEl.appendChild(li);
  });
}

function updateMeta(md) {
  const words = (md.trim().match(/\S+/g) || []).length;
  $('#wordcount').textContent = words.toLocaleString();
  const ts = new Date();
  $('#genstamp').textContent = ts.toLocaleString();
}

async function init() {
  try {
    const md = await fetchPlan();
    if (!md || !md.trim()) {
      alertEl.classList.remove('hidden');
      alertEl.textContent = '(No plan yet. Go to Chat and type RESULTS after answering questions.)';
      loadingEl.classList.add('hidden');
      return;
    }

    renderMarkdown(md);
    buildTOC();
    extractReferences();
    updateMeta(md);

    loadingEl.classList.add('hidden');
    docEl.classList.remove('hidden');

    // Actions
    $('#copy-md').onclick = async () => {
      await navigator.clipboard.writeText(md);
      toast('Markdown copied');
    };
    $('#download-md').onclick = () => {
      downloadFile('business_plan.md', md, 'text/markdown;charset=utf-8');
    };
    $('#download-docx').onclick = () => {
      const wrapper = `
        <!doctype html><html><head>
          <meta charset="utf-8">
          <style>
            body { font-family: Arial, Helvetica, sans-serif; }
            h1,h2,h3 { margin: 8px 0; }
            table { border-collapse: collapse; width: 100%; }
            th,td { border: 1px solid #ddd; padding: 6px; }
          </style>
        </head><body>${docEl.innerHTML}</body></html>`;
      const blob = window.htmlDocx.asBlob(wrapper);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'business_plan.docx'; a.click();
      setTimeout(() => URL.revokeObjectURL(url), 500);
    };
    $('#print-pdf').onclick = () => window.print();

    // Theme toggle
    const root = document.documentElement;
    const toggle = $('#toggle-theme');
    const setTheme = (mode) => {
      if (mode === 'light') root.classList.add('light');
      else root.classList.remove('light');
      localStorage.setItem('theme', mode);
    };
    const saved = localStorage.getItem('theme') || 'dark';
    setTheme(saved);
    toggle.onclick = () => setTheme(root.classList.contains('light') ? 'dark' : 'light');

  } catch (e) {
    console.error(e);
    alertEl.classList.remove('hidden');
    alertEl.textContent = 'Failed to load the plan.';
  }
}

function downloadFile(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 500);
}

function toast(text) {
  const t = document.createElement('div');
  t.textContent = text;
  t.style.position = 'fixed';
  t.style.bottom = '16px';
  t.style.right = '16px';
  t.style.padding = '8px 12px';
  t.style.background = 'rgba(0,0,0,.75)';
  t.style.color = '#fff';
  t.style.borderRadius = '10px';
  t.style.zIndex = '9999';
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 1400);
}

document.addEventListener('DOMContentLoaded', init);
