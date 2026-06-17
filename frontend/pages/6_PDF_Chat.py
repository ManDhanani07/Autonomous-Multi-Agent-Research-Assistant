import os
import sys
import json
import re
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


def clean_academic_citations(text: str) -> str:
    """Strips bracketed academic citations, figure references, PDF headers/footers, linebreaks, and trims to complete sentences."""
    if not text:
        return ""
    
    # 1. Merge hyphenated words across lines (e.g., momen-\ntum -> momentum)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # 2. Replace single newlines with spaces, keeping double newlines for paragraph separation
    paragraphs = text.split("\n\n")
    cleaned_paragraphs = []
    for para in paragraphs:
        para_clean = re.sub(r'\s*\n\s*', ' ', para)
        cleaned_paragraphs.append(para_clean.strip())
    text = "\n\n".join([p for p in cleaned_paragraphs if p])
    
    # 3. Remove license text block (e.g. © 2024 The Authors. This work is licensed under...)
    text = re.sub(r'©\s*\d+\s+The\s+Authors\..*?License\.', '', text, flags=re.IGNORECASE)
    text = re.sub(r'https?://[^\s]*creativecommons\.org[^\s]*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'For\s+more\s+information,\s*(?:see)?\s*', '', text, flags=re.IGNORECASE)
    
    # 4. Remove volume and journal header markers
    text = re.sub(r'VOLUME\s*\d+\s*,\s*\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'KOH\s+ET\s+AL\.:.*?(?:AUGUST|2024)\)?', '', text, flags=re.IGNORECASE)
    
    # 5. Remove standalone page numbers (typically 3 digits like 204 or 205)
    text = re.sub(r'\b\d{3}\b', '', text)

    # 6. Remove bracketed citation markers (e.g., [1], [2], [1, 2], [1-3], [12, 15])
    text = re.sub(r'\[\s*\d+(?:[\s,,-]*\d+)*\s*\]', '', text)
    
    # 7. Remove figure/table/section references (e.g., Fig. 1, Fig 2, Figure 3, Table 2, Fig. 2a, FIGURE 4)
    text = re.sub(r'\b(?:[Ff]ig(?:\.|s)?|[Ff]igure[s]?|[Tt]able[s]?|[Ff]igures|[Cc]hapter[s]?)\s*\d+[a-zA-Z]?\.?', '', text)
    text = re.sub(r'\b(?:FIGURE[s]?|FIG(?:\.|s)?|TABLE[s]?)\s*\d+[a-zA-Z]?\.?', '', text)
    
    # 8. Clean up spacing and punctuation issues arising from deletion
    text = re.sub(r'\(\s*\)', '', text)  # remove empty parentheses
    text = re.sub(r'\b\s+,\s*', ', ', text)
    text = re.sub(r'\b\s+\.\s*', '. ', text)
    text = re.sub(r'\s+,\s*', ', ', text)
    text = re.sub(r'\s+\.\s*', '. ', text)
    
    # Remove multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # 9. Trim leading and trailing incomplete sentence fragments
    # Trim leading
    starts_with_capital = bool(re.match(r'^\s*[A-Z]', text))
    matches = list(re.finditer(r'[.!?]\s+([A-Z])', text))
    if not starts_with_capital and matches:
        first_match = matches[0]
        start_idx = first_match.start(1)
        text = text[start_idx:]
    elif not starts_with_capital and not matches:
        cap_match = re.search(r'[A-Z]', text)
        if cap_match:
            text = text[cap_match.start():]
            
    # Trim trailing
    last_terminator_match = list(re.finditer(r'[.!?](?:\s|$)', text))
    if last_terminator_match:
        last_match = last_terminator_match[-1]
        end_idx = last_match.end()
        text = text[:end_idx]
        
    return text.strip()


def clean_assistant_response(text: str) -> str:
    """Strips citation brackets and figure references from LLM responses, formatting Q&A headers and preserving spacing/newlines."""
    if not text:
        return ""
        
    # Remove bracketed academic citation markers (e.g., [1], [2], [1, 2], [1-3], [12, 15])
    text = re.sub(r'\[\s*\d+(?:[\s,,-]*\d+)*\s*\]', '', text)
    
    # Remove figure/table/section references (e.g., Fig. 1, Fig 2, Figure 3, Table 2, Fig. 2a, FIGURE 4)
    text = re.sub(r'\b(?:[Ff]ig(?:\.|s)?|[Ff]igure[s]?|[Tt]able[s]?|[Ff]igures|[Cc]hapter[s]?)\s*\d+[a-zA-Z]?\.?', '', text)
    text = re.sub(r'\b(?:FIGURE[s]?|FIG(?:\.|s)?|TABLE[s]?)\s*\d+[a-zA-Z]?\.?', '', text)
    
    # Clean up empty parentheses
    text = re.sub(r'\(\s*\)', '', text)
    
    # Strip any leading titles/headers (e.g. "Summary", "Study Notes", "Flashcards", etc.)
    # to avoid duplication when we prepend our custom styled headers
    text = re.sub(r'^(?:#+|\*?\*?)\s*(?:Summary|Notes|Study Notes|Flashcards|Interview Questions|Interview|Explanation|Beginner-Friendly Explanation)\s*\*?\*?\s*\n+', '', text, flags=re.IGNORECASE)
    
    # Strip any list numbers/bullets that prefix the Q: / Question: (e.g. "1. Q:" or "1. **Q:**" or "- **Q:**")
    text = re.sub(r'(?:^|\n)\s*(?:\d+[\.\)]|[-*+])\s*(?=\**(?:Q|Question)\**\s*:)', '\n', text, flags=re.IGNORECASE)
    
    # Standardize Q/Question and A/Answer headers (case-insensitive) to Q: and A:
    text = re.sub(r'\*\*\s*(Q|Question)\s*:\s*\*\*', 'Q:', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*\s*(Q|Question)\s*\*\*:', 'Q:', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(Q|Question):', 'Q:', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\*\*\s*(A|Answer)\s*:\s*\*\*', 'A:', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*\s*(A|Answer)\s*\*\*:', 'A:', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(A|Answer):', 'A:', text, flags=re.IGNORECASE)
    
    # Clean up any potential markdown bullet lists or numbers followed immediately by Q: or A:
    # to avoid double nesting, and ensure clean line breaks
    text = re.sub(r'\s*\bQ:\s*', '\n\n**Q:** ', text)
    text = re.sub(r'\s*\bA:\s*', '\n\n**A:** ', text)
    
    # Clean up multiple spaces on a single line but preserve newlines
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line_clean = re.sub(r' {2,}', ' ', line)
        cleaned_lines.append(line_clean)
    text = "\n".join(cleaned_lines)
    
    # Normalize multiple newlines to max double newlines for clean spacing
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def render_grouped_sources(sources: list[dict]) -> str:
    """Renders formatted source citation cards grouped by unique PDF files."""
    if not sources:
        return ""
        
    grouped = {}
    for source in sources:
        meta = source.get("metadata", {})
        source_file = meta.get("source_file", "Unknown PDF")
        if "/" in source_file:
            source_file = source_file.split("/")[-1]
        elif "\\" in source_file:
            source_file = source_file.split("\\")[-1]
            
        section = meta.get("section", "Unknown")
        sim_pct = source.get("similarity_pct", "0.0%")
        try:
            sim_val = float(sim_pct.replace("%", ""))
        except ValueError:
            sim_val = 0.0
            
        if source_file not in grouped:
            grouped[source_file] = {
                "sections": {section},
                "max_similarity_val": sim_val,
                "max_similarity_str": sim_pct,
                "parts_count": 1
            }
        else:
            grouped[source_file]["sections"].add(section)
            grouped[source_file]["parts_count"] += 1
            if sim_val > grouped[source_file]["max_similarity_val"]:
                grouped[source_file]["max_similarity_val"] = sim_val
                grouped[source_file]["max_similarity_str"] = sim_pct

    html_cards = []
    for filename, info in grouped.items():
        sections_str = ", ".join(sorted(list(info["sections"])))
        parts_count = info["parts_count"]
        similarity = info["max_similarity_str"]
        
        html_card = f"""
        <div style='background: rgba(99, 102, 241, 0.08); border-left: 3px solid rgba(99, 102, 241, 0.5); 
                    padding: 12px 14px; margin-bottom: 8px; border-radius: 6px;'>
            <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                <span style='font-size: 14px;'>📄</span>
                <span style='font-weight: 600; color: #ffffff;'>{filename}</span>
            </div>
            <div style='display: flex; gap: 16px; font-size: 13px; color: #a1a1aa;'>
                <span>📚 Parts: <strong style='color: #ffffff;'>{"1-" + str(parts_count) if parts_count > 1 else "1"}</strong></span>
                <span>📍 Sections: <code style='background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 3px;'>{sections_str}</code></span>
                <span>🎯 Similarity: <code style='background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 3px; color: #818cf8;'>{similarity}</code></span>
            </div>
        </div>
        """
        html_cards.append(html_card)
        
    return "\n".join(html_cards)


def build_prompt(question: str, retrieved_context: str, action: str | None = None) -> str:
    action_instructions = ""
    if action == "explain":
        action_instructions = "Please answer in very simple, plain language suitable for a beginner. Do not include any main title or header in your response."
    elif action == "notes":
        action_instructions = "Create concise study notes summarizing the important points from the retrieved PDF context. Do not include any main title or header in your response."
    elif action == "flashcards":
        action_instructions = (
            "Generate 5 short flashcards based on the retrieved PDF context. "
            "Format each flashcard exactly like this, with a blank line separating the Question and Answer, and a blank line separating different flashcards:\n\n"
            "**Q:** [Question Text]\n\n"
            "**A:** [Answer Text]\n\n"
            "Do not include any numbers (like 1., 2.) before the Q: or A:. Do not include any main title or header in your response."
        )
    elif action == "interview":
        action_instructions = (
            "Generate 5 interview-style questions and answers based on the retrieved PDF context. "
            "Format each exactly like this, with a blank line separating the Question and Answer, and a blank line separating different questions:\n\n"
            "**Q:** [Question Text]\n\n"
            "**A:** [Answer Text]\n\n"
            "Do not include any numbers (like 1., 2.) before the Q: or A:. Do not include any main title or header in your response."
        )
    elif action == "summary":
        action_instructions = "Create a comprehensive summary of the retrieved PDF context, detailing all key findings, objectives, methodology, and conclusions. Do not include any main title or header in your response."

    instructions = (
        "You are an elite academic research assistant. Use ONLY the retrieved PDF context below to answer the user's question. "
        "Strictly adhere to the following rules:\n"
        "1. Do not use your own general training data, external knowledge, or external facts to answer the question. Your answer must be derived ENTIRELY and EXCLUSIVELY from the retrieved PDF context below.\n"
        "2. Do not invent facts, fabricate findings, or assume information outside the provided PDF context. If a fact or claim cannot be verified from the PDF context, do not include it. Strict factual grounding is mandatory.\n"
        "3. Keep your response closely aligned to the exact wording or close phrasing of the PDF text ('same to same'). Do not paraphrase to the point of altering the tone or factual precision of the original text.\n"
        "4. Do NOT include any bracketed academic citations (e.g., [1], [2], [12-14]) or figure/table references (e.g., Fig. 2, Figure 4, Table 1) in your response. The response must be clean and highly readable.\n"
        "5. Format your response beautifully using clear Markdown structures: use bold titles, structured bullet points, or numbered lists where appropriate for professional readability.\n"
        "6. If the retrieved context contains relevant information to answer or address the user's query, synthesize it comprehensively. Do NOT say 'I could not find the answer' or apologize if there is relevant information present. Only say 'I could not find the answer in the selected PDF' if the retrieved context is completely irrelevant to the topic of the query or does not contain the answer."
    )

    if action_instructions:
        instructions += "\n7. SPECIAL FORMATTING DIRECTION: " + action_instructions

    prompt = (
        f"{instructions}\n\n"
        f"Selected PDF: {st.session_state.pdf_chat_selected_pdf or 'Unknown'}\n"
        f"User Question: {question}\n\n"
        "Retrieved PDF Context:\n"
        f"{retrieved_context}\n\n"
        "Please provide a comprehensive, well-structured answer below:"
    )
    return prompt


def build_retrieved_context(chunks: list[dict]) -> str:
    cleaned_texts = []
    for chunk in chunks:
        doc = chunk.get("document", "")
        cleaned_doc = clean_academic_citations(doc)
        if cleaned_doc:
            cleaned_texts.append(cleaned_doc)
            
    # Join with double newlines to make one clean block
    return "\n\n".join(cleaned_texts)


def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
    apply_shared_theme()

    initialize_session_state()

    st.markdown(
        "<div class='header-card header-card-pdf'>"
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
            _, chunks = search_pdf_context(query, n_results=8, min_similarity=0.15, workspace=workspace, metadata_filter=metadata_filter)

        if chunks:
            # Perform sequential context window expansion to guarantee complete lists/workflows
            try:
                from memory.chroma_store import get_chroma_client, get_collection_name_for_workspace
                client = get_chroma_client()
                collection_name = get_collection_name_for_workspace(workspace, suffix="_pdfs")
                collection = client.get_collection(name=collection_name)
                
                # Fetch all chunks of this PDF to find contiguous pages quickly
                all_pdf_data = collection.get(
                    where={"source_file": selected_pdf},
                    include=["documents", "metadatas"]
                )
                
                # Map chunk_index (int) -> chunk dictionary
                chunk_map = {}
                if all_pdf_data and all_pdf_data.get("documents"):
                    for i in range(len(all_pdf_data["ids"])):
                        meta = all_pdf_data["metadatas"][i]
                        idx_str = meta.get("chunk_index", "0")
                        try:
                            idx = int(idx_str)
                            chunk_map[idx] = {
                                "id": all_pdf_data["ids"][i],
                                "document": all_pdf_data["documents"][i],
                                "metadata": meta,
                                "similarity_pct": "Expanded"
                            }
                        except ValueError:
                            pass
                
                # Expand each of the top 6 retrieved chunks to include their next 2 consecutive chunks
                expanded_chunks = []
                seen_indices = set()
                
                for c in chunks[:6]:
                    meta = c.get("metadata", {})
                    idx_str = meta.get("chunk_index")
                    if idx_str is not None:
                        try:
                            idx = int(idx_str)
                            for offset in [0, 1, 2]:
                                target_idx = idx + offset
                                if target_idx in chunk_map and target_idx not in seen_indices:
                                    seen_indices.add(target_idx)
                                    target_chunk = dict(chunk_map[target_idx])
                                    if offset == 0:
                                        target_chunk["similarity_pct"] = c.get("similarity_pct", "0.0%")
                                    else:
                                        primary_sim = c.get("similarity_pct", "0.0%")
                                        target_chunk["similarity_pct"] = f"{primary_sim} (Ext)"
                                    expanded_chunks.append(target_chunk)
                        except ValueError:
                            pass
                            
                # Append any remaining chunks beyond the top 6 that were retrieved
                for c in chunks[6:]:
                    meta = c.get("metadata", {})
                    idx_str = meta.get("chunk_index")
                    if idx_str is not None:
                        try:
                            idx = int(idx_str)
                            if idx in chunk_map and idx not in seen_indices:
                                    seen_indices.add(idx)
                                    target_chunk = dict(chunk_map[idx])
                                    target_chunk["similarity_pct"] = c.get("similarity_pct", "0.0%")
                                    expanded_chunks.append(target_chunk)
                        except ValueError:
                            pass
                            
                if expanded_chunks:
                    chunks = expanded_chunks
            except Exception:
                pass

        # Sort chunks chronologically by chunk_index
        try:
            chunks = sorted(chunks, key=lambda x: int(x.get("metadata", {}).get("chunk_index", 0)))
        except Exception:
            pass

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

        cleaned_answer = clean_assistant_response(answer)
        if action == "explain":
            cleaned_answer = "### 💡 Beginner-Friendly Explanation\n\n" + cleaned_answer
        elif action == "notes":
            cleaned_answer = "### 📝 Study Notes\n\n" + cleaned_answer
        elif action == "flashcards":
            cleaned_answer = "### 🗂️ Flashcards\n\n" + cleaned_answer
        elif action == "interview":
            cleaned_answer = "### 💼 Interview Questions\n\n" + cleaned_answer
        elif action == "summary":
            cleaned_answer = "### 📖 Summary\n\n" + cleaned_answer
            
        add_chat_message("assistant", cleaned_answer, sources=filtered_chunks)

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
                st.markdown(render_grouped_sources(message["sources"]), unsafe_allow_html=True)

    if st.session_state.pdf_chat_history:
        with st.expander("📖 Retrieved Context", expanded=False):
            if st.session_state.pdf_chat_latest_chunks:
                chunks = st.session_state.pdf_chat_latest_chunks
                meta = chunks[0].get("metadata", {})
                source_file = meta.get("source_file", "Unknown PDF")
                if "/" in source_file:
                    source_file = source_file.split("/")[-1]
                elif "\\" in source_file:
                    source_file = source_file.split("\\")[-1]
                
                # Deduplicate and format unique sections covered
                sections_covered = []
                for c in chunks:
                    sec = c.get("metadata", {}).get("section", "Unknown")
                    if sec not in sections_covered:
                        sections_covered.append(sec)
                sections_str = ", ".join(sections_covered)
                
                # Get max similarity
                max_sim = chunks[0].get("similarity_pct", "0.0%")
                
                # Consolidate and clean all text blocks
                cleaned_texts = []
                for c in chunks:
                    text = c.get("document", "").strip()
                    cleaned_text = clean_academic_citations(text)
                    if cleaned_text:
                        cleaned_texts.append(cleaned_text)
                
                consolidated_text = "\n\n".join(cleaned_texts)
                
                st.markdown(
                    f"""<div style='background: rgba(129, 140, 248, 0.05); border: 1px solid rgba(129, 140, 248, 0.15); 
                               padding: 16px 20px; border-radius: 10px; margin-bottom: 16px;'>
                    <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; border-bottom: 1px solid rgba(129, 140, 248, 0.15); padding-bottom: 12px;'>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <span style='font-size: 16px;'>📄</span>
                            <span style='font-weight: 700; color: #ffffff; font-size: 15px;'>{source_file}</span>
                        </div>
                        <div style='display: flex; gap: 12px; font-size: 12.5px; color: #a1a1aa;'>
                            <span>📚 Parts: <strong style='color: #ffffff;'>{"1-" + str(len(chunks)) if len(chunks) > 1 else "1"}</strong></span>
                            <span>📍 Sections: <strong style='color: #ffffff;'>{sections_str}</strong></span>
                            <span>🎯 Max Match: <strong style='color: #818cf8;'>{max_sim}</strong></span>
                        </div>
                    </div>
                    <div style='max-height: 500px; overflow-y: auto; padding-right: 8px; white-space: pre-wrap; color: #e4e4e7; font-size: 13.5px; line-height: 1.6; font-family: inherit;'>{consolidated_text}</div>
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
