import streamlit as st
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.shared_theme import apply_shared_theme

st.set_page_config(
    page_title="Nexus | Saved Reports",
    page_icon="📁",
    layout="wide"
)

# Apply global premium SaaS theme & sidebar widgets
apply_shared_theme()

# Header Section
st.markdown("""
<div class="header-card header-card-reports">
    <div style="margin-bottom: 12px;">
        <span style="background-color: rgba(167, 139, 250, 0.15); color: #c084fc; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(167, 139, 250, 0.3);">Archived Reports</span>
    </div>
    <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0; color: #ffffff;">Saved Research Reports</h1>
    <p style="font-size: 1.05rem; color: #a1a1aa; margin: 8px 0 0 0; line-height: 1.6;">
        Review previous agent intelligence outputs, summarizations, and critiques.
    </p>
</div>
""", unsafe_allow_html=True)

# Sample reports listing
st.markdown("""
<div class="report-card">
    <div class="report-title">How to build predictable model using ML algorithms?</div>
    <div class="report-meta">Date: May 20, 2026 | Engine: Groq Llama 3.3 70B</div>
    <div class="report-summary">
        Comprehensive analysis on selecting ML algorithms, data preprocessing strategies, hyperparameter optimization protocols, and feature engineering to maximize predictability.
    </div>
</div>

<div class="report-card">
    <div class="report-title">AI is harmful?</div>
    <div class="report-meta">Date: May 16, 2026 | Engine: Groq Llama 3.3 70B</div>
    <div class="report-summary">
        An in-depth debate investigating systemic bias, cybersecurity risks, autonomous decision-making alignment issues, alongside economic disruption vs productivity benefits.
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("Review more deep-retrieved documents directly in the AI Memory Bank page.")
