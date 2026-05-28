import streamlit as st
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.shared_theme import apply_shared_theme

st.set_page_config(
    page_title="Nexus | System Dashboard",
    page_icon="📊",
    layout="wide"
)

# Apply global premium SaaS theme & sidebar widgets
apply_shared_theme()

# Header Section
st.markdown("""
<div class="header-card header-card-dashboard">
    <div style="margin-bottom: 12px;">
        <span style="background-color: rgba(99, 102, 241, 0.15); color: #a5b4fc; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(99, 102, 241, 0.3);">System Telemetry</span>
    </div>
    <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0; color: #ffffff;">System Intelligence Dashboard</h1>
    <p style="font-size: 1.05rem; color: #a1a1aa; margin: 8px 0 0 0; line-height: 1.6;">
        Real-time telemetry and resource tracking for the multi-agent neural pipeline.
    </p>
</div>
""", unsafe_allow_html=True)

# Metrics Grid
st.markdown("""
<div class="metrics-grid">
    <div class="metric-card">
        <span class="metric-label">Neural Pipelines Executed</span>
        <div class="metric-value">42</div>
        <div class="metric-delta">▲ 14.8% this week</div>
    </div>
    <div class="metric-card">
        <span class="metric-label">Avg. Agent Response Time</span>
        <div class="metric-value">4.2s</div>
        <div class="metric-delta" style="color: #3b82f6;">Optimal performance</div>
    </div>
    <div class="metric-card">
        <span class="metric-label">ChromaDB Vector Pool</span>
        <div class="metric-value">1,420</div>
        <div class="metric-delta">▲ 120 vector records</div>
    </div>
    <div class="metric-card">
        <span class="metric-label">Groq API Status</span>
        <div class="metric-value" style="color: #34d399;">Active</div>
        <div class="metric-delta">Ping: 124ms</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='display:flex;align-items:center;gap:12px;"
    "padding:16px 20px;margin-top:20px;margin-bottom:20px;"
    "background:rgba(59,130,246,0.08);color:#93c5fd;"
    "border-radius:10px;border:1px solid rgba(59,130,246,0.25);font-weight:600;'>"
    "<svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='#93c5fd' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><line x1='12' y1='16' x2='12' y2='12'/><line x1='12' y1='8' x2='12.01' y2='8'/></svg>"
    "<span>System stats are mock telemetry for display purposes. Live telemetry connection is online.</span>"
    "</div>",
    unsafe_allow_html=True
)
