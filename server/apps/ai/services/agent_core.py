# src/agent_core.py
import os
from typing import Any, Dict, Tuple
from openai import OpenAI
from apps.ai.config.templates_config import TEMPLATES

TEMPERATURE = float(os.getenv("MODEL_TEMP", "0.15"))
TOP_P       = float(os.getenv("MODEL_TOP_P", "0.9"))
MODEL       = os.getenv("OPENAI_MODEL", os.getenv("PAID_MODEL", "gpt-4o-mini"))

SYSTEM_HINT = """You are a senior software & AI product consultant specialized in Spain.
Produce full professional business plans in Markdown that STRICTLY follow a given section outline.
- Spain focus: market sizing in EUR, competitors operating in Spain, Spanish/EU regulations.
- Use provided research and cite sources inline with short links.
- Be concise but complete; avoid fluff; use bullet points and tables where suitable.
- If data is missing, infer conservative defaults and label them as assumptions.
"""

def _mk_outline_markdown(template_id: str) -> str:
    tpl = TEMPLATES[template_id]
    lines = []
    for s in tpl["sections"]:
        lines.append(f"# {s}")
        for sub in tpl.get("subsections", {}).get(s, []):
            lines.append(f"## {sub}")
    return "\n".join(lines)

def _mk_guidance(template_id: str) -> str:
    name = TEMPLATES[template_id]["display_name"]
    return f"""Follow this exact section outline from **{name}**.
- Fill every section with Spain-specific content.
- Use bullets where helpful.
- Insert compact tables for pricing, GTM calendar, and 12-month P&L.
- Include 3–6 named competitors operating in Spain, each with one-line notes.
- Cite at least 2 sources for market sizing (short inline links).
"""

def _mk_inputs_block(answers: Dict[str, Any]) -> str:
    if not answers: return "(no structured answers provided)"
    out = []
    for k,v in answers.items():
        if isinstance(v,str) and v.strip():
            out.append(f"- **{k}**: {v.strip()}")
    return "\n".join(out)

def _mk_research_block(research: Dict[str, Any]) -> str:
    if not research: return "(no research pack)"
    srcs = research.get("sources", []) or []
    facts = research.get("facts", []) or []
    comps = research.get("competitors", []) or []
    parts = []
    if comps:
        parts.append("**Competitors (Spain):** " + ", ".join(comps[:8]))
    if facts:
        parts.append("**Facts:** " + " | ".join(f"{f['fact']} (src: {f['source']})" for f in facts[:8]))
    if srcs:
        parts.append("**Sources:** " + " | ".join(f"{s['title']} ({s['url']})" for s in srcs[:8]))
    return "\n".join(parts)

def _client() -> OpenAI:
    return OpenAI()

def _call_model_markdown(prompt: str) -> str:
    client = _client()
    resp = client.chat.completions.create(
        model=MODEL, temperature=TEMPERATURE, top_p=TOP_P,
        messages=[{"role":"system","content": SYSTEM_HINT},
                  {"role":"user","content": prompt}]
    )
    return resp.choices[0].message.content.strip()

def generate_markdown_plan(
    answers: Dict[str, Any],
    research: Dict[str, Any],
    template_id: str = "template_a_ministry",
    language: str = "English"
) -> Tuple[str, str]:
    outline = _mk_outline_markdown(template_id)
    guidance = _mk_guidance(template_id)
    inputs = _mk_inputs_block(answers)
    research_block = _mk_research_block(research)

    prompt = f"""
Respond in {language}. Write a full professional **business plan for Spain**.

{guidance}

Use the following OUTLINE exactly (do not change section titles):

---
{outline}
---

**User Inputs (raw):**
{inputs}

**Automated Research (Spain):**
{research_block}

**Requirements:**
- Use EUR figures; include TAM/SAM/SOM with 2+ sources.
- Provide 12-month P&L table (Revenue, COGS, Gross Margin, Opex, EBITDA).
- GTM: at least 4 channels relevant in Spain; include monthly launch calendar for first year.
- Regulations: note Spain/EU compliance relevant to the industry (e.g., GDPR, sector licenses).
- Keep all claims realistic and internally consistent.
- Use Markdown headings (#, ##) matching the outline EXACTLY.
- Markdown ONLY (no JSON).

Now produce the full plan in Markdown following the outline:
""".strip()

    md = _call_model_markdown(prompt)

    preview = []
    preview.append(f"Template: {TEMPLATES[template_id]['display_name']}")
    preview.append("Includes: Spain competitors, EUR sizing, GTM, 12-month P&L, regulations.")
    return md, "\n".join(preview)

# ---- Optional compatibility shim (if old code calls generate_plans) ----
from apps.ai.services.research import research_market
def generate_plans(answers, language="English", out_format="Markdown", referee=True, research=None, template_id="template_a_ministry"):
    if research is None:
        research = research_market(answers)
    md, preview = generate_markdown_plan(answers, research, template_id=template_id, language=language)
    return md, preview
