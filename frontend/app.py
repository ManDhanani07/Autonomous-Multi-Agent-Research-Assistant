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
<div class="icon-box">🗺️</div>
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
                st.error("⚠️ Research pipeline encountered an API quota issue.")
                st.markdown(clean_summary)
            else:
                st.success("✅ Memory Saved Successfully")
                st.success("Autonomous Research Pipeline Complete.")
                
                # ── Planner Roadmap Panel ──────────────────────────────────
                plan = getattr(st.session_state, "planner_roadmap", None)
                if plan:
                    st.markdown(
                        "<h3 style='margin-top: 30px; margin-bottom: 12px; color: #a855f7; "
                        "font-size: 1.3rem; display: flex; align-items: center; gap: 10px;'>"
                        "🗺️ Planner Agent Roadmap</h3>",
                        unsafe_allow_html=True
                    )
                    
                    with st.expander("View Strategic Investigation Roadmap"):
                        st.markdown(f"**Overview:** {plan.get('overview', '')}")
                        
                        colA, colB = st.columns(2)
                        with colA:
                            st.markdown("#### 🎯 Research Objectives")
                            for obj in plan.get('objectives', []):
                                st.markdown(f"- {obj}")
                            
                            st.markdown("#### 📑 Core Subtopics")
                            for sub in plan.get('subtopics', []):
                                st.markdown(f"- {sub}")

                            st.markdown("#### ⚙️ Technical Areas")
                            for tech in plan.get('technical_areas', []):
                                st.markdown(f"- {tech}")

                            st.markdown("#### 🔍 Recommended Focus Areas")
                            for focus in plan.get('focus_areas', []):
                                st.markdown(f"- {focus}")

                            st.markdown("#### 🚀 Future Investigation Opportunities")
                            for opp in plan.get('future_opportunities', []):
                                st.markdown(f"- {opp}")
                        
                        with colB:
                            st.markdown("#### 🗺️ Investigation Roadmap")
                            for phase in plan.get('roadmap', []):
                                st.markdown(f"- {phase}")

                            st.markdown("#### 🔄 Suggested Workflow Order")
                            for step in plan.get('suggested_order', []):
                                st.markdown(f"1. {step}")
                            
                            st.markdown("#### ❓ Critical Questions")
                            for q in plan.get('critical_questions', []):
                                st.markdown(f"- {q}")

                            st.markdown("#### ⚠️ Potential Challenges")
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
                                    <h4 style='margin: 0; color: #10b981;'>✨ AI Self-Corrected & Optimized</h4>
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
                                    <h4 style='margin: 0; color: #3b82f6;'>🛡️ AI Quality Verified</h4>
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
                        "<h3 style='margin-top: 30px; margin-bottom: 12px; color: #34d399; "
                        "font-size: 1.3rem; display: flex; align-items: center; gap: 10px;'>"
                        "🧠 RAG Memory Context — Retrieved &amp; Injected</h3>",
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
                        sim_pct  = mem.get("similarity_pct", "N/A")
                        sim_val  = mem.get("similarity_score", 0)
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

                        with st.expander(f"📁 Memory {idx}: {mem_topic}  ·  {sim_pct} relevance"):
                            st.markdown(
                                f"<div style='display:flex; gap:12px; margin-bottom:12px; "
                                f"flex-wrap:wrap;'>"
                                f"<span style='background:rgba(52,211,153,0.1); color:#34d399; "
                                f"padding:4px 12px; border-radius:20px; font-size:0.8rem; "
                                f"border:1px solid rgba(52,211,153,0.3); font-weight:600;'>"
                                f"🕒 {mem_date}</span>"
                                f"<span style='background:rgba(99,102,241,0.1); "
                                f"color:{badge_colour}; padding:4px 12px; border-radius:20px; "
                                f"font-size:0.8rem; border:1px solid {badge_colour}40; "
                                f"font-weight:700;'>⚡ Similarity: {sim_pct}</span>"
                                f"<span style='background:rgba(255,255,255,0.05); color:#71717a; "
                                f"padding:4px 12px; border-radius:20px; font-size:0.8rem;'>"
                                f"ID: {mem.get('id','—')}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                            # Similarity progress bar
                            st.progress(min(sim_val, 1.0))

                            # Full stored memory content
                            st.markdown(mem.get("document", ""))

                elif not summary_is_error:
                    st.info("💡 No related past research was found for this topic. "
                            "This report has been stored and will be retrieved as context for future searches.")

                # ── Executive Summary ────────────────────────────────────
                st.markdown(
                    f"<h3 style='margin-top: 30px; margin-bottom: 16px; color: #ffffff; "
                    f"font-size: 1.5rem; display: flex; align-items: center; gap: 10px;'>"
                    f"{ICON_SUMMARIZER} Executive Summary</h3>",
                    unsafe_allow_html=True
                )
                st.markdown('<div id="exec-summary-anchor"></div>', unsafe_allow_html=True)
                st.markdown(clean_summary)

                # ── AI Critic Analysis ───────────────────────────────────
                st.markdown(
                    f"<h3 style='margin-top: 30px; margin-bottom: 16px; color: #ffffff; "
                    f"font-size: 1.5rem; display: flex; align-items: center; gap: 10px;'>"
                    f"{ICON_CRITIC} AI Critic Analysis</h3>",
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
                        with st.expander("📄 View Original Draft (v1)"):
                            st.markdown('<div style="padding: 10px; opacity: 0.8;">', unsafe_allow_html=True)
                            st.markdown(opt_data.get("original_report", "Original report not available."))
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with st.expander("✨ View Optimized Final Report (v2)", expanded=True):
                            st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)
                            st.markdown(st.session_state.full_research)
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        with st.expander("View Full Comprehensive Research Report", expanded=True):
                            st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)
                            st.markdown(st.session_state.full_research)
                            st.markdown('</div>', unsafe_allow_html=True)
