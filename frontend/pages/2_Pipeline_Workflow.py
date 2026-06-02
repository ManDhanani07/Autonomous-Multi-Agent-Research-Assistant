import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.shared_theme import apply_shared_theme

st.set_page_config(
    page_title="Nexus | Pipeline Workflow",
    page_icon=":material/account_tree:",
    layout="wide"
)

apply_shared_theme()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

@keyframes fadeSlideUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes badgePulse  { 0%,100% { opacity:1; } 50% { opacity:.55; } }
@keyframes glowPulse   { 0%,100% { box-shadow:0 0 6px currentColor; } 50% { box-shadow:0 0 14px currentColor; } }

/* ── Page wrapper ── */
.wf-page { animation: fadeSlideUp .45s ease both; max-width: 860px; margin: 0 auto; }

/* ── Page title ── */
.wf-page-title {
    font-size: 2rem; font-weight: 800; color: #ffffff;
    margin: 0 0 6px 0; line-height: 1.2;
}
.wf-page-sub {
    font-size: .95rem; color: #71717a; margin: 0 0 36px 0;
}

/* ── Stage card ── */
.wf-card {
    background: linear-gradient(135deg, rgba(17,17,27,.95) 0%, rgba(24,24,37,.95) 100%);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 18px;
    padding: 22px 26px;
    position: relative;
    transition: all .25s ease;
    animation: fadeSlideUp .4s ease both;
}
.wf-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 36px rgba(0,0,0,.45);
}

/* ── Parallel wrapper ── */
.wf-parallel {
    display: flex;
    gap: 14px;
    align-items: stretch;
}
.wf-parallel-lane {
    flex: 1;
    background: linear-gradient(135deg, rgba(17,17,27,.95), rgba(24,24,37,.95));
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 18px;
    padding: 20px 22px;
    position: relative;
    transition: all .25s ease;
    animation: fadeSlideUp .4s ease both;
}
.wf-parallel-lane:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 36px rgba(0,0,0,.45);
}
.wf-parallel-banner {
    text-align: center;
    font-size: .7rem; font-weight: 700;
    letter-spacing: .9px; text-transform: uppercase;
    color: #818cf8;
    background: rgba(99,102,241,.1);
    border: 1px solid rgba(99,102,241,.22);
    border-radius: 8px;
    padding: 5px 0;
    margin-bottom: 16px;
}

/* ── Stage number pill ── */
.wf-num {
    width: 28px; height: 28px;
    border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: .75rem; font-weight: 800;
    flex-shrink: 0;
}

/* ── Status dot ── */
.wf-dot {
    width: 8px; height: 8px; border-radius: 50%;
    position: absolute; top: 16px; right: 16px;
}

/* ── Title / desc ── */
.wf-title { font-size: .95rem; font-weight: 700; color: #f4f4f5; margin: 0 0 7px 0; line-height: 1.3; }
.wf-desc  { font-size: .8rem;  color: #a1a1aa; line-height: 1.6; margin: 0; }

/* ── Connector arrow ── */
.wf-arrow {
    display: flex; justify-content: center; align-items: center;
    padding: 6px 0;
}

/* ── Colour tokens ── */
.c-indigo  { background:rgba(99,102,241,.18); color:#a5b4fc; border:1px solid rgba(99,102,241,.35); }
.c-violet  { background:rgba(139,92,246,.18); color:#c4b5fd; border:1px solid rgba(139,92,246,.35); }
.c-cyan    { background:rgba(6,182,212,.18);  color:#67e8f9; border:1px solid rgba(6,182,212,.35);  }
.c-emerald { background:rgba(16,185,129,.18); color:#6ee7b7; border:1px solid rgba(16,185,129,.35); }
.c-amber   { background:rgba(245,158,11,.18); color:#fcd34d; border:1px solid rgba(245,158,11,.35); }
.c-rose    { background:rgba(239,68,68,.18);  color:#fca5a5; border:1px solid rgba(239,68,68,.35);  }
.c-sky     { background:rgba(14,165,233,.18); color:#7dd3fc; border:1px solid rgba(14,165,233,.35); }
.c-pink    { background:rgba(236,72,153,.18); color:#f9a8d4; border:1px solid rgba(236,72,153,.35); }
.c-teal    { background:rgba(20,184,166,.18); color:#5eead4; border:1px solid rgba(20,184,166,.35); }

.bd-indigo  { border-color:rgba(99,102,241,.35);  box-shadow: inset 0 0 28px rgba(99,102,241,.12),  0 0 0 1px rgba(99,102,241,.12); }
.bd-violet  { border-color:rgba(139,92,246,.35);  box-shadow: inset 0 0 28px rgba(139,92,246,.12),  0 0 0 1px rgba(139,92,246,.12); }
.bd-cyan    { border-color:rgba(6,182,212,.35);   box-shadow: inset 0 0 28px rgba(6,182,212,.12),   0 0 0 1px rgba(6,182,212,.12); }
.bd-emerald { border-color:rgba(16,185,129,.35);  box-shadow: inset 0 0 28px rgba(16,185,129,.12),  0 0 0 1px rgba(16,185,129,.12); }
.bd-amber   { border-color:rgba(245,158,11,.35);  box-shadow: inset 0 0 28px rgba(245,158,11,.12),  0 0 0 1px rgba(245,158,11,.12); }
.bd-rose    { border-color:rgba(239,68,68,.35);   box-shadow: inset 0 0 28px rgba(239,68,68,.12),   0 0 0 1px rgba(239,68,68,.12); }
.bd-sky     { border-color:rgba(14,165,233,.35);  box-shadow: inset 0 0 28px rgba(14,165,233,.12),  0 0 0 1px rgba(14,165,233,.12); }
.bd-pink    { border-color:rgba(236,72,153,.35);  box-shadow: inset 0 0 28px rgba(236,72,153,.12),  0 0 0 1px rgba(236,72,153,.12); }
.bd-teal    { border-color:rgba(20,184,166,.35);  box-shadow: inset 0 0 28px rgba(20,184,166,.12),  0 0 0 1px rgba(20,184,166,.12); }

.dot-indigo  { background:#6366f1; box-shadow:0 0 7px #6366f1; }
.dot-violet  { background:#8b5cf6; box-shadow:0 0 7px #8b5cf6; }
.dot-cyan    { background:#06b6d4; box-shadow:0 0 7px #06b6d4; }
.dot-emerald { background:#10b981; box-shadow:0 0 7px #10b981; }
.dot-amber   { background:#f59e0b; box-shadow:0 0 7px #f59e0b; animation:badgePulse 2s ease infinite; }
.dot-rose    { background:#ef4444; box-shadow:0 0 7px #ef4444; }
.dot-sky     { background:#0ea5e9; box-shadow:0 0 7px #0ea5e9; }
.dot-pink    { background:#ec4899; box-shadow:0 0 7px #ec4899; }
.dot-teal    { background:#14b8a6; box-shadow:0 0 7px #14b8a6; }

/* ── Final output badge ── */
.wf-final {
    display: flex; justify-content: center; padding: 18px 0 4px 0;
}
.wf-final-badge {
    background: linear-gradient(135deg, rgba(99,102,241,.15), rgba(16,185,129,.12));
    border: 1px solid rgba(99,102,241,.3);
    border-radius: 12px;
    padding: 12px 28px;
    display: inline-flex; align-items: center; gap: 10px;
    font-size: .9rem; font-weight: 700; color: #f4f4f5;
}
</style>
""", unsafe_allow_html=True)

# ── Arrow helper ──────────────────────────────────────────────────────────────
ARROW = """
<div class="wf-arrow">
  <svg width="2" height="30" viewBox="0 0 2 30">
    <line x1="1" y1="0" x2="1" y2="26" stroke="#374151" stroke-width="1.5" stroke-dasharray="4 3"/>
    <polygon points="1,30 -3,22 5,22" fill="#374151"/>
  </svg>
</div>
"""

# ── Page ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="wf-page">', unsafe_allow_html=True)

st.markdown("""
<h1 class="wf-page-title">Pipeline Workflow</h1>
<p class="wf-page-sub">9-stage autonomous multi-agent research execution pipeline</p>
""", unsafe_allow_html=True)

# ── Stage 1 ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="wf-card bd-indigo">
  <div class="wf-dot dot-indigo"></div>
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
    <div class="wf-num c-indigo">1</div>
    <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24"
         fill="none" stroke="#a5b4fc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
    </svg>
    <span class="wf-title" style="margin:0;">Strategic Planner Agent</span>
  </div>
  <p class="wf-desc">
    Receives the research topic and generates a structured 3-subtopic research roadmap.
    Dynamically assigns sub-task names to the downstream parallel Researcher Agents,
    ensuring focused and non-overlapping research scopes across all three tracks.
  </p>
</div>
{ARROW}
""", unsafe_allow_html=True)

# ── Stage 2 — Parallel ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="wf-parallel-banner">⚡ Parallel Execution — 3 Simultaneous Researcher Agents</div>
<div class="wf-parallel">

  <div class="wf-parallel-lane bd-violet" style="animation-delay:.05s;">
    <div class="wf-dot dot-violet"></div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:9px;">
      <div class="wf-num c-violet" style="font-size:.68rem;">2A</div>
      <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
           fill="none" stroke="#c4b5fd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
      </svg>
      <span class="wf-title" style="margin:0;font-size:.87rem;">Researcher A</span>
    </div>
    <p class="wf-desc">Deep-dives into the first assigned subtopic. Gathers authoritative source material and drafts a focused research report.</p>
  </div>

  <div class="wf-parallel-lane bd-violet" style="animation-delay:.1s;">
    <div class="wf-dot dot-violet"></div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:9px;">
      <div class="wf-num c-violet" style="font-size:.68rem;">2B</div>
      <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
           fill="none" stroke="#c4b5fd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
      </svg>
      <span class="wf-title" style="margin:0;font-size:.87rem;">Researcher B</span>
    </div>
    <p class="wf-desc">Independently researches the second subtopic. Cross-validates facts and produces a comprehensive draft without blocking A or C.</p>
  </div>

  <div class="wf-parallel-lane bd-violet" style="animation-delay:.15s;">
    <div class="wf-dot dot-violet"></div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:9px;">
      <div class="wf-num c-violet" style="font-size:.68rem;">2C</div>
      <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
           fill="none" stroke="#c4b5fd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
      </svg>
      <span class="wf-title" style="margin:0;font-size:.87rem;">Researcher C</span>
    </div>
    <p class="wf-desc">Covers the third subtopic concurrently, leveraging ingested PDF literature alongside live web sources for the richest possible sourcing.</p>
  </div>

</div>
{ARROW}
""", unsafe_allow_html=True)

# ── Stages 3–9 ────────────────────────────────────────────────────────────────
stages = [
    ("3", "c-cyan",    "bd-cyan",    "dot-cyan",
     '<path d="M16 3H1v18h15"/><path d="M8 8h8"/><path d="M8 12h8"/><path d="M8 16h8"/><path d="M21 6l-5 6 5 6"/>',
     "#67e8f9",
     "Draft Consolidation Agent",
     "Aggregates the three parallel researcher outputs and intelligently merges them into a single, coherent master draft. Removes duplication, resolves contradictions, and structures the combined knowledge for downstream processing."),

    ("4", "c-emerald", "bd-emerald", "dot-emerald",
     '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
     "#6ee7b7",
     "Memory / RAG Enhancement",
     "Performs a semantic search over the vector memory store to inject relevant prior research context into the consolidated draft, ensuring continuity across sessions and preventing redundant re-investigation of already-covered topics."),

    ("5", "c-amber",   "bd-amber",   "dot-amber",
     '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>',
     "#fcd34d",
     "Executive Summarizer Agent",
     "Distils the memory-augmented draft into a structured executive summary. Highlights key findings, organises arguments into logical sections, and extracts the most impactful insights in a clean, publishable format."),

    ("6", "c-rose",    "bd-rose",    "dot-rose",
     '<path d="M2 20h.01"/><path d="M7 20v-4"/><path d="M12 20v-8"/><path d="M17 20V8"/><path d="M22 4v16"/>',
     "#fca5a5",
     "AI Critic Agent",
     "Performs a rigorous multi-dimensional review of the summary — evaluating factual accuracy, argument completeness, logical consistency, and potential bias. Produces a structured critique report with specific improvement recommendations."),

    ("7", "c-sky",     "bd-sky",     "dot-sky",
     '<path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>',
     "#7dd3fc",
     "Self-Correction Loop",
     "Takes the critique report and feeds it back to iteratively refine the research output. Addresses each flagged issue, strengthens weak arguments, fills citation gaps, and rebalances content structure — producing a revision-validated document."),

    ("8", "c-pink",    "bd-pink",    "dot-pink",
     '<path d="M4 22h14a2 2 0 0 0 2-2V7.5L14.5 2H6a2 2 0 0 0-2 2v4"/><polyline points="14 2 14 8 20 8"/><path d="M2 15h10"/><path d="m9 18 3-3-3-3"/>',
     "#f9a8d4",
     "Report Generator Agent",
     "Synthesises all refined outputs into the final, publication-ready research report. Applies professional formatting with structured sections, executive abstract, key findings, methodology notes, limitations, and a full references section."),

    ("9", "c-teal",    "bd-teal",    "dot-teal",
     '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
     "#5eead4",
     "Memory Persistence",
     "Permanently stores the completed research report as semantic vector embeddings. Future research sessions can semantically retrieve any past finding, enabling true long-term multi-session intelligence with full workspace isolation."),
]

for i, (num, num_cls, border_cls, dot_cls, svg_paths, stroke, title, desc) in enumerate(stages):
    arrow_html = ARROW if i < len(stages) - 1 else ""
    st.markdown(f"""
<div class="wf-card {border_cls}">
  <div class="wf-dot {dot_cls}"></div>
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
    <div class="wf-num {num_cls}">{num}</div>
    <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24"
         fill="none" stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      {svg_paths}
    </svg>
    <span class="wf-title" style="margin:0;">{title}</span>
  </div>
  <p class="wf-desc">{desc}</p>
</div>
{arrow_html}
""", unsafe_allow_html=True)

# ── Final badge ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="wf-final">
  <div class="wf-final-badge">
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
         fill="none" stroke="#34d399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
    Final Output: Publication-Ready Research Report + Persistent Vector Memory
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
