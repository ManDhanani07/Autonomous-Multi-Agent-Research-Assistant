import os
import warnings
import logging

# Silence all verbose PyTorch/transformers path access warnings globally
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

import streamlit as st
import os
import sys
import time
import json
import threading

# Add the project root to the Python path so it can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontend.shared_theme import apply_shared_theme

# Page configuration
st.set_page_config(
    page_title="Nexus | Autonomous AI Researcher",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global premium SaaS theme & sidebar widgets
apply_shared_theme()

# ==========================================
# Lucide Icons (Inline SVGs)
# ==========================================
ICON_AI_ENGINE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
ICON_RESEARCHER = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>'
ICON_SUMMARIZER = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>'
ICON_CRITIC = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/></svg>'
ICON_CHECK = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'
ICON_PLANNER = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3V6z"/><path d="M9 3v15"/><path d="M15 6v15"/></svg>'
ICON_RAG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/></svg>'
ICON_CORRECTION = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>'
ICON_VERIFIED = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>'
ICON_SPARKLES = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3z"/></svg>'
ICON_DRAFT = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>'
ICON_REPORT = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>'


# ==========================================
# Helper: Remove hallucinated markdown links
# ==========================================
def strip_fake_links(text: str) -> str:
    """
    Removes hallucinated markdown hyperlinks [text](url) from the report body.
    Preserves:
      - Real http/https URLs: [title](https://...) → kept as clickable link
      - Local static PDF URLs: [title](/app/static/...) → kept as clickable link
    Only strips links where the URL is not a real http address or local static path.
    """
    import re
    # Keep real links and local PDF paths intact, strip everything else
    def replacer(m):
        link_text = m.group(1)
        url = m.group(2)
        if url.startswith("http://") or url.startswith("https://") or url.startswith("/app/static/") or url.startswith("/static/"):
            return m.group(0)  # keep real links and local served PDF links
        return link_text      # strip fake/invented links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replacer, text)
    return text


# ==========================================
# Main UI
# ==========================================

# Hero Section
st.markdown("""
<div class="card-container">
    <div style="margin-bottom: 16px;">
        <span style="background-color: rgba(99, 102, 241, 0.1); color: #818cf8; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(99, 102, 241, 0.2);">Nexus AI OS v3.0</span>
    </div>
    <h1 style="font-size: 3.2rem; font-weight: 700; margin-bottom: 0.5rem; line-height: 1.15; color: #ffffff;">
        Intelligent Research,<br>Powered by <span style="background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">Nexus Agents.</span>
    </h1>
    <p style="font-size: 1.15rem; color: #a1a1aa; font-weight: 400; margin-bottom: 2rem; line-height: 1.6; max-width: 700px;">
        Input your topic below to initialize the multi-agent neural network. Generating highly structured, deeply researched professional reports in seconds.
    </p>
</div>
""", unsafe_allow_html=True)

tab_research, tab_pdf = st.tabs(["🔬 Research Workspace", "📁 Document Library"])

with tab_research:
    # Input Section
    st.markdown("<h3 style='margin-bottom: 16px; color: #ffffff; font-size: 1.4rem;'>Initialize Parameters</h3>", unsafe_allow_html=True)
    topic = st.text_input("Research Topic", placeholder="e.g., Quantum Machine Learning Algorithms...", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        initiate_btn = st.button("Execute Neural Protocol")
    
    # Placeholder for dynamic workflow UI
    workflow_ui = st.empty()
    output_ui = st.empty()

with tab_pdf:
    st.markdown("<h3 style='margin-bottom: 12px; color: #ffffff; font-size: 1.4rem;'>Ingest PDF Literature</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a1a1aa; font-size:0.95rem; margin-bottom:20px;'>Upload academic PDF documents to parse, split, and vectorize their contents into the RAG system database.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Academic PDF Paper", type=["pdf"])
    if uploaded_file is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Process & Ingest Paper", key="ingest_pdf_button"):
            # Set up save paths
            database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
            upload_dir = os.path.join(database_dir, "uploaded_pdfs")
            os.makedirs(upload_dir, exist_ok=True)
            temp_path = os.path.join(upload_dir, uploaded_file.name)
            
            # Save file to database
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Save file to static for serving
            static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploaded_pdfs")
            os.makedirs(static_dir, exist_ok=True)
            static_path = os.path.join(static_dir, uploaded_file.name)
            with open(static_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # Ingest to Chroma
            from tools.pdf_parser_tool import ingest_pdf_to_chroma
            try:
                with st.spinner(f"Parsing, chunking, and indexing '{uploaded_file.name}'..."):
                    record = ingest_pdf_to_chroma(temp_path, uploaded_file.name)
                st.success(f"Successfully processed and ingested '{record['title']}'!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to ingest paper: {e}")
                
    st.markdown("---")
    
    # Render library list
    database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
    metadata_file = os.path.join(database_dir, "pdf_metadata.json")
    ingested_papers = []
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                ingested_papers = json.load(f)
        except Exception:
            ingested_papers = []
            
    if ingested_papers:
        st.markdown(f"<h3 style='color:#ffffff; margin-bottom: 16px;'>Ingested Papers ({len(ingested_papers)})</h3>", unsafe_allow_html=True)
        for idx, paper in enumerate(ingested_papers, start=1):
            sections_str = ", ".join(paper.get("sections", []))
            with st.expander(f"📄  {paper.get('title')}  ·  {paper.get('chunk_count')} chunks"):
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:12px;"
                    f"padding:12px 16px;margin-bottom:14px;"
                    f"background:rgba(99,102,241,0.07);"
                    f"border-radius:10px;border:1px solid rgba(99,102,241,0.18);'>"
                    f"<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#818cf8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
                    f"<path d='M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z'/><path d='M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z'/>"
                    f"</svg>"
                    f"<div style='flex:1;min-width:0;'>"
                    f"<p style='margin:0;font-size:0.7rem;font-weight:700;text-transform:uppercase;"
                    f"letter-spacing:0.1em;color:#818cf8;'>Paper {idx} · {paper.get('filename')}</p>"
                    f"<p style='margin:2px 0 0 0;font-size:0.95rem;font-weight:600;color:#ffffff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{paper.get('title')}</p>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
                # Stats badges
                st.markdown(
                    f"<div style='display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap;'>"
                    f"<span style='display:inline-flex;align-items:center;gap:6px;"
                    f"background:rgba(129,140,248,0.1);color:#818cf8;"
                    f"padding:5px 12px;border-radius:20px;font-size:0.8rem;"
                    f"border:1px solid rgba(129,140,248,0.3);font-weight:600;'>"
                    f" Chunks: {paper.get('chunk_count')}</span>"
                    f"<span style='display:inline-flex;align-items:center;gap:6px;"
                    f"background:rgba(167,139,250,0.1);color:#c084fc;"
                    f"padding:5px 12px;border-radius:20px;font-size:0.8rem;"
                    f"border:1px solid rgba(167,139,250,0.3);font-weight:600;'>"
                    f" Tables: {paper.get('table_count')}</span>"
                    f"<span style='display:inline-flex;align-items:center;gap:6px;"
                    f"background:rgba(52,211,153,0.1);color:#34d399;"
                    f"padding:5px 12px;border-radius:20px;font-size:0.8rem;"
                    f"border:1px solid rgba(52,211,153,0.3);font-weight:600;'>"
                    f" References: {paper.get('reference_count')}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.markdown(f"**Extracted Sections:** {sections_str}")
                
                # Add View/Download buttons
                filename = paper.get("filename")
                import urllib.parse
                safe_filename = urllib.parse.quote(filename)
                pdf_url = f"/app/static/uploaded_pdfs/{safe_filename}"
                
                col_view, col_dl = st.columns([1, 1])
                with col_view:
                    st.markdown(f"<a href='{pdf_url}' target='_blank' style='text-decoration:none;'><button style='width:100%; padding:8px 16px; background-color:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.4); border-radius:6px; color:#a5b4fc; font-weight:600; cursor:pointer;'>👁️ View PDF in Browser</button></a>", unsafe_allow_html=True)
                with col_dl:
                    upload_dir = os.path.join(database_dir, "uploaded_pdfs")
                    pdf_path = os.path.join(upload_dir, filename)
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            pdf_data = f.read()
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name=filename,
                            mime="application/pdf",
                            key=f"dl_{filename}"
                        )
                st.markdown("---")
                st.markdown(f"**Summary Preview:**\n{paper.get('summary')}")
    else:
        st.markdown(
            "<div style='display:flex;align-items:center;gap:12px;"
            "padding:16px 20px;margin-bottom:24px;"
            "background:rgba(59,130,246,0.08);color:#93c5fd;"
            "border-radius:10px;border:1px solid rgba(59,130,246,0.25);font-weight:600;'>"
            "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#93c5fd' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><line x1='12' y1='16' x2='12' y2='12'/><line x1='12' y1='8' x2='12.01' y2='8'/></svg>"
            "<span>No papers have been ingested yet. Upload an academic PDF above to start building your literature library.</span>"
            "</div>",
            unsafe_allow_html=True
        )

def render_workflow_step(current_step):
    """Generates the HTML for the workflow pipeline based on the current step (1 to 6)"""
    
    def get_state(step_id):
        if step_id < current_step: return "completed"
        if step_id == current_step: return "active"
        return "pending"
    
    def get_status_text(step_id, default_text, active_text):
        if step_id < current_step: return "Completed"
        if step_id == current_step: return active_text
        return default_text

    if current_step == 6:
        s1, s2, s3, s4, s5, s6 = "completed", "completed", "completed", "completed", "completed", "completed"
        t1, t2, t3, t4, t5, t6 = "Completed", "Completed", "Completed", "Completed", "Completed", "Pipeline Finished"
    else:
        s1 = get_state(1)
        s2 = get_state(2)
        s3 = get_state(3)
        s4 = get_state(4)
        s5 = get_state(5)
        s6 = "pending"
        t1 = get_status_text(1, "Awaiting execution", "Connecting to Groq Llama 3.3 70B...")
        t2 = get_status_text(2, "Awaiting execution", "Architecting Strategic Roadmap...")
        t3 = get_status_text(3, "Awaiting execution", "Drafting v1 Report...")
        t4 = get_status_text(4, "Awaiting execution", "Evaluating research...")
        t5 = get_status_text(5, "Awaiting execution", "Self-Correcting & Refining...")
        t6 = "Awaiting execution"

    html = f"""
<div class="workflow-container">
<!-- Step 1: AI Engine -->
<div class="workflow-card {s1}">
<div class="icon-box">{ICON_AI_ENGINE}</div>
<div class="content">
<div class="title">System Initialization</div>
<div class="status">{t1}</div>
</div>
</div>

<!-- Step 2: Planner -->
<div class="workflow-card {s2}">
<div class="icon-box">{ICON_PLANNER}</div>
<div class="content">
<div class="title">Phase 1: Strategic Planner Agent</div>
<div class="status">{t2}</div>
</div>
</div>

<!-- Step 3: Researcher -->
<div class="workflow-card {s3}">
<div class="icon-box">{ICON_RESEARCHER}</div>
<div class="content">
<div class="title">Phase 2: Elite Researcher Agent</div>
<div class="status">{t3}</div>
</div>
</div>

<!-- Step 4: Critic -->
<div class="workflow-card {s4}">
<div class="icon-box">{ICON_CRITIC}</div>
<div class="content">
<div class="title">Phase 3: AI Critic Evaluation</div>
<div class="status">{t4}</div>
</div>
</div>

<!-- Step 5: Refinement -->
<div class="workflow-card {s5}">
<div class="icon-box">{ICON_SUMMARIZER}</div>
<div class="content">
<div class="title">Phase 4: Self-Correction (v2)</div>
<div class="status">{t5}</div>
</div>
</div>

<!-- Step 6: Complete -->
<div class="workflow-card {s6}">
<div class="icon-box">{ICON_CHECK}</div>
<div class="content">
<div class="title">Pipeline Complete</div>
<div class="status">{t6}</div>
</div>
</div>
</div>
"""
    workflow_ui.markdown(html, unsafe_allow_html=True)


if initiate_btn:
    if not topic.strip():
        st.warning("Please provide a valid research topic to begin.")
    else:
        st.session_state.running           = True
        st.session_state.topic             = topic
        st.session_state.full_research     = None
        st.session_state.executive_summary = None
        st.session_state.critique_analysis = None
        st.session_state.planner_roadmap   = None
        st.session_state.retrieved_memories = []   # RAG: store for UI display
        st.session_state.academic_papers = []      # Academic sources
        st.session_state.fallback_used = False     # Fallback flag
        st.session_state.retrieved_pdf_chunks = [] # PDF RAG chunks

if getattr(st.session_state, 'running', False):
    if not st.session_state.full_research:
        # Step 1: Initialize
        render_workflow_step(1)
        from agents.planner_agent import generate_plan
        from agents.researcher_agent import generate_research
        from orchestrators.self_correction_loop import run_optimization_loop
        time.sleep(1)

        # Step 2: Planner Agent
        render_workflow_step(2)
        st.session_state.planner_roadmap = generate_plan(st.session_state.topic)
        
        # Step 3: Researcher Agent (Generates v1)
        render_workflow_step(3)
        research_result = generate_research(st.session_state.topic, plan=st.session_state.planner_roadmap)
        initial_report = research_result.get("report", "")
        st.session_state.retrieved_memories = research_result.get("memories", [])
        st.session_state.academic_papers = research_result.get("academic_papers", [])
        st.session_state.fallback_used = research_result.get("fallback_used", False)
        st.session_state.retrieved_pdf_chunks = research_result.get("pdf_chunks", [])
        
        if initial_report.startswith("⚠️"):
            # Skip loop if quota hit
            st.session_state.full_research = initial_report
            st.session_state.executive_summary = initial_report
            st.session_state.critique_analysis = {"error": initial_report}
            st.session_state.optimized_data = None
        else:
            # Step 4 & 5: Critic Evaluation & Self-Correction (Handled by loop controller)
            render_workflow_step(4)
            loop_result = run_optimization_loop(st.session_state.topic, initial_report)
            
            # Update to Step 5 dynamically
            render_workflow_step(5)
            
            # Unpack results
            st.session_state.full_research = loop_result["final_report"]
            st.session_state.executive_summary = loop_result["final_summary"]
            st.session_state.critique_analysis = loop_result["final_critique"]
            st.session_state.optimized_data = loop_result

        # Step 6: Complete
        render_workflow_step(6)
        time.sleep(0.5)

        # Save to memory in a background thread
        def save_memory_background(topic, research, summary, critique_dict):
            try:
                from memory.memory_manager import save_research_to_memory
                # Convert the JSON critique to string for saving
                critique_str = str(critique_dict) if isinstance(critique_dict, dict) else critique_dict
                save_research_to_memory(topic, research, summary, critique_str)
            except Exception as e:
                print(f"Memory System Error: {e}")

        thread = threading.Thread(
            target=save_memory_background,
            args=(
                st.session_state.topic,
                st.session_state.full_research,
                st.session_state.executive_summary,
                st.session_state.critique_analysis
            )
        )
        thread.start()

        workflow_ui.empty()
        st.rerun()

    # ── Render Output from Session State ─────────────────────────────────
    if st.session_state.executive_summary and st.session_state.critique_analysis is not None:
        clean_summary  = st.session_state.executive_summary.replace("## Executive Summary", "").strip()
        
        # Format the JSON dict into Markdown for the UI
        crit_dict = st.session_state.critique_analysis
        if isinstance(crit_dict, dict) and "error" in crit_dict:
            clean_critique = f"⚠️ {crit_dict['error']}"
            critique_is_error = True
        elif isinstance(crit_dict, dict):
            critique_is_error = False
            clean_critique = f"**Overall Score:** {crit_dict.get('score', 'N/A')}/10\n\n"
            clean_critique += "**Strengths:**\n" + "".join([f"- {s}\n" for s in crit_dict.get('strengths', [])]) + "\n"
            clean_critique += "**Weaknesses:**\n" + "".join([f"- {w}\n" for w in crit_dict.get('weaknesses', [])]) + "\n"
            clean_critique += "**Missing Topics:**\n" + "".join([f"- {m}\n" for m in crit_dict.get('missing_topics', [])]) + "\n"
            clean_critique += "**Improvement Suggestions:**\n" + "".join([f"- {i}\n" for i in crit_dict.get('improvement_suggestions', [])]) + "\n"
            clean_critique += "**Clarity Evaluation:**\n" + str(crit_dict.get('clarity_evaluation', ''))
        else:
            clean_critique = str(crit_dict)
            critique_is_error = clean_critique.startswith("⚠️")

        summary_is_error  = clean_summary.startswith("⚠️")

        with output_ui.container():
            if summary_is_error:
                st.markdown(
                    "<div style='display:flex;align-items:center;gap:12px;"
                    "padding:16px 20px;margin-bottom:24px;"
                    "background:rgba(239,68,68,0.08);color:#fca5a5;"
                    "border-radius:10px;border:1px solid rgba(239,68,68,0.25);font-weight:600;'>"
                    "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#fca5a5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z'/><line x1='12' y1='9' x2='12' y2='13'/><line x1='12' y1='17' x2='12.01' y2='17'/></svg>"
                    "<span>Research pipeline encountered an API quota issue.</span>"
                    "</div>",
                    unsafe_allow_html=True
                )
                st.markdown(clean_summary)
            else:
                st.markdown(
                    "<div style='display:flex;align-items:center;gap:12px;"
                    "padding:16px 20px;margin-bottom:14px;"
                    "background:rgba(16,185,129,0.08);color:#34d399;"
                    "border-radius:10px;border:1px solid rgba(16,185,129,0.25);font-weight:600;'>"
                    "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#34d399' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/></svg>"
                    "<span>Memory Saved Successfully</span>"
                    "</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    "<div style='display:flex;align-items:center;gap:12px;"
                    "padding:16px 20px;margin-bottom:24px;"
                    "background:rgba(16,185,129,0.08);color:#34d399;"
                    "border-radius:10px;border:1px solid rgba(16,185,129,0.25);font-weight:600;'>"
                    "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#34d399' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>"
                    "<span>Autonomous Research Pipeline Complete.</span>"
                    "</div>",
                    unsafe_allow_html=True
                )
                
                # ── Planner Roadmap Panel ──────────────────────────────────
                plan = getattr(st.session_state, "planner_roadmap", None)
                if plan:
                    st.markdown(
                        f"<h3 style='margin-top: 30px; margin-bottom: 12px; color: #a855f7; "
                        f"font-size: 1.3rem; display: flex; align-items: center; gap: 10px;'>"
                        f"<span style='color:#a855f7'>{ICON_PLANNER}</span> Planner Agent Roadmap</h3>",
                        unsafe_allow_html=True
                    )
                    
                    with st.expander("View Strategic Investigation Roadmap"):
                        st.markdown(f"**Overview:** {plan.get('overview', '')}")
                        
                        colA, colB = st.columns(2)
                        with colA:
                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:8px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#6366f1' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><path d='M12 8v4'/><path d='M12 16h.01'/></svg>"
                                " Research Objectives</h4>",
                                unsafe_allow_html=True
                            )
                            for obj in plan.get('objectives', []):
                                st.markdown(f"- {obj}")

                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:16px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#10b981' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><path d='M14 2v6h6'/><path d='M16 13H8'/><path d='M16 17H8'/><path d='M10 9H8'/></svg>"
                                " Core Subtopics</h4>",
                                unsafe_allow_html=True
                            )
                            for sub in plan.get('subtopics', []):
                                st.markdown(f"- {sub}")

                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:16px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#f59e0b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='3'/><path d='M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83'/></svg>"
                                " Technical Areas</h4>",
                                unsafe_allow_html=True
                            )
                            for tech in plan.get('technical_areas', []):
                                st.markdown(f"- {tech}")

                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:16px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#06b6d4' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'/><path d='m21 21-4.3-4.3'/></svg>"
                                " Recommended Focus Areas</h4>",
                                unsafe_allow_html=True
                            )
                            for focus in plan.get('focus_areas', []):
                                st.markdown(f"- {focus}")

                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:16px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#ec4899' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M5 12h14'/><path d='m12 5 7 7-7 7'/></svg>"
                                " Future Investigation Opportunities</h4>",
                                unsafe_allow_html=True
                            )
                            for opp in plan.get('future_opportunities', []):
                                st.markdown(f"- {opp}")

                        with colB:
                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:8px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#a855f7' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3V6z'/><path d='M9 3v15'/><path d='M15 6v15'/></svg>"
                                " Investigation Roadmap</h4>",
                                unsafe_allow_html=True
                            )
                            for phase in plan.get('roadmap', []):
                                st.markdown(f"- {phase}")

                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:16px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#34d399' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8'/><path d='M21 3v5h-5'/><path d='M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16'/><path d='M8 16H3v5'/></svg>"
                                " Suggested Workflow Order</h4>",
                                unsafe_allow_html=True
                            )
                            for step in plan.get('suggested_order', []):
                                st.markdown(f"1. {step}")

                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:16px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#38bdf8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><path d='M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3'/><path d='M12 17h.01'/></svg>"
                                " Critical Questions</h4>",
                                unsafe_allow_html=True
                            )
                            for q in plan.get('critical_questions', []):
                                st.markdown(f"- {q}")

                            st.markdown(
                                "<h4 style='display:flex;align-items:center;gap:8px;color:#ffffff;margin-top:16px;margin-bottom:6px;'>"
                                "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='#f97316' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3z'/><path d='M12 9v4'/><path d='M12 17h.01'/></svg>"
                                " Potential Challenges</h4>",
                                unsafe_allow_html=True
                            )
                            for challenge in plan.get('potential_challenges', []):
                                st.markdown(f"- {challenge}")


                # ── Self-Correction Badge & Delta ────────────────────────
                opt_data = getattr(st.session_state, "optimized_data", None)
                if opt_data:
                    if opt_data.get("optimized"):
                        st.markdown(
                            f"""
                            <div style='background: linear-gradient(90deg, rgba(16, 185, 129, 0.15) 0%, rgba(52, 211, 153, 0.05) 100%);
                                        border-left: 4px solid #10b981; padding: 16px; border-radius: 8px; margin-top: 16px; margin-bottom: 24px;'>
                                <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'>
                                    <span style='color:#10b981;'>{ICON_SPARKLES}</span>
                                    <h4 style='margin: 0; color: #10b981;'>AI Self-Corrected &amp; Optimized</h4>
                                </div>
                                <p style='margin: 0; color: #a1a1aa; font-size: 0.95rem;'>
                                    The AI iteratively refined this report based on internal critique.<br>
                                    Score improved from <strong>{opt_data['original_critique'].get('score')}</strong> to <strong>{opt_data['final_critique'].get('score')}</strong> (+{opt_data['score_delta']}).
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style='background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%);
                                        border-left: 4px solid #3b82f6; padding: 16px; border-radius: 8px; margin-top: 16px; margin-bottom: 24px;'>
                                <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 8px;'>
                                    <span style='color:#3b82f6;'>{ICON_VERIFIED}</span>
                                    <h4 style='margin: 0; color: #3b82f6;'>AI Quality Verified</h4>
                                </div>
                                <p style='margin: 0; color: #a1a1aa; font-size: 0.95rem;'>
                                    The AI attempted to self-correct, but determined the original Draft v1 (Score: <strong>{opt_data['original_critique'].get('score')}</strong>) 
                                    was superior to the refined Draft v2 (Score: <strong>{opt_data['final_critique'].get('score')}</strong>).<br>
                                    Safely retained original version.
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                # ── RAG Memory Panel ──────────────────────────────────────
                retrieved_mems = getattr(st.session_state, "retrieved_memories", [])
                if retrieved_mems:
                    st.markdown(
                        f"<h3 style='margin-top: 30px; margin-bottom: 12px; color: #34d399; "
                        f"font-size: 1.3rem; display: flex; align-items: center; gap: 10px;'>"
                        f"<span style='color:#34d399'>{ICON_RAG}</span> RAG Memory Context — Retrieved &amp; Injected</h3>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<p style='color: #71717a; font-size: 0.9rem; margin-bottom: 16px;'>"
                        f"Found <strong style='color:#34d399'>{len(retrieved_mems)}</strong> semantically "
                        f"related past research session(s). These were injected into the prompt to produce "
                        f"a smarter, context-aware report.</p>",
                        unsafe_allow_html=True
                    )

                    for idx, mem in enumerate(retrieved_mems, start=1):
                        sim_pct   = mem.get("similarity_pct", "N/A")
                        sim_val   = mem.get("similarity_score", 0)
                        mem_topic = mem.get("topic", "Unknown Topic")
                        mem_date  = mem.get("metadata", {}).get("timestamp", "")

                        # Colour-code the similarity badge
                        if sim_val >= 0.70:
                            badge_colour = "#10b981"   # green  — high relevance
                        elif sim_val >= 0.45:
                            badge_colour = "#f59e0b"   # amber  — moderate
                        else:
                            badge_colour = "#6366f1"   # indigo — low but above threshold

                        try:
                            from datetime import datetime as _dt
                            mem_date = _dt.fromisoformat(mem_date).strftime("%b %d, %Y at %I:%M %p")
                        except Exception:
                            pass

                        # Single expander with Lucide icon header INSIDE (no duplication)
                        with st.expander(f"🗂  Memory {idx}  ·  {sim_pct} relevance  —  {mem_topic[:55]}{'...' if len(mem_topic) > 55 else ''}"):
                            # Rich Lucide icon title row inside
                            st.markdown(
                                f"<div style='display:flex;align-items:center;gap:12px;"
                                f"padding:12px 16px;margin-bottom:14px;"
                                f"background:rgba(52,211,153,0.07);"
                                f"border-radius:10px;border:1px solid rgba(52,211,153,0.18);'>"
                                # Folder icon
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#34d399' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
                                f"<path d='M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z'/>"
                                f"</svg>"
                                f"<div style='flex:1;min-width:0;'>"
                                f"<p style='margin:0;font-size:0.7rem;font-weight:700;text-transform:uppercase;"
                                f"letter-spacing:0.1em;color:#34d399;'>Memory {idx}</p>"
                                f"<p style='margin:2px 0 0 0;font-size:0.95rem;font-weight:600;color:#ffffff;"
                                f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{mem_topic}</p>"
                                f"</div>"
                                f"<span style='background:{badge_colour}22;color:{badge_colour};"
                                f"padding:4px 12px;border-radius:20px;font-size:0.8rem;"
                                f"font-weight:700;border:1px solid {badge_colour}55;flex-shrink:0;'>{sim_pct}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            # Badge row with Lucide icons
                            st.markdown(
                                f"<div style='display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap;'>"
                                # Clock icon badge
                                f"<span style='display:inline-flex;align-items:center;gap:6px;"
                                f"background:rgba(52,211,153,0.1);color:#34d399;"
                                f"padding:5px 12px;border-radius:20px;font-size:0.8rem;"
                                f"border:1px solid rgba(52,211,153,0.3);font-weight:600;'>"
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='#34d399' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>"
                                f" {mem_date}</span>"
                                # Zap icon badge
                                f"<span style='display:inline-flex;align-items:center;gap:6px;"
                                f"background:rgba(99,102,241,0.1);color:{badge_colour};"
                                f"padding:5px 12px;border-radius:20px;font-size:0.8rem;"
                                f"border:1px solid {badge_colour}40;font-weight:700;'>"
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='{badge_colour}' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'/></svg>"
                                f" Similarity: {sim_pct}</span>"
                                # ID badge
                                f"<span style='display:inline-flex;align-items:center;gap:6px;"
                                f"background:rgba(255,255,255,0.05);color:#71717a;"
                                f"padding:5px 12px;border-radius:20px;font-size:0.8rem;'>"
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='#71717a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>"
                                f" {mem.get('id', '—')}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                            # Similarity progress bar
                            st.progress(min(sim_val, 1.0))

                            # Full stored memory content
                            st.markdown(mem.get("document", ""))
                else:
                    st.markdown(
                        "<div style='display:flex;align-items:center;gap:12px;"
                        "padding:16px 20px;margin-bottom:24px;"
                        "background:rgba(59,130,246,0.08);color:#93c5fd;"
                        "border-radius:10px;border:1px solid rgba(59,130,246,0.25);font-weight:600;'>"
                        "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#93c5fd' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><line x1='12' y1='16' x2='12' y2='12'/><line x1='12' y1='8' x2='12.01' y2='8'/></svg>"
                        "<span>No related past research was found for this topic. This report has been stored and will be retrieved as context for future searches.</span>"
                        "</div>",
                        unsafe_allow_html=True
                    )


                # ── PDF Library Panel — grouped by file (1 card per PDF) ─────
                retrieved_pdf_chunks_ui = getattr(st.session_state, "retrieved_pdf_chunks", [])
                if retrieved_pdf_chunks_ui:
                    # Group chunks by unique source file
                    pdf_groups = {}
                    for chunk in retrieved_pdf_chunks_ui:
                        meta  = chunk.get("metadata", {})
                        fname = meta.get("source_file", "PDF")
                        if fname not in pdf_groups:
                            pdf_groups[fname] = {
                                "title":    meta.get("title", fname),
                                "sections": [],
                                "best_sim": 0,
                                "best_pct": "0%",
                                "best_excerpt": ""
                            }
                        g = pdf_groups[fname]
                        sec = meta.get("section", "")
                        if sec and sec not in g["sections"]:
                            g["sections"].append(sec)
                        sim = chunk.get("similarity_score", 0)
                        if sim > g["best_sim"]:
                            g["best_sim"]     = sim
                            g["best_pct"]     = chunk.get("similarity_pct", "—")
                            g["best_excerpt"] = chunk.get("document", "")[:300]

                    unique_count = len(pdf_groups)
                    st.markdown(
                        f"<h3 style='margin-top:30px;margin-bottom:12px;color:#f59e0b;"
                        f"font-size:1.3rem;display:flex;align-items:center;gap:10px;'>"
                        f"<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' "
                        f"stroke='#f59e0b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
                        f"<path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/>"
                        f"<path d='M14 2v6h6'/><path d='M16 13H8'/><path d='M16 17H8'/><path d='M10 9H8'/></svg>"
                        f" 📄 PDF Library — Used in This Report</h3>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<p style='color:#71717a;font-size:0.9rem;margin-bottom:16px;'>"
                        f"<strong style='color:#f59e0b'>{unique_count}</strong> of your uploaded PDF(s) matched this topic "
                        f"and were injected into the AI prompt.</p>",
                        unsafe_allow_html=True
                    )

                    for fname, g in pdf_groups.items():
                        sim_val   = g["best_sim"]
                        sim_pct   = g["best_pct"]
                        sections  = ", ".join(g["sections"]) or "—"
                        title     = g["title"]
                        excerpt   = g["best_excerpt"]
                        badge_col = "#10b981" if sim_val >= 0.6 else ("#f59e0b" if sim_val >= 0.4 else "#6366f1")
                        short_title = title[:70] + ("..." if len(title) > 70 else "")

                        import urllib.parse
                        safe_filename = urllib.parse.quote(fname)
                        pdf_url = f"/app/static/uploaded_pdfs/{safe_filename}"

                        with st.expander(f"📄  {short_title}  ·  Best match: {sim_pct}"):
                            # Header card
                            st.markdown(
                                f"<div style='background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.2);"
                                f"border-radius:8px;padding:12px 16px;margin-bottom:12px;'>"
                                f"<p style='margin:0 0 6px 0;font-size:0.7rem;font-weight:700;text-transform:uppercase;"
                                f"letter-spacing:0.1em;color:#f59e0b;'>PAPER TITLE & FILENAME</p>"
                                f"<p style='margin:0 0 4px 0;font-size:0.95rem;font-weight:600;color:#ffffff;'>{title}</p>"
                                f"<p style='margin:0 0 10px 0;font-size:0.8rem;color:#71717a;'>📄 {fname}</p>"
                                f"<div style='display:flex;gap:10px;flex-wrap:wrap;align-items:center;'>"
                                f"<span style='background:{badge_col}22;color:{badge_col};padding:3px 10px;"
                                f"border-radius:20px;font-size:0.78rem;font-weight:700;border:1px solid {badge_col}44;'>"
                                f"✦ Best match: {sim_pct}</span>"
                                f"<span style='background:rgba(255,255,255,0.05);color:#a1a1aa;padding:3px 10px;"
                                f"border-radius:20px;font-size:0.78rem;'>Sections: {sections}</span>"
                                f"<a href='{pdf_url}' target='_blank' style='text-decoration:none;display:inline-flex;align-items:center;'>"
                                f"<span style='background:rgba(99,102,241,0.15);color:#a5b4fc;padding:3px 10px;"
                                f"border-radius:20px;font-size:0.78rem;font-weight:600;border:1px solid rgba(99,102,241,0.3);'>👁️ View PDF</span></a>"
                                f"</div></div>",
                                unsafe_allow_html=True
                            )
                            st.progress(min(sim_val, 1.0))



                # ── Academic Literature Panel ──────────────────────────────────
                fallback_used = getattr(st.session_state, "fallback_used", False)
                academic_papers = getattr(st.session_state, "academic_papers", [])

                
                if fallback_used:
                    st.markdown(
                        "<div style='display:flex;align-items:center;gap:12px;"
                        "padding:16px 20px;margin-top:20px;margin-bottom:24px;"
                        "background:rgba(249,115,22,0.08);color:#fca5a5;"
                        "border-radius:10px;border:1px solid rgba(249,115,22,0.25);font-weight:600;'>"
                        "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#fca5a5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z'/><line x1='12' y1='9' x2='12' y2='13'/><line x1='12' y1='17' x2='12.01' y2='17'/></svg>"
                        "<span>Academic databases could not be reached or yielded no results. Fell back to Web Search intelligence.</span>"
                        "</div>",
                        unsafe_allow_html=True
                    )
                elif academic_papers:
                    st.markdown(
                        f"<h3 style='margin-top: 30px; margin-bottom: 12px; color: #818cf8; "
                        f"font-size: 1.3rem; display: flex; align-items: center; gap: 10px;'>"
                        f"<span style='color:#818cf8'>{ICON_RESEARCHER}</span> Retrieved Academic Literature</h3>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<p style='color: #71717a; font-size: 0.9rem; margin-bottom: 16px;'>"
                        f"Retrieved <strong style='color:#818cf8'>{len(academic_papers)}</strong> peer-reviewed publications "
                        f"from arXiv, Semantic Scholar, and Crossref. Prioritized based on citations, recency, and journal index.</p>",
                        unsafe_allow_html=True
                    )
                    
                    for idx, paper in enumerate(academic_papers, start=1):
                        title = paper.get("title", "No Title")
                        authors = ", ".join(paper.get("authors", [])[:3])
                        if len(paper.get("authors", [])) > 3:
                            authors += " et al."
                        year = paper.get("year", "N/A")
                        citations = paper.get("citations", 0)
                        venue = paper.get("venue") or "Academic Source"
                        url = paper.get("url") or "#"
                        abstract = paper.get("abstract") or "No abstract available."
                        
                        # Style-matched card expander
                        with st.expander(f"📄  Paper {idx}  ·  {citations} citations  —  {title[:55]}{'...' if len(title) > 55 else ''}"):
                            st.markdown(
                                f"<div style='display:flex;align-items:center;gap:12px;"
                                f"padding:12px 16px;margin-bottom:14px;"
                                f"background:rgba(129,140,248,0.07);"
                                f"border-radius:10px;border:1px solid rgba(129,140,248,0.18);'>"
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#818cf8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
                                f"<path d='M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z'/><path d='M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z'/>"
                                f"</svg>"
                                f"<div style='flex:1;min-width:0;'>"
                                f"<p style='margin:0;font-size:0.7rem;font-weight:700;text-transform:uppercase;"
                                f"letter-spacing:0.1em;color:#818cf8;'>Paper {idx} · {venue}</p>"
                                f"<a href='{url}' target='_blank' style='margin:2px 0 0 0;font-size:0.95rem;font-weight:600;color:#ffffff;text-decoration:none;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{title} ↗</a>"
                                f"</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                            # Info badges
                            st.markdown(
                                f"<div style='display:flex; gap:10px; margin-bottom:14px; flex-wrap:wrap;'>"
                                f"<span style='display:inline-flex;align-items:center;gap:6px;"
                                f"background:rgba(129,140,248,0.1);color:#818cf8;"
                                f"padding:5px 12px;border-radius:20px;font-size:0.8rem;"
                                f"border:1px solid rgba(129,140,248,0.3);font-weight:600;'>"
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='#818cf8' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>"
                                f" Published: {year}</span>"
                                
                                f"<span style='display:inline-flex;align-items:center;gap:6px;"
                                f"background:rgba(167,139,250,0.1);color:#c084fc;"
                                f"padding:5px 12px;border-radius:20px;font-size:0.8rem;"
                                f"border:1px solid rgba(167,139,250,0.3);font-weight:600;'>"
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='#c084fc' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><polygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'/></svg>"
                                f" Citations: {citations}</span>"
                                
                                f"<span style='display:inline-flex;align-items:center;gap:6px;"
                                f"background:rgba(52,211,153,0.1);color:#34d399;"
                                f"padding:5px 12px;border-radius:20px;font-size:0.8rem;"
                                f"border:1px solid rgba(52,211,153,0.3);font-weight:600;'>"
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='#34d399' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><ellipse cx='12' cy='5' rx='9' ry='3'/><path d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5'/><path d='M3 12c0 1.66 4 3 9 3s9-1.34 9-3'/></svg>"
                                f" DB: {paper.get('source', 'Unknown')}</span>"
                                
                                f"<span style='display:inline-flex;align-items:center;gap:6px;"
                                f"background:rgba(255,255,255,0.05);color:#71717a;"
                                f"padding:5px 12px;border-radius:20px;font-size:0.8rem;'>"
                                f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='#71717a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'/><circle cx='9' cy='7' r='4'/><path d='M23 21v-2a4 4 0 0 0-3-3.87'/><path d='M16 3.13a4 4 0 0 1 0 7.75'/></svg>"
                                f" {authors}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                            st.markdown(f"**Abstract:** {abstract}")

                # ── Executive Summary ────────────────────────────────────
                st.markdown(
                    f"""
                    <div style='margin-top:40px; margin-bottom:20px; padding:20px 24px;
                                background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(139,92,246,0.06) 100%);
                                border-left: 5px solid #6366f1; border-radius: 12px;'>
                        <div style='display:flex; align-items:center; gap:14px;'>
                            <span style='color:#818cf8; flex-shrink:0;'>{ICON_SUMMARIZER}</span>
                            <div>
                                <p style='margin:0; font-size:0.75rem; font-weight:700; letter-spacing:0.12em;
                                          text-transform:uppercase; color:#818cf8;'>Section 1</p>
                                <h2 style='margin:4px 0 0 0; font-size:2rem; font-weight:800; line-height:1.1;
                                           background: linear-gradient(90deg, #818cf8, #c084fc);
                                           -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
                                    Executive Summary
                                </h2>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown('<div id="exec-summary-anchor"></div>', unsafe_allow_html=True)
                st.markdown(clean_summary)

                # ── AI Critic Analysis ───────────────────────────────────
                st.markdown(
                    f"""
                    <div style='margin-top:40px; margin-bottom:20px; padding:20px 24px;
                                background: linear-gradient(135deg, rgba(245,158,11,0.12) 0%, rgba(249,115,22,0.06) 100%);
                                border-left: 5px solid #f59e0b; border-radius: 12px;'>
                        <div style='display:flex; align-items:center; gap:14px;'>
                            <span style='color:#fbbf24; flex-shrink:0;'>{ICON_CRITIC}</span>
                            <div>
                                <p style='margin:0; font-size:0.75rem; font-weight:700; letter-spacing:0.12em;
                                          text-transform:uppercase; color:#fbbf24;'>Section 2</p>
                                <h2 style='margin:4px 0 0 0; font-size:2rem; font-weight:800; line-height:1.1;
                                           background: linear-gradient(90deg, #fbbf24, #f97316);
                                           -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
                                    AI Critic Analysis
                                </h2>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown('<div id="critic-anchor"></div>', unsafe_allow_html=True)
                if critique_is_error:
                    st.warning(clean_critique)
                else:
                    st.markdown(clean_critique)

                st.markdown("<br>", unsafe_allow_html=True)

                with st.container():
                    st.markdown("<br>", unsafe_allow_html=True)
                    opt_data = getattr(st.session_state, "optimized_data", None)
                    if opt_data and opt_data.get("optimized"):
                        # Lucide icon header for Draft v1
                        st.markdown(
                            "<div style='display:flex;align-items:center;gap:10px;margin-bottom:4px;'>"
                            "<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#a1a1aa' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><path d='M14 2v6h6'/><path d='M16 13H8'/><path d='M16 17H8'/><path d='M10 9H8'/></svg>"
                            "<span style='color:#a1a1aa;font-weight:600;font-size:0.9rem;'>Draft v1 &mdash; Original Report</span>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                        with st.expander("View Draft v1"):
                            st.markdown('<div style="padding: 10px; opacity: 0.8;">', unsafe_allow_html=True)
                            st.markdown(strip_fake_links(opt_data.get("original_report", "Original report not available.")))
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Lucide icon header for Draft v2
                        st.markdown(
                            "<div style='display:flex;align-items:center;gap:10px;margin-top:16px;margin-bottom:4px;'>"
                            "<svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#818cf8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3z'/></svg>"
                            "<span style='color:#818cf8;font-weight:600;font-size:0.9rem;'>Draft v2 &mdash; Optimized Final Report</span>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                        with st.expander("View Draft v2 — Optimized", expanded=True):
                            st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)
                            st.markdown(strip_fake_links(st.session_state.full_research))
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        # Lucide icon header for Full Report
                        st.markdown(
                            f"""
                            <div style='margin-top:40px; margin-bottom:20px; padding:20px 24px;
                                        background: linear-gradient(135deg, rgba(52,211,153,0.12) 0%, rgba(6,182,212,0.06) 100%);
                                        border-left: 5px solid #34d399; border-radius: 12px;'>
                                <div style='display:flex; align-items:center; gap:14px;'>
                                    <svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 24 24' fill='none' stroke='#34d399' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z'/><path d='M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z'/></svg>
                                    <div>
                                        <p style='margin:0; font-size:0.75rem; font-weight:700; letter-spacing:0.12em;
                                                  text-transform:uppercase; color:#34d399;'>Section 3</p>
                                        <h2 style='margin:4px 0 0 0; font-size:2rem; font-weight:800; line-height:1.1;
                                                   background: linear-gradient(90deg, #34d399, #06b6d4);
                                                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
                                            Full Comprehensive Research Report
                                        </h2>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        with st.expander("View Full Report", expanded=True):
                            st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)
                            st.markdown(strip_fake_links(st.session_state.full_research))
                            st.markdown('</div>', unsafe_allow_html=True)



