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
    """Generates the HTML for the workflow pipeline based on the current step (1 to 5)"""
    
    def get_state(step_id):
        if step_id < current_step: return "completed"
        if step_id == current_step: return "active"
        return "pending"
    
    def get_status_text(step_id, default_text, active_text):
        if step_id < current_step: return "Completed"
        if step_id == current_step: return active_text
        return default_text

    if current_step == 5:
        s1, s2, s3, s4, s5 = "completed", "completed", "completed", "completed", "completed"
        t1, t2, t3, t4, t5 = "Completed", "Completed", "Completed", "Completed", "Pipeline Finished"
    else:
        s1 = get_state(1)
        s2 = get_state(2)
        s3 = get_state(3)
        s4 = get_state(4)
        s5 = "pending"
        t1 = get_status_text(1, "Awaiting execution", "Connecting to Groq Llama 3.3 70B...")
        t2 = get_status_text(2, "Awaiting execution", "Executing...")
        t3 = get_status_text(3, "Awaiting execution", "Analyzing...")
        t4 = get_status_text(4, "Awaiting execution", "Evaluating research...")
        t5 = "Awaiting execution"

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

<!-- Step 2: Researcher -->
<div class="workflow-card {s2}">
<div class="icon-box">{ICON_RESEARCHER}</div>
<div class="content">
<div class="title">Phase 1: Elite Researcher Agent</div>
<div class="status">{t2}</div>
</div>
</div>

<!-- Step 3: Summarizer -->
<div class="workflow-card {s3}">
<div class="icon-box">{ICON_SUMMARIZER}</div>
<div class="content">
<div class="title">Phase 2: Executive Summarizer Agent</div>
<div class="status">{t3}</div>
</div>
</div>

<!-- Step 4: Critic -->
<div class="workflow-card {s4}">
<div class="icon-box">{ICON_CRITIC}</div>
<div class="content">
<div class="title">Phase 3: AI Critic Agent</div>
<div class="status">{t4}</div>
</div>
</div>

<!-- Step 5: Complete -->
<div class="workflow-card {s5}">
<div class="icon-box">{ICON_CHECK}</div>
<div class="content">
<div class="title">Autonomous Research Pipeline Complete</div>
<div class="status">{t5}</div>
</div>
</div>
</div>
"""
    workflow_ui.markdown(html, unsafe_allow_html=True)


if initiate_btn:
    if not topic.strip():
        st.warning("Please provide a valid research topic to begin.")
    else:
        st.session_state.running = True
        st.session_state.topic = topic
        st.session_state.full_research = None
        st.session_state.executive_summary = None
        st.session_state.critique_analysis = None

if getattr(st.session_state, 'running', False):
    if not st.session_state.full_research:
        # Step 1: Initialize
        render_workflow_step(1)
        # Import heavy agent modules and memory manager dynamically during initialization
        from agents.researcher_agent import generate_research
        from agents.summarizer_agent import summarize_research
        from agents.critic_agent import critique_research
        from memory.memory_manager import save_complete_research
        time.sleep(1)
        
        # Step 2: Researcher Agent
        render_workflow_step(2)
        st.session_state.full_research = generate_research(st.session_state.topic)
        
        # Step 3: Summarizer Agent
        render_workflow_step(3)
        st.session_state.executive_summary = summarize_research(st.session_state.full_research)
        
        # Step 4: Critic Agent
        render_workflow_step(4)
        st.session_state.critique_analysis = critique_research(st.session_state.full_research, st.session_state.executive_summary)
        
        # Step 5: Complete
        render_workflow_step(5)
        time.sleep(0.5)
        
        # Save to memory system in a background thread to avoid blocking the UI
        def save_memory_background(topic, research, summary, critique):
            try:
                from memory.memory_manager import save_complete_research
                save_complete_research(topic, research, summary, critique)
                print("[*] Background memory save completed successfully.")
            except Exception as e:
                print(f"Memory System Error: {e}")
                
        # Start the background thread
        thread = threading.Thread(
            target=save_memory_background, 
            args=(st.session_state.topic, st.session_state.full_research, st.session_state.executive_summary, st.session_state.critique_analysis)
        )
        thread.start()
            
        # Clear the workflow UI immediately
        workflow_ui.empty()
        
        # Force Streamlit to rerun and display the output instantly
        st.rerun()
        
    # Render Output from Session State
    if st.session_state.executive_summary and st.session_state.critique_analysis:
        # Remove redundant headings from LLM output
        clean_summary = st.session_state.executive_summary.replace("## Executive Summary", "").strip()
        clean_critique = st.session_state.critique_analysis.replace("# AI Critic Analysis", "").strip()
        
        with output_ui.container():
            st.success("✅ Memory Saved Successfully")
            st.success("Autonomous Research Pipeline Complete.")
            
            st.markdown(f"<h3 style='margin-top: 30px; margin-bottom: 16px; color: #ffffff; font-size: 1.5rem; display: flex; align-items: center; gap: 10px;'>{ICON_SUMMARIZER} Executive Summary</h3>", unsafe_allow_html=True)
            
            # Use an anchor and CSS :has() to style the exact next markdown container perfectly
            st.markdown('<div id="exec-summary-anchor"></div>', unsafe_allow_html=True)
            st.markdown(clean_summary)
            
            st.markdown(f"<h3 style='margin-top: 30px; margin-bottom: 16px; color: #ffffff; font-size: 1.5rem; display: flex; align-items: center; gap: 10px;'>{ICON_CRITIC} AI Critic Analysis</h3>", unsafe_allow_html=True)
            
            st.markdown('<div id="critic-anchor"></div>', unsafe_allow_html=True)
            st.markdown(clean_critique)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.expander("View Full Comprehensive Research Report"):
                st.markdown('<div style="padding: 10px;">', unsafe_allow_html=True)
                st.markdown(st.session_state.full_research)
                st.markdown('</div>', unsafe_allow_html=True)
