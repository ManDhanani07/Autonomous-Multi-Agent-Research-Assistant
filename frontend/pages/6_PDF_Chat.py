import os
import sys
import json
import streamlit as st

# Add project root to python path to allow importing backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from frontend.shared_theme import apply_shared_theme
from memory.chroma_store import list_workspaces
from tools.pdf_parser_tool import search_pdf_context
from tools.groq_client import ask_groq


PAGE_TITLE = "Nexus | PDF Chat Assistant"
PAGE_ICON = "📄"


def load_pdf_metadata(workspace: str) -> list[dict]:
    database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "database")
    metadata_file = os.path.join(database_dir, "pdf_metadata.json")

    if not os.path.exists(metadata_file):
        return []

    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            all_metadata = json.load(f)
    except Exception:
        return []

    filtered_metadata = [item for item in all_metadata if item.get("workspace", "default") == workspace]
    return filtered_metadata


def initialize_session_state():
    if "pdf_chat_history" not in st.session_state:
        st.session_state.pdf_chat_history = []
    if "pdf_chat_selected_pdf" not in st.session_state:
        st.session_state.pdf_chat_selected_pdf = None
    if "pdf_chat_latest_context" not in st.session_state:
        st.session_state.pdf_chat_latest_context = ""
    if "pdf_chat_latest_chunks" not in st.session_state:
        st.session_state.pdf_chat_latest_chunks = []
    if "pdf_chat_workspace" not in st.session_state:
        st.session_state.pdf_chat_workspace = st.session_state.get("active_workspace", "default")


def reset_chat():
    st.session_state.pdf_chat_history = []
    st.session_state.pdf_chat_latest_context = ""
    st.session_state.pdf_chat_latest_chunks = []
def build_prompt(question: str, retrieved_context: str, action: str | None = None) -> str:
    action_instructions = ""
    if action == "explain":
        action_instructions = "Please answer in very simple, plain language suitable for a beginner."
    elif action == "notes":
        action_instructions = "Create concise study notes summarizing the important points from the retrieved PDF context."
    elif action == "flashcards":
        action_instructions = "Generate 5 short flashcards with questions and answers based on the retrieved PDF context."
    elif action == "interview":
        action_instructions = "Generate 5 interview-style questions and answers based on the retrieved PDF context."
    elif action == "summary":
        action_instructions = "Create a comprehensive summary of the retrieved PDF context, detailing all key findings, objectives, methodology, and conclusions."

    instructions = (
        "You are an expert PDF research assistant. Use only the retrieved PDF chunks below to answer the user query. "
        "Do not invent facts that are not contained in the context." 
    )

    if action_instructions:
        instructions += " " + action_instructions

    prompt = (
        f"{instructions}\n\n"
        f"Selected PDF: {st.session_state.pdf_chat_selected_pdf or 'Unknown'}\n"
        f"User Question: {question}\n\n"
        "Retrieved PDF Context:\n"
        f"{retrieved_context}\n\n"
        "Answer the question clearly and cite relevant source sections when possible. "
        "If the answer cannot be found, say you could not find the answer in the selected PDF."
    )
    return prompt


def render_source_row(source: dict, index: int = 1) -> str:
    """Renders a formatted source citation card with PDF name, section, and similarity."""
    source_file = source.get("metadata", {}).get("source_file", "Unknown PDF")
    section = source.get("metadata", {}).get("section", "Unknown")
    similarity = source.get("similarity_pct", "0.0%")
    
    # Extract just the filename without path
    if "/" in source_file:
        source_file = source_file.split("/")[-1]
    
    html_card = f"""
    <div style='background: rgba(99, 102, 241, 0.08); border-left: 3px solid rgba(99, 102, 241, 0.5); 
                padding: 12px 14px; margin-bottom: 8px; border-radius: 6px;'>
        <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
            <span style='font-size: 14px;'>📄</span>
            <span style='font-weight: 600; color: #ffffff;'>{source_file}</span>
        </div>
        <div style='display: flex; gap: 16px; font-size: 13px; color: #a1a1aa;'>
            <span>📍 Section: <code style='background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 3px;'>{section}</code></span>
            <span>🎯 Similarity: <code style='background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 3px; color: #818cf8;'>{similarity}</code></span>
        </div>
    </div>
    """
    return html_card


def build_retrieved_context(chunks: list[dict]) -> str:
    lines = []
    for idx, chunk in enumerate(chunks, start=1):
        meta = chunk.get("metadata", {})
        lines.append(
            f"[{idx}] Source: {meta.get('source_file', 'Unknown PDF')} | Section: {meta.get('section', 'Unknown')} | Similarity: {chunk.get('similarity_pct', '0.0%')}"
        )
        lines.append(chunk.get("document", ""))
        lines.append("")
    return "\n".join(lines)


def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
    apply_shared_theme()

    initialize_session_state()

    st.markdown(
        "<div class='header-card header-card-memory'>"
        "<h1 style='font-weight: 700; font-size: 2.6rem; margin-bottom: 10px; color: #ffffff;'>📄 PDF Chat Agent</h1>"
        "<p style='color: #a1a1aa; font-size: 1.05rem; margin: 0;'>"
        "Chat directly with uploaded PDFs using semantic retrieval, then get answers, flashcards, notes, and beginner-level explanations." 
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    workspaces = list_workspaces()
    workspace = st.selectbox(
        "Workspace",
        workspaces,
        index=workspaces.index(st.session_state.pdf_chat_workspace) if st.session_state.pdf_chat_workspace in workspaces else 0
    )
    st.session_state.pdf_chat_workspace = workspace
    pdfs = load_pdf_metadata(workspace)
    pdf_options = [pdf.get("filename", "Unnamed PDF") for pdf in pdfs]

    if pdf_options:
        col_select, col_dl = st.columns([3, 1])
        with col_select:
            selected_pdf = st.selectbox(
                "Select an uploaded PDF",
                pdf_options,
                index=pdf_options.index(st.session_state.pdf_chat_selected_pdf) if st.session_state.pdf_chat_selected_pdf in pdf_options else 0
            )
            st.session_state.pdf_chat_selected_pdf = selected_pdf
            
        with col_dl:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "database")
            pdf_file_path = os.path.join(database_dir, "uploaded_pdfs", selected_pdf)
            if os.path.exists(pdf_file_path):
                try:
                    with open(pdf_file_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_bytes,
                        file_name=selected_pdf,
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception:
                    st.error("Error reading PDF")
            else:
                st.error("File not found")
    else:
        selected_pdf = None
    # Check if selected PDF chunks are indexed in ChromaDB
    db_chunk_count = 0
    if selected_pdf:
        try:
            from memory.chroma_store import get_chroma_client, get_collection_name_for_workspace
            client = get_chroma_client()
            collection_name = get_collection_name_for_workspace(workspace, suffix="_pdfs")
            collection = client.get_collection(name=collection_name)
            results = collection.get(where={"source_file": selected_pdf}, include=[])
            db_chunk_count = len(results.get("ids", []))
        except Exception:
            db_chunk_count = 0

    if selected_pdf and db_chunk_count == 0:
        st.warning(f"⚠️ The document '{selected_pdf}' is not indexed in the active workspace '{workspace}' vector database.")
        database_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "database")
        pdf_file_path = os.path.join(database_dir, "uploaded_pdfs", selected_pdf)
        
        if os.path.exists(pdf_file_path):
            if st.button("🔄 Index Document Chunks", key="index_pdf_now"):
                with st.spinner(f"Parsing and indexing '{selected_pdf}'..."):
                    try:
                        from tools.pdf_parser_tool import ingest_pdf_to_chroma
                        ingest_pdf_to_chroma(pdf_file_path, filename=selected_pdf, workspace=workspace)
                        st.success(f"Successfully indexed '{selected_pdf}' in database!")
                        import time
                        time.sleep(1.0)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to index PDF: {e}")
        else:
            st.error("The source PDF file was not found on disk. Please upload it again on the Home page.")

    st.markdown("---")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Clear Chat", key="clear_pdf_chat"):
            reset_chat()
        st.markdown("<div style='margin-top: 12px; color: #a1a1aa;'>Your PDF chat history is stored only for this session.</div>", unsafe_allow_html=True)
    with col2:
        action_cols = st.columns(5)
        if action_cols[0].button("Explain Simply", key="pdf_chat_explain"):
            st.session_state.pdf_chat_action = "explain"
        if action_cols[1].button("Generate Notes", key="pdf_chat_notes"):
            st.session_state.pdf_chat_action = "notes"
        if action_cols[2].button("Generate Flashcards", key="pdf_chat_flashcards"):
            st.session_state.pdf_chat_action = "flashcards"
        if action_cols[3].button("Generate Interview Questions", key="pdf_chat_interview"):
            st.session_state.pdf_chat_action = "interview"
        if action_cols[4].button("Generate Summary", key="pdf_chat_summary"):
            st.session_state.pdf_chat_action = "summary"

    if not selected_pdf:
        return
    if "last_user_message" not in st.session_state:
        st.session_state.last_user_message = ""

    def add_chat_message(role: str, content: str, sources: list[dict] | None = None):
        st.session_state.pdf_chat_history.append({
            "role": role,
            "content": content,
            "sources": sources or []
        })

    def run_retrieval_and_answer(question: str, action: str | None = None):
        if not selected_pdf:
            st.error("Select a PDF before asking a question.")
            return

        query = question.strip()
        if not query:
            st.warning("Enter a question to chat with the PDF.")
            return

        add_chat_message("user", query)
        st.session_state.last_user_message = query

        metadata_filter = {"source_file": selected_pdf}
        with st.spinner("Retrieving relevant PDF chunks..."):
            _, chunks = search_pdf_context(query, n_results=8, min_similarity=0.20, workspace=workspace, metadata_filter=metadata_filter)

        filtered_chunks = chunks

        if not filtered_chunks:
            add_chat_message("assistant", "I couldn't find relevant content in the selected PDF. Try another question or choose a different PDF.")
            return

        retrieved_context = build_retrieved_context(filtered_chunks)
        st.session_state.pdf_chat_latest_context = retrieved_context
        st.session_state.pdf_chat_latest_chunks = filtered_chunks

        prompt = build_prompt(query, retrieved_context, action)
        with st.spinner("Generating PDF-based answer..."):
            answer = ask_groq(prompt)

        if answer.startswith("⚠️"):
            add_chat_message("assistant", "The AI engine failed to generate an answer. Please try again later.")
            st.error(answer)
            return

        add_chat_message("assistant", answer, sources=filtered_chunks)

    quick_action = st.session_state.get("pdf_chat_action")
    if quick_action:
        st.session_state.pdf_chat_action = None
        # Determine appropriate semantic query for retrieval based on action
        if st.session_state.last_user_message:
            query = st.session_state.last_user_message
        else:
            if quick_action == "summary":
                query = "executive summary abstract introduction methodology main findings conclusions"
            elif quick_action == "explain":
                query = "introduction overview fundamentals summary"
            elif quick_action == "notes":
                query = "key concepts methodology results main contributions summary"
            elif quick_action == "flashcards":
                query = "important terminology definitions key facts summary"
            elif quick_action == "interview":
                query = "core questions concepts definitions findings methodology summary"
            else:
                query = "document overview summary main points"
        
        run_retrieval_and_answer(query, action=quick_action)

    with st.chat_message("system"):
        st.markdown("**PDF Chat is using the selected PDF and retrieved chunks only. Answers are generated from the current PDF context.**")

    for message in st.session_state.pdf_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                st.markdown("**📚 Sources Used:**")
                for idx, source in enumerate(message["sources"], start=1):
                    st.markdown(render_source_row(source, idx), unsafe_allow_html=True)

    if st.session_state.pdf_chat_history:
        with st.expander("📖 Retrieved Context", expanded=False):
            if st.session_state.pdf_chat_latest_chunks:
                for idx, chunk in enumerate(st.session_state.pdf_chat_latest_chunks, start=1):
                    meta = chunk.get("metadata", {})
                    source_file = meta.get("source_file", "Unknown PDF")
                    if "/" in source_file:
                        source_file = source_file.split("/")[-1]
                    
                    st.markdown(
                        f"""<div style='background: rgba(129, 140, 248, 0.08); border: 1px solid rgba(129, 140, 248, 0.2); 
                                   padding: 12px 14px; border-radius: 8px; margin-bottom: 12px;'>
                        <div style='display: flex; gap: 12px; margin-bottom: 8px; font-size: 13px;'>
                            <span style='background: rgba(129, 140, 248, 0.2); color: #818cf8; padding: 4px 8px; border-radius: 4px; font-weight: 600;'>Chunk {idx}</span>
                            <span style='color: #a1a1aa;'>📄 {source_file}</span>
                            <span style='color: #a1a1aa;'>📍 {meta.get('section', 'Unknown')}</span>
                            <span style='color: #818cf8;'>🎯 {chunk.get('similarity_pct', '0.0%')}</span>
                        </div>
                        <div style='background: rgba(255,255,255,0.03); padding: 10px 12px; border-radius: 6px; border-left: 2px solid rgba(129, 140, 248, 0.3); 
                                  color: #e4e4e7; font-size: 13px; line-height: 1.5;'>
                            {chunk.get('document', '')}
                        </div>
                        </div>""",
                        unsafe_allow_html=True
                    )
            else:
                st.info("No retrieved PDF chunks are available for the current conversation.")

    user_question = st.chat_input("Ask this PDF a question...")
    if user_question:
        run_retrieval_and_answer(user_question)


if __name__ == "__main__":
    main()
