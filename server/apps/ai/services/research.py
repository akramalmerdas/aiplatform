import os
import re
import time
from typing import Any, Dict, List

import requests

# -------- Tunables --------
MIN_RESULTS_PER_PHASE = 6  # if fewer, widen to next phase
MAX_RESULTS_PER_QUERY = 8  # per Tavily call
RECENCY_DAYS = 365  # bias to the last year

# Priority/quality domains
PHASE1_AUTHORITIES = [
    "boe.es",
    "aeat.es",
    "aepd.es",
    "ine.es",
    "cnmc.es",
    "eur-lex.europa.eu",
    "europa.eu",
]
PHASE2_INSTITUTIONS = [
    "camara.es",
    "datos.gob.es",
    "lamoncloa.gob.es",
    "industria.gob.es",
    "mineco.gob.es",
    "seg-social.es",
    "seguridad-social.es",
]
PHASE3_INDUSTRY_MEDIA = [
    # Business media (.es)
    "expansion.com",
    "cincodias.elpais.com",
    "eleconomista.es",
    # International quality/statistics
    "oecd.org",
    "worldbank.org",
    "imf.org",
    "ec.europa.eu",
]
EXCLUDE_DOMAINS = [
    "pinterest.com",
    "quora.com",
    "reddit.com",
    "youtube.com",
    "tiktok.com",
    "linkedin.com/pulse",
    "facebook.com",
    "instagram.com",
    "medium.com",
]

SEED_SYNONYMS = {
    "fintech": ["pagos", "banca abierta", "PSD2", "AML", "KYC"],
    "health": ["sanidad", "salud digital", "marcado CE", "dispositivo sanitario"],
    "edtech": ["formación", "plataformas educativas", "LMS"],
    "energy": ["energía", "autoconsumo", "fotovoltaica", "CNMC"],
    "consulting": [
        "asesoría",
        "trámites",
        "constitución",
        "licencia",
        "site:boe.es",
        "site:aeat.es",
        "site:aepd.es",
        "site:camara.es",
    ],
    "startup": [
        "constitución de empresa",
        "sociedad limitada",
        "autónomos",
        "site:boe.es",
        "site:camara.es",
    ],
}


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()


def _uniq(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in seq:
        k = (x or "").strip().lower()
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out


def _mk_queries(answers: Dict[str, Any]) -> List[str]:
    # Industry/idea in ES-friendly form
    industry = _norm(answers.get("industry") or answers.get("idea_summary") or "")
    base = _norm(
        " ".join([industry, answers.get("solution", ""), answers.get("problem", "")])
    )
    es_terms = []
    for key, terms in SEED_SYNONYMS.items():
        if key in industry.lower():
            es_terms = terms
            break

    return _uniq(
        [
            f"{industry} Spain competitors site:.es",
            f"{industry} Spain market size EUR TAM SAM SOM",
            f"{base} tendencias España regulaciones {' '.join(es_terms)}",
            f"{industry} Spain regulations licencia cumplimiento {' '.join(es_terms)}",
            f"{industry} Spain distribution channels B2B B2C",
            f"{industry} Spain startups funding inversores",
        ]
    )


def _pick_competitors(results: List[Dict[str, str]], maxn=8) -> List[str]:
    names = []
    for r in results or []:
        title = _norm(r.get("title"))
        if not title:
            continue
        title = re.sub(r"\s*[\-|–|:|•]\s*.*$", "", title)
        if 2 <= len(title.split()) <= 6:
            names.append(title)
    return _uniq(names)[:maxn]


def _tavily_search(
    query: str, include_domains: List[str] = None
) -> List[Dict[str, str]]:
    tavily = os.getenv("TAVILY_API_KEY")
    if not tavily:
        return []

    payload = {
        "query": query,
        "search_depth": "advanced",
        "max_results": MAX_RESULTS_PER_QUERY,
        "include_answer": True,
        "include_raw_content": True,
        "include_images": False,
        "topic": "general",
        "days": RECENCY_DAYS,
        "exclude_domains": EXCLUDE_DOMAINS,
    }
    if include_domains:
        payload["include_domains"] = include_domains

    r = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {tavily}"},
        json=payload,
        timeout=35,
    )
    r.raise_for_status()
    data = r.json()
    out = []
    for it in data.get("results", []):
        out.append(
            {
                "title": it.get("title", ""),
                "url": it.get("url", ""),
                "content": it.get("raw_content") or it.get("content") or "",
            }
        )
    # Push the synthesized answer as a pseudo-result (helps grounding)
    ans = _norm(data.get("answer", ""))
    if ans:
        out.insert(0, {"title": "Tavily synthesis", "url": "", "content": ans})
    return out


def _serper_search(query: str) -> List[Dict[str, str]]:
    serper = os.getenv("SERPER_API_KEY") or os.getenv("SERPAPI_API_KEY")
    if not serper:
        return []
    r = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": serper, "Content-Type": "application/json"},
        json={"q": query, "num": 8},
        timeout=25,
    )
    r.raise_for_status()
    data = r.json()
    out = []
    for it in data.get("organic", []):
        out.append(
            {
                "title": it.get("title", ""),
                "url": it.get("link", ""),
                "content": it.get("snippet", ""),
            }
        )
    return out


def _wikipedia_search(query: str) -> List[Dict[str, str]]:
    r = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "opensearch",
            "search": query,
            "limit": 5,
            "namespace": 0,
            "format": "json",
        },
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    out = []
    for t, u in zip(data[1], data[3]):
        out.append({"title": t, "url": u, "content": ""})
    return out


def research_market(answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Spain-focused research pack with tiered widening:
    1) Authorities -> 2) Institutions -> 3) Industry & media -> 4) Broad search
    Falls back to Serper/Wikipedia when Tavily is missing.
    """
    queries = _mk_queries(answers)
    all_results: List[Dict[str, str]] = []

    have_tavily = bool(os.getenv("TAVILY_API_KEY"))
    phases = [
        ("authorities", PHASE1_AUTHORITIES),
        ("institutions", PHASE2_INSTITUTIONS),
        ("industry_media", PHASE3_INDUSTRY_MEDIA),
        ("broad", None),  # remove include_domains
    ]

    for q in queries:
        phase_hits = []
        if have_tavily:
            for phase_name, domains in phases:
                try:
                    hits = _tavily_search(q, include_domains=domains)
                except Exception:
                    hits = []
                phase_hits.extend(hits)
                # If we’ve gathered enough for this query, stop widening
                if len(phase_hits) >= MIN_RESULTS_PER_PHASE:
                    break
                time.sleep(0.3)
        else:
            # No Tavily: Serper or Wikipedia
            try:
                phase_hits = _serper_search(q)
            except Exception:
                try:
                    phase_hits = _wikipedia_search(q)
                except Exception:
                    phase_hits = []

        all_results.extend(phase_hits)
        time.sleep(0.3)

    # Post-process & summarise
    sources = []
    facts = []
    seen_urls = set()
    for r in all_results:
        title = _norm(r.get("title"))
        url = (r.get("url") or "").strip()
        if title and url and url not in seen_urls:
            seen_urls.add(url)
            sources.append({"title": title, "url": url})

    # Longer snippets preferred for grounding
    for r in all_results[:20]:
        txt = _norm(r.get("content") or r.get("title"))
        url = r.get("url") or ""
        if txt:
            facts.append({"fact": txt[:450], "source": url})

    competitors = _pick_competitors(all_results)
    summary = "Tiered research (Spain): " + "; ".join(queries[:4])

    return {
        "summary": summary,
        "competitors": competitors,
        "facts": facts[:14],
        "sources": sources[:20],
        "queries": queries,
    }
