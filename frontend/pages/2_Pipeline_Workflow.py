import streamlit as st
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.shared_theme import apply_shared_theme

st.set_page_config(
    page_title="Nexus | Pipeline Workflow",
    page_icon="🧬",
    layout="wide"
)

# Apply global premium SaaS theme & sidebar widgets
apply_shared_theme()

# Header Section
st.markdown("""
<div class="header-card header-card-workflow">
    <div style="margin-bottom: 12px;">
        <span style="background-color: rgba(59, 130, 246, 0.15); color: #93c5fd; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(59, 130, 246, 0.3);">Pipeline Architecture</span>
    </div>
    <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0; color: #ffffff;">Neural Agent Pipeline Workflow</h1>
    <p style="font-size: 1.05rem; color: #a1a1aa; margin: 8px 0 0 0; line-height: 1.6;">
        Explore the multi-layered agent intelligence execution workflow designed by Nexus.
    </p>
</div>
""", unsafe_allow_html=True)

# Workflow Steps
st.markdown("""
<div class="flow-card">
    <div class="flow-title">
        <div class="flow-step-num">1</div>
        Elite Researcher Agent
    </div>
    <div class="flow-desc">
        Gathers raw research parameters, queries external intelligence databases, retrieves factual reference material, and compiles deep factual data reports on the target research topic.
    </div>
</div>

<div class="flow-card">
    <div class="flow-title">
        <div class="flow-step-num">2</div>
        Executive Summarizer Agent
    </div>
    <div class="flow-desc">
        Processes the vast data sheets compiled by the researcher, highlights core concepts, organizes arguments into elegant layouts, and generates the final executive summary dossier.
    </div>
</div>

<div class="flow-card">
    <div class="flow-title">
        <div class="flow-step-num">3</div>
        AI Critic Agent
    </div>
    <div class="flow-desc">
        Conducts structural validations on the generated content, analyzes argumentative bias, checks completeness of references, and delivers a rigorous critique report.
    </div>
</div>

<div class="flow-card">
    <div class="flow-title">
        <div class="flow-step-num">4</div>
        Memory Manager
    </div>
    <div class="flow-desc">
        Stores all output tokens permanently in ChromaDB vector storage. Ensures future queries have contextual access to completed research history via fast semantic vector lookups.
    </div>
</div>
""", unsafe_allow_html=True)
