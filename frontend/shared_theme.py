import streamlit as st
import base64
import re
import threading
import time

@st.cache_resource
def _prewarm_chromadb():
    """
    Spawns a daemon background thread that fully initializes ChromaDB AND
    loads the sentence-transformers embedding model into memory at startup.

    Previously only get_chroma_client() was called, which skipped loading the
    'all-MiniLM-L6-v2' model weights (~103 tensors). That meant the first
    memory save was slow because it had to load the model on-demand.
    Now initialize_chroma() is called instead, which loads everything up front.
    """
    def warm():
        try:
            print("[*] Background ChromaDB pre-warming thread started...")
            # initialize_chroma() loads BOTH the ChromaDB client AND the
            # sentence-transformers embedding model — eliminating the delay
            # that previously appeared during the first memory save.
            from memory.chroma_store import initialize_chroma
            initialize_chroma()
            print("[*] Background ChromaDB pre-warming completed successfully.")
        except Exception as e:
            print(f"[*] Background ChromaDB pre-warming error: {e}")

    thread = threading.Thread(target=warm, daemon=True)
    thread.start()

def apply_shared_theme():
    # Warm up ChromaDB in a background thread at startup
    _prewarm_chromadb()

    # Lucide Icons (Inline SVGs)
    ICON_NETWORK = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/></svg>'
    ICON_SERVER = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></svg>'
    ICON_CPU = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>'
    ICON_DATABASE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>'

    # Define the complete, unified CSS rules for the entire app.
    unified_css = """
/* Smooth entry animation for the main page content area */
@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}
section[data-testid="stMain"] {
    animation: pageFadeIn 0.3s ease-out forwards !important;
}

/* Prevent Streamlit's default entry slide-up animations from causing layout jumps */
[data-testid="stElementContainer"] {
    animation: none !important;
}

/* Hide skeleton loaders, status indicators, and header decorations to prevent layout jumps/popping */
[data-testid="stSkeleton"] {
    display: none !important;
}
div[data-testid="stDecoration"] {
    display: none !important;
}
div[data-testid="stStatusWidget"] {
    display: none !important;
}
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    background-color: #09090b !important;
    color: #f4f4f5 !important;
}
.stApp {
    background-image: radial-gradient(circle at top center, rgba(99, 102, 241, 0.05) 0%, transparent 70%) !important;
}
p, h1, h2, h3, h4, h5, h6, li, a, span, div, button, input {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

/* Sidebar container styling */
[data-testid="stSidebar"] {
    background-color: #18181b !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}
/* Force typography in the sidebar list of pages */
[data-testid="stSidebar"] *:not(i):not([class*="icon"]):not([class*="stIcon"]):not([data-testid*="stIcon"]):not([data-testid="collapsedControl"]):not([data-testid="collapsedControl"] *) {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}
/* Fix page link text colors in Streamlit navigation */
[data-testid="stSidebarNav"] a span {
    color: #a1a1aa !important;
    font-size: 0.95rem;
    font-weight: 500;
}
[data-testid="stSidebarNav"] a[aria-current="page"] span {
    color: #ffffff !important;
    font-weight: 600;
}

/* Global button design */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    border: none;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1.05rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
    transform: translateY(-1px);
}

/* Ensure Streamlit material icons aren't broken */
i, .material-icons, .material-symbols-rounded, [class*="icon"], [class*="stIcon"], [data-testid*="stIcon"], [data-testid="collapsedControl"] * {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}
/* Force sidebar collapse/expand toggle controls to remain visible at all times */
[data-testid="collapsedControl"],
[data-testid="stBaseButton-headerNoPadding"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] button,
button[class*="sidebar-collapse"] {
    opacity: 1 !important;
    visibility: visible !important;
}

/* Premium Header Cards */
.header-card {
    border-radius: 16px;
    padding: 40px;
    margin-bottom: 30px;
}
.header-card-dashboard {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(192, 132, 252, 0.05) 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
}
.header-card-workflow {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
    border: 1px solid rgba(59, 130, 246, 0.2);
}
.header-card-reports {
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.1) 0%, rgba(192, 132, 252, 0.05) 100%);
    border: 1px solid rgba(167, 139, 250, 0.2);
}
.header-card-memory {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.05) 100%);
    border: 1px solid rgba(16, 185, 129, 0.2);
}
.header-card-settings {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(244, 63, 94, 0.05) 100%);
    border: 1px solid rgba(239, 68, 68, 0.2);
}

/* Dashboard Page Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}
.metric-card {
    background: rgba(24, 24, 27, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.3);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff;
    margin: 8px 0;
}
.metric-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #71717a;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-delta {
    font-size: 0.85rem;
    font-weight: 500;
    color: #10b981;
}

/* Pipeline Workflow Page Cards */
.flow-card {
    background: rgba(24, 24, 27, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 20px;
}
.flow-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.flow-desc {
    font-size: 0.95rem;
    color: #d4d4d8;
    line-height: 1.6;
}
.flow-step-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid #3b82f6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: bold;
    color: #60a5fa;
}

/* Saved Reports Page Cards */
.report-card {
    background: rgba(24, 24, 27, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}
.report-card:hover {
    border-color: rgba(167, 139, 250, 0.3);
    transform: translateX(4px);
}
.report-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 8px;
}
.report-meta {
    font-size: 0.85rem;
    color: #71717a;
    margin-bottom: 12px;
}
.report-summary {
    font-size: 0.95rem;
    color: #d4d4d8;
    line-height: 1.6;
}

/* Memory Tag (Memory Bank Page) */
.memory-tag {
    display: inline-block;
    background: rgba(167, 139, 250, 0.15);
    color: #a78bfa;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 8px;
    border: 1px solid rgba(167, 139, 250, 0.3);
}

/* Settings Page Components */
.settings-section {
    background: rgba(24, 24, 27, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 24px;
}
.settings-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 8px;
}
.settings-desc {
    font-size: 0.9rem;
    color: #71717a;
    margin-bottom: 20px;
}

/* Premium Card Container - Hardware Accelerated Animation (Homepage) */
.card-container {
    position: relative;
    border-radius: 16px;
    padding: 40px;
    margin-bottom: 24px;
    background: #18181b;
    box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5);
    z-index: 1;
    overflow: hidden;
}
.card-container::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%; bottom: -50%; right: -50%;
    background: conic-gradient(from 0deg, transparent 75%, #818cf8 85%, #c084fc 100%);
    z-index: -2;
    animation: spin-border 4s linear infinite;
    transform-origin: center center;
    will-change: transform;
}
.card-container::after {
    content: '';
    position: absolute;
    inset: 2px;
    background-color: #18181b;
    border-radius: 14px;
    z-index: -1;
}
@keyframes spin-border {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Workflow Cards Custom CSS (Homepage) */
.workflow-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    margin-top: 20px;
    margin-bottom: 30px;
}
.workflow-card {
    display: flex;
    align-items: center;
    gap: 16px;
    background: rgba(24, 24, 27, 0.65);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px 24px;
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
}
.workflow-card .icon-box {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    color: #71717a;
    transition: all 0.4s ease;
}
.workflow-card .content {
    flex: 1;
}
.workflow-card .title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #a1a1aa;
    margin-bottom: 4px;
    transition: all 0.4s ease;
}
.workflow-card .status {
    font-size: 0.9rem;
    color: #52525b;
    transition: all 0.4s ease;
}
.workflow-card.active {
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
    transform: translateX(10px);
}
.workflow-card.active .icon-box {
    background: rgba(99, 102, 241, 0.15);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.3);
    animation: pulse-icon 2s infinite;
}
.workflow-card.active .title {
    color: #ffffff;
}
.workflow-card.active .status {
    color: #818cf8;
}
.workflow-card.completed {
    border-color: rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.02);
}
.workflow-card.completed .icon-box {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
}
.workflow-card.completed .title {
    color: #e4e4e7;
}
.workflow-card.completed .status {
    color: #10b981;
}
.workflow-card.failed {
    border-color: rgba(239, 68, 68, 0.3);
    background: rgba(239, 68, 68, 0.02);
}
.workflow-card.failed .icon-box {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}
.workflow-card.failed .title {
    color: #e4e4e7;
}
.workflow-card.failed .status {
    color: #ef4444;
}
@keyframes pulse-icon {
    0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
    100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
}

/* Output Containers & Glassmorphism */
.glass-card {
    background: rgba(24, 24, 27, 0.65) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 40px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    margin-bottom: 24px;
    position: relative;
    line-height: 1.8;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167, 139, 250, 0.5), transparent);
}
.glass-card p, .glass-card li {
    color: #d4d4d8;
    font-size: 1.1rem;
}
.glass-card h1, .glass-card h2, .glass-card h3 {
    color: #ffffff;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 10px;
    margin-bottom: 20px;
    margin-top: 30px;
}

/* Target the exact markdown container after our anchor using CSS :has() */
div[data-testid="stMarkdownContainer"]:has(#exec-summary-anchor) + div[data-testid="stMarkdownContainer"],
div[data-testid="stMarkdownContainer"]:has(#critic-anchor) + div[data-testid="stMarkdownContainer"] {
    background: rgba(24, 24, 27, 0.65) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 40px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    margin-bottom: 24px;
    position: relative;
    line-height: 1.8;
}
div[data-testid="stMarkdownContainer"]:has(#exec-summary-anchor) + div[data-testid="stMarkdownContainer"]::before,
div[data-testid="stMarkdownContainer"]:has(#critic-anchor) + div[data-testid="stMarkdownContainer"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167, 139, 250, 0.5), transparent);
}

/* Expanders */
[data-testid="stExpander"] {
    background: rgba(24, 24, 27, 0.4) !important;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    margin-bottom: 12px;
}
[data-testid="stExpanderDetails"] {
    background: rgba(0, 0, 0, 0.2);
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding: 24px !important;
    color: #d4d4d8;
    line-height: 1.8;
}

/* TextInput Styling override */
.stTextInput > div > div > input {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    background-color: #09090b;
    border: 1px solid #27272a;
    color: #ffffff;
    border-radius: 10px;
    padding: 14px;
    font-size: 1.05rem;
    transition: all 0.3s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

/* Hide Streamlit Header Anchor Links & Hints */
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { display: none !important; }
[data-testid="InputInstructions"] { display: none !important; }

/* Hide invisible iframe containers for theme/font script injections to prevent layout shifting */
iframe,
div[data-testid="stHtml"]:has(iframe),
div[data-testid="stIframe"],
div[data-testid="stIframe"] iframe,
div[data-testid="element-container"]:has(iframe),
div[data-testid="element-container"]:has(div[data-testid="stIframe"]) {
    display: none !important;
    height: 0px !important;
    width: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
    border: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
}
"""

    # Encode CSS into Base64 to prevent any quote/escaped char mismatch breaking the HTML tag attributes
    b64_css = base64.b64encode(unified_css.encode('utf-8')).decode('utf-8')

    # Safe iframe/window-parent styling injection.
    # We use st.iframe to execute custom javascript inside a same-origin iframe.
    # The script accesses window.parent.document to apply global styling and font link elements
    # directly to the parent document's head, which persists across page changes.
    js_code = f"""
    <script>
        try {{
            var parentDoc = window.parent.document || document;
            if (!parentDoc.getElementById('nexus-google-fonts')) {{
                var link1 = parentDoc.createElement('link');
                link1.rel = 'preconnect';
                link1.href = 'https://fonts.googleapis.com';
                parentDoc.head.appendChild(link1);
                
                var link2 = parentDoc.createElement('link');
                link2.rel = 'preconnect';
                link2.href = 'https://fonts.gstatic.com';
                link2.crossOrigin = 'anonymous';
                parentDoc.head.appendChild(link2);
                
                var link3 = parentDoc.createElement('link');
                link3.id = 'nexus-google-fonts';
                link3.rel = 'stylesheet';
                link3.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap';
                parentDoc.head.appendChild(link3);
            }}
            
            var styleEl = parentDoc.getElementById('nexus-global-theme');
            if (!styleEl) {{
                styleEl = parentDoc.createElement('style');
                styleEl.id = 'nexus-global-theme';
                parentDoc.head.appendChild(styleEl);
            }}
            styleEl.textContent = atob('{b64_css}');
        }} catch (err) {{
            console.error("Parent style injection failed:", err);
        }}
    </script>
    """

    st.iframe(js_code, height=1)

    # Render the unified sidebar structure
    with st.sidebar:
        st.markdown(f"<h2 style='display: flex; align-items: center; gap: 10px; color: #ffffff;'>{ICON_NETWORK} NEXUS ENGINE</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Initialize session state for workspace if not exists
        if "active_workspace" not in st.session_state:
            st.session_state.active_workspace = "default"

        # Workspace selector section
        st.markdown("<span style='font-size: 0.85rem; font-weight: 600; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em;'>Active Workspace</span>", unsafe_allow_html=True)
        # Active workspace badge
        st.markdown(
            f"<div style='margin-top: 8px; margin-bottom: 12px; display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; background: rgba(99, 102, 241, 0.15); color: #818cf8; border-radius: 20px; border: 1px solid rgba(99, 102, 241, 0.25); font-weight: 600; font-size: 0.85rem;'>"
            f"<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z'/></svg> {st.session_state.active_workspace.upper()}</div>",
            unsafe_allow_html=True
        )

        from memory.chroma_store import list_workspaces, initialize_chroma
        try:
            workspaces = list_workspaces()
        except Exception:
            workspaces = ["default"]

        if st.session_state.active_workspace not in workspaces:
            workspaces.append(st.session_state.active_workspace)
            workspaces = sorted(list(set(workspaces)))

        # Workspace Selector dropdown
        selected_ws = st.selectbox(
            "Switch Workspace",
            options=workspaces,
            index=workspaces.index(st.session_state.active_workspace),
            key="workspace_select_dropdown_widget",
            label_visibility="collapsed"
        )
        if selected_ws != st.session_state.active_workspace:
            st.session_state.active_workspace = selected_ws
            st.rerun()

        # Create Workspace Option
        st.markdown("<span style='font-size: 0.75rem; font-weight: 600; color: #52525b; text-transform: uppercase; letter-spacing: 0.05em;'>Create Workspace</span>", unsafe_allow_html=True)
        new_ws = st.text_input(
            "New workspace name",
            placeholder="e.g. biology_project",
            key="workspace_create_text_input_widget",
            label_visibility="collapsed"
        )
        if st.button("Create", key="workspace_create_button_widget"):
            if new_ws.strip():
                clean_ws = new_ws.strip()
                try:
                    initialize_chroma(workspace=clean_ws)
                    st.session_state.active_workspace = clean_ws
                    st.success(f"Workspace '{clean_ws}' created!")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Name cannot be empty.")

        st.markdown("---")
        
        # System Status
        st.markdown(f"""
            <div style="margin-bottom: 24px;">
                <span style="font-size: 0.85rem; font-weight: 600; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em;">System Status</span><br>
                <div style="margin-top: 8px; display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; background: rgba(16, 185, 129, 0.1); color: #34d399; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.2); font-weight: 600; font-size: 0.85rem;">
                    {ICON_SERVER} ONLINE
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # AI Model Interface
        st.markdown(f"""
            <div style="margin-bottom: 24px;">
                <span style="font-size: 0.85rem; font-weight: 600; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em;">AI Model Interface</span><br>
                <div style="margin-top: 8px; display: inline-flex; align-items: center; gap: 8px; color: #e4e4e7; font-weight: 500; font-size: 0.95rem;">
                    <span style="color: #a1a1aa;">{ICON_CPU}</span> Llama 3.3 70B
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Active Agents Pipeline
        st.markdown(f"""
            <div style="margin-bottom: 24px;">
                <span style="font-size: 0.85rem; font-weight: 600; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em;">Neural Pipeline</span><br>
                <div style="margin-top: 12px; padding-left: 8px; border-left: 2px solid rgba(99, 102, 241, 0.3);">
                    <div style="margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <div style="width: 24px; height: 24px; border-radius: 50%; background: rgba(99, 102, 241, 0.2); border: 1px solid #6366f1; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; color: #818cf8;">1</div>
                        <span style="color: #e0e7ff; font-weight: 500; font-size: 0.95rem;">Elite Researcher</span>
                    </div>
                    <div style="margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <div style="width: 24px; height: 24px; border-radius: 50%; background: rgba(192, 132, 252, 0.2); border: 1px solid #c084fc; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; color: #c084fc;">2</div>
                        <span style="color: #f3e8ff; font-weight: 500; font-size: 0.95rem;">Exec Summarizer</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 24px; height: 24px; border-radius: 50%; background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; color: #34d399;">3</div>
                        <span style="color: #d1fae5; font-weight: 500; font-size: 0.95rem;">AI Critic</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # AI Memory System Status
        st.markdown(f"""
            <div style="margin-bottom: 24px;">
                <span style="font-size: 0.85rem; font-weight: 600; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;">
                    {ICON_DATABASE} AI Memory System
                </span>
                <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: #a1a1aa;">
                        <span style="color: #10b981; font-size: 1.2rem;">•</span> ChromaDB Active
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: #a1a1aa;">
                        <span style="color: #10b981; font-size: 1.2rem;">•</span> Semantic Retrieval Enabled
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: #a1a1aa;">
                        <span style="color: #10b981; font-size: 1.2rem;">•</span> Long-Context Memory Active
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("© 2026 Nexus Labs | Multi-Agent OS")
