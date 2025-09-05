async function fetchJSON(url, opts = {}) {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opts });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}
function fieldRow(q) {
  return `
    <div class="row">
      <label for="${q.key}">${q.label}</label>
      <textarea id="${q.key}" data-key="${q.key}" rows="2" placeholder="${q.label}"></textarea>
    </div>`;
}
async function loadQA() {
  const { questions } = await fetchJSON("/api/questions");
  const saved = await fetchJSON("/api/answers");
  const qa = document.getElementById("qa");
  qa.innerHTML = questions.map(fieldRow).join("");
  for (const [k,v] of Object.entries(saved||{})) {
    const el = document.getElementById(k);
    if (el) el.value = v;
  }
}
async function saveAnswers() {
  const textareas = document.querySelectorAll("#qa textarea");
  const answers = {}; textareas.forEach(t => answers[t.dataset.key] = t.value);
  await fetchJSON("/api/save-answers", { method:"POST", body: JSON.stringify({answers}) });
  console.log("Saved.");
}
async function generate(path="/api/generate") {
  const body = JSON.stringify({
    language: document.getElementById("language").value,
    format: document.getElementById("format").value,
    referee: document.getElementById("referee").checked
  });
  document.getElementById("output").textContent = "Working...";
  const method = path.includes("regenerate") ? "GET" : "POST";
  const data = await fetchJSON(path, method === "POST" ? { method, body } : {});
  document.getElementById("output").textContent = data.plan || "";
}
document.getElementById("save").addEventListener("click", saveAnswers);
document.getElementById("generate").addEventListener("click", ()=>generate("/api/generate"));
document.getElementById("regenerate").addEventListener("click", ()=>generate("/api/regenerate"));
loadQA().catch(console.error);
