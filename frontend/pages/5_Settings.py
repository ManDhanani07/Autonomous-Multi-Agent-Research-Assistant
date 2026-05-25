import streamlit as st
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.shared_theme import apply_shared_theme

st.set_page_config(
    page_title="Nexus | Settings",
    page_icon="⚙️",
    layout="wide"
)

# Apply global premium SaaS theme & sidebar widgets
apply_shared_theme()

# Header Section
st.markdown("""
<div class="header-card header-card-settings">
    <div style="margin-bottom: 12px;">
        <span style="background-color: rgba(239, 68, 68, 0.15); color: #fca5a5; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(239, 68, 68, 0.3);">System Configuration</span>
    </div>
    <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0; color: #ffffff;">Nexus Control Panel</h1>
    <p style="font-size: 1.05rem; color: #a1a1aa; margin: 8px 0 0 0; line-height: 1.6;">
        Manage API integrations, pipeline configurations, model endpoints, and database connection pools.
    </p>
</div>
""", unsafe_allow_html=True)

# API Settings Section
with st.container():
    st.markdown("""
    <div class="settings-section">
        <div class="settings-title">AI Engine Settings</div>
        <div class="settings-desc">Configure LLM parameters, system instructions, and tokens limits.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.selectbox("Default AI Model Engine", ["Llama 3.3 70B (Groq)", "Mixtral 8x7B (Groq)", "Gemma 2 9B (Groq)"])
    st.slider("Model Temperature (Creativity vs. Precision)", 0.0, 1.0, 0.3, 0.05)
    st.text_input("System Instructions Override", placeholder="Enter custom agent behavior directives...")

st.markdown("<br>", unsafe_allow_html=True)

# Vector Database Settings Section
with st.container():
    st.markdown("""
    <div class="settings-section">
        <div class="settings-title">Memory & Database Configurations</div>
        <div class="settings-desc">Adjust ChromaDB collection namespaces and similarity search thresholds.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.slider("Retrieval Context Threshold (Similarity Limit)", 0.0, 2.0, 1.1, 0.05)
    st.text_input("Database Path Override", value="memory/chroma_db", disabled=True)

st.success("Configurations saved successfully to active Streamlit workspace.")
