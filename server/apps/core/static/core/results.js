// results.js — build TOC, exports, theme toggle from server-rendered content

const $ = (s) => document.querySelector(s);

const docEl = $('#doc');
const tocEl = $('#toc');
const refsEl = $('#refs-list');
const rawMdEl = $('#raw-md');

function buildTOC() {
  if (!tocEl || !docEl) return;
  tocEl.innerHTML = '';
  const headings = docEl.querySelectorAll('h1, h2, h3');
  let sectionCount = 0;
  headings.forEach((h, i) => {
    if (!h.id) h.id = 'h-' + i;
    const a = document.createElement('a');
    a.href = `#${h.id}`;
    a.innerHTML = h.textContent;
    a.className = `toc-item toc-${h.tagName.toLowerCase()}`;
    tocEl.appendChild(a);
    sectionCount++;
  });
  const sectionCountEl = $('#sectioncount');
  if (sectionCountEl) sectionCountEl.textContent = sectionCount || '–';
}

function extractReferences() {
  if (!refsEl || !docEl) return;
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
  const wordCountEl = $('#wordcount');
  if (wordCountEl) {
      const words = (md.trim().match(/\S+/g) || []).length;
      wordCountEl.textContent = words.toLocaleString();
  }
  const genStampEl = $('#genstamp');
  if(genStampEl) {
      const ts = new Date();
      genStampEl.textContent = ts.toLocaleDateString();
  }
}

function downloadFile(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 500);
}

function toast(text, type = 'success') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = text;
    document.body.appendChild(t);
    setTimeout(() => {
      t.style.opacity = '0';
      setTimeout(() => t.remove(), 500);
    }, 2000);
}


function init() {
  if (!docEl) return;

  const md = rawMdEl ? rawMdEl.textContent.trim() : '';

  buildTOC();
  extractReferences();
  updateMeta(md);

  // Actions
  const copyBtn = $('#copy-md');
  if (copyBtn) {
    copyBtn.onclick = async () => {
      await navigator.clipboard.writeText(md);
      toast('Markdown copied!');
    };
  }

  const downloadMdBtn = $('#download-md');
  if (downloadMdBtn) {
    downloadMdBtn.onclick = () => {
      downloadFile('business_plan.md', md, 'text/markdown;charset=utf-8');
    };
  }

  const downloadDocxBtn = $('#download-docx');
  if (downloadDocxBtn) {
      downloadDocxBtn.onclick = () => {
      if (typeof htmlDocx === 'undefined') {
          toast('Could not create .docx file.', 'error');
          return;
      }
      const wrapper = `<!doctype html><html><head><meta charset="utf-8"></head><body>${docEl.innerHTML}</body></html>`;
      const blob = htmlDocx.asBlob(wrapper);
      downloadFile('business_plan.docx', blob, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    };
  }

  const printBtn = $('#print-pdf');
  if(printBtn) printBtn.onclick = () => window.print();

  // Theme toggle
  const root = document.documentElement;
  const toggle = $('#toggle-theme');
  if (toggle) {
      const setTheme = (mode) => {
        root.classList.remove('light', 'dark');
        root.classList.add(mode);
        localStorage.setItem('theme', mode);
      };
      const saved = localStorage.getItem('theme') || 'dark';
      setTheme(saved);
      toggle.onclick = () => setTheme(root.classList.contains('light') ? 'dark' : 'light');
  }
}

document.addEventListener('DOMContentLoaded', init);
