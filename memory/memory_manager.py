import uuid
import time
from datetime import datetime
from memory.chroma_store import store_research_memory, search_related_memories

# -------------------------------------------------------------------
# Beginner-Friendly Explanation:
# This file is the "Memory Manager". It bridges the gap between our Agents
# and the underlying ChromaDB vector database.
# It handles the logic of saving entire research pipelines and preparing
# retrieved context so the AI can use it in future tasks.
# -------------------------------------------------------------------

def save_complete_research(topic: str, full_research: str, summary: str, critique: str, workspace: str = "default"):
    """
    Saves the Research, Summary, and Critic Analysis together into the memory database.
    
    Args:
        topic (str): The original topic that was researched.
        full_research (str): The output from the Researcher Agent.
        summary (str): The output from the Summarizer Agent.
        critique (str): The output from the Critic Agent.
        workspace (str): The workspace to archive under.
    """
    print(f"[*] Memory Manager: Archiving research for topic '{topic}' in workspace '{workspace}'...")
    
    # We combine the most crucial parts for semantic search.
    # The summary is great for searchability, but we also save the full context.
    combined_document = f"TOPIC: {topic}\n\nSUMMARY:\n{summary}\n\nCRITIQUE:\n{critique}\n\nFULL RESEARCH:\n{full_research}"
    
    # Generate a unique ID for this specific research session
    session_id = f"mem_{uuid.uuid4().hex[:8]}"
    
    # Create metadata to make filtering easier later
    metadata = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "type": "comprehensive_research"
    }
    
    # Store it in our Vector Database!
    store_research_memory(
        doc_id=session_id,
        document_text=combined_document,
        metadata=metadata,
        workspace=workspace
    )

def retrieve_related_research(new_topic: str, workspace: str = "default") -> str:
    """
    Retrieves previous research related to a new topic and formats it as context.
    
    Args:
        new_topic (str): The new topic we are about to research.
        workspace (str): The workspace to retrieve from.
        
    Returns:
        str: A formatted string containing past research context, or empty string if none found.
    """
    print(f"[*] Memory Manager: Searching for past research related to '{new_topic}' in workspace '{workspace}'...")
    
    # Search ChromaDB for the top 2 most related past sessions
    past_memories = search_related_memories(query_text=new_topic, n_results=2, workspace=workspace)
    
    if not past_memories:
        print("[*] Memory Manager: No relevant past memories found.")
        return ""
        
    print(f"[*] Memory Manager: Found {len(past_memories)} related past memories!")
    
    context_string = "### PREVIOUS KNOWLEDGE RECOVERED FROM MEMORY ###\n\n"
    
    for idx, memory in enumerate(past_memories):
        topic = memory['metadata'].get('topic', 'Unknown Topic')
        date = memory['metadata'].get('timestamp', 'Unknown Date')
        
        context_string += f"--- Past Research {idx+1}: {topic} (from {date}) ---\n"
        context_string += f"{memory['document'][:1500]}...\n" # Limit length to save tokens
        context_string += "-" * 50 + "\n\n"
        
    return context_string


# ═══════════════════════════════════════════════════════════════════
#  RAG MEMORY MANAGER  —  production-grade retrieval interface
#  These functions build on the storage layer above to provide
#  clean semantic search and context injection for agents.
# ═══════════════════════════════════════════════════════════════════

def save_research_to_memory(topic: str, full_research: str,
                             summary: str, critique: str, workspace: str = "default", sources: list = None):
    """
    Enhanced memory save function with richer metadata.

    Stores the complete research session (report + summary + critique)
    as a single embedded document, optimised for semantic search retrieval.
    Metadata includes char counts so the UI can display useful stats.

    This function is additive — it does not replace save_complete_research().

    Args:
        topic         (str): The researched topic.
        full_research (str): Full markdown report from the Researcher Agent.
        summary       (str): Executive summary from the Summarizer Agent.
        critique      (str): Quality critique from the Critic Agent.
        workspace     (str): The workspace to archive under.
        sources       (list): List of sources containing full metadata.
    """
    print(f"[Memory Manager] Saving research session for: '{topic}' in workspace: '{workspace}'")

    # Build the combined searchable document
    # We prioritise summary + topic at the top for better embedding quality
    combined_document = (
        f"TOPIC: {topic}\n\n"
        f"SUMMARY:\n{summary}\n\n"
        f"CRITIQUE:\n{critique}\n\n"
        f"FULL RESEARCH:\n{full_research}"
    )

    session_id = f"rag_{uuid.uuid4().hex[:10]}"

    metadata = {
        "topic":            topic,
        "timestamp":        datetime.now().isoformat(),
        "type":             "rag_research",
        "research_chars":   str(len(full_research)),
        "summary_chars":    str(len(summary)),
    }
    if sources:
        import json
        metadata["sources_json"] = json.dumps(sources)


    from memory.chroma_store import add_research_memory
    add_research_memory(
        doc_id=session_id,
        document_text=combined_document,
        metadata=metadata,
        workspace=workspace
    )
    print(f"[Memory Manager] Research memory saved: {session_id}")


def _compute_keyword_similarity(q: str, doc: str) -> float:
    import re
    stop_words = {
        "the", "and", "a", "of", "to", "in", "is", "that", "it", "on", "for", "as", "with",
        "was", "were", "by", "an", "at", "are", "be", "this", "from", "or", "but", "not", "your", "my", "our"
    }
    q_tokens = [w.lower() for w in re.findall(r'\b\w{2,}\b', q) if w.lower() not in stop_words]
    doc_tokens = [w.lower() for w in re.findall(r'\b\w{2,}\b', doc) if w.lower() not in stop_words]
    
    if not q_tokens or not doc_tokens:
        return 0.0
        
    doc_token_set = set(doc_tokens)
    matches = sum(1 for tok in q_tokens if tok in doc_token_set)
    token_overlap = matches / len(q_tokens)
    
    # Calculate simple frequency density
    match_count = sum(doc_tokens.count(tok) for tok in q_tokens)
    tf_density = match_count / (len(doc_tokens) + 10)
    
    score = 0.8 * token_overlap + 0.2 * min(1.0, tf_density * 5)
    return round(min(1.0, score), 4)

def _are_duplicates(doc1: str, doc2: str) -> bool:
    import re
    # Convert documents to token sets (excluding very short words)
    tokens1 = set(re.findall(r'\b\w{3,}\b', doc1.lower()))
    tokens2 = set(re.findall(r'\b\w{3,}\b', doc2.lower()))
    if not tokens1 or not tokens2:
        return False
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    jaccard = len(intersection) / len(union)
    return jaccard > 0.75

def search_memory_context(query: str,
                           n_results: int = 3,
                           min_similarity: float = 0.20,
                           workspace: str = "default",
                           metadata_filter: dict = None
                           ) -> tuple[str, list]:
    """
    RAG Context Builder — retrieves and formats related memories for agent injection.
    Features hybrid search, reranking, metadata filtering, duplicate detection,
    semantic score boosting, dynamic thresholding, and latency tracking.
    """
    start_time = time.time()
    
    from memory.chroma_store import retrieve_similar_research
    
    # Step 1: Fetch a larger candidate set from ChromaDB
    candidate_n = max(12, n_results * 3)
    try:
        # We query with a low threshold to get enough candidates for reranking
        raw_candidates = retrieve_similar_research(
            query=query,
            n_results=candidate_n,
            min_similarity=0.02,
            workspace=workspace
        )
    except Exception as e:
        print(f"[Memory Retrieval Error] Failed to retrieve candidates: {e}")
        return "", []
        
    if not raw_candidates:
        print("[Memory Retrieval] No relevant memories found in ChromaDB.")
        return "", []
        
    # Step 2: Apply Hybrid Score Fusion, Metadata Filtering, and Boosting
    processed_candidates = []
    for cand in raw_candidates:
        # Metadata Filtering (Pre-filtering)
        if metadata_filter:
            metadata = cand.get("metadata", {})
            match = True
            for k, v in metadata_filter.items():
                if metadata.get(k) != v:
                    match = False
                    break
            if not match:
                continue
                
        # Sparse Keyword Scoring
        vector_score = cand.get("similarity_score", 0.0)
        keyword_score = _compute_keyword_similarity(query, cand.get("document", ""))
        
        # Score Fusion (70% Vector, 30% Keyword)
        hybrid_score = 0.7 * vector_score + 0.3 * keyword_score
        
        # Semantic Boosting
        boosting_reasons = []
        topic = cand.get("topic", "").lower()
        
        # Exact/Sub-phrase query match in topic
        if query.lower() in topic or topic in query.lower():
            hybrid_score += 0.15
            boosting_reasons.append("Exact/Sub-phrase Topic Match (+15%)")
            
        # Comprehensive report structure match
        doc_content = cand.get("document", "")
        if "SUMMARY:" in doc_content and "CRITIQUE:" in doc_content and "FULL RESEARCH:" in doc_content:
            hybrid_score += 0.10
            boosting_reasons.append("Comprehensive Report Structure (+10%)")
            
        # Recency Boost
        timestamp_str = cand.get("metadata", {}).get("timestamp")
        if timestamp_str:
            try:
                from datetime import datetime
                timestamp = datetime.fromisoformat(timestamp_str)
                age_seconds = (datetime.now() - timestamp).total_seconds()
                if age_seconds < 86400: # 24 hours
                    hybrid_score += 0.05
                    boosting_reasons.append("Recent Report <24h (+5%)")
            except Exception:
                pass
                
        hybrid_score = min(1.0, hybrid_score)
        
        # Source Confidence Scoring
        doc_len = len(doc_content)
        length_bonus = 0.10 if doc_len > 1500 else (0.05 if doc_len > 500 else 0.0)
        
        metadata = cand.get("metadata", {})
        has_full_metadata = all(k in metadata for k in ["topic", "timestamp", "type"])
        metadata_bonus = 0.10 if has_full_metadata else 0.0
        
        confidence_score = 0.8 * hybrid_score + length_bonus + metadata_bonus
        confidence_score = round(min(1.0, confidence_score), 4)
        
        # Attach intermediate details to memory
        cand_copy = cand.copy()
        cand_copy["vector_score"] = round(vector_score, 4)
        cand_copy["keyword_score"] = round(keyword_score, 4)
        cand_copy["hybrid_score"] = round(hybrid_score, 4)
        cand_copy["confidence_score"] = confidence_score
        cand_copy["confidence_pct"] = f"{confidence_score * 100:.1f}%"
        cand_copy["boosting_reasons"] = boosting_reasons
        
        processed_candidates.append(cand_copy)
        
    # Step 3: Sort by Confidence Score descending
    processed_candidates.sort(key=lambda x: x["confidence_score"], reverse=True)
    
    # Step 4: Duplicate Detection (Jaccard token comparison)
    unique_candidates = []
    for cand in processed_candidates:
        is_dup = False
        for unique in unique_candidates:
            if _are_duplicates(cand.get("document", ""), unique.get("document", "")):
                is_dup = True
                break
        if not is_dup:
            unique_candidates.append(cand)
            
    if not unique_candidates:
        print("[Memory Retrieval] No unique memories remained after filtering.")
        return "", []
        
    # Step 5: Dynamic Thresholding & Dynamic Top-K Selection
    top_score = unique_candidates[0]["confidence_score"]
    dynamic_min = max(min_similarity, top_score * 0.40)
    
    filtered_candidates = []
    for cand in unique_candidates:
        if cand["confidence_score"] >= dynamic_min:
            filtered_candidates.append(cand)
            
    # Apply dynamic slope cutoff (sudden drop in confidence > 0.35)
    final_candidates = []
    for i, cand in enumerate(filtered_candidates):
        if i > 0:
            prev_score = filtered_candidates[i-1]["confidence_score"]
            if prev_score - cand["confidence_score"] > 0.35:
                print(f"[Memory Retrieval] Dynamic slope cutoff: Dropped memory {cand.get('id')} (score drop: {prev_score:.2f} -> {cand['confidence_score']:.2f})")
                break
        final_candidates.append(cand)
        
    # Slice to final size
    selected_memories = final_candidates[:n_results]
    
    # Step 6: Logging & Latency Analytics
    latency_ms = int((time.time() - start_time) * 1000)
    dedup_count = len(processed_candidates) - len(unique_candidates)
    
    analytics = {
        "latency_ms": latency_ms,
        "scanned_candidates": len(raw_candidates),
        "deduplicated_count": dedup_count,
        "selected_count": len(selected_memories),
        "top_confidence": f"{top_score * 100:.1f}%" if selected_memories else "0.0%"
    }
    
    # Attach analytics to all returned memory dicts so the UI can display it
    for mem in selected_memories:
        mem["analytics"] = analytics
        
    print(f"[Memory Retrieval] Retrieval complete in {latency_ms}ms. "
          f"Scanned: {len(raw_candidates)}, Deduplicated: {dedup_count}, Final: {len(selected_memories)} memories.")
          
    if not selected_memories:
        return "", []
        
    # Step 7: Build structured context block with analytics details
    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║      ADVANCED RETRIEVED SEMANTIC MEMORY CONTEXT (RAG)     ║",
        "╚══════════════════════════════════════════════════════════╝",
        "",
        "┌──────────────────────────────────────────────────────────┐",
        f"│ RAG PIPELINE TELEMETRY ANALYTICS                         │",
        f"│ - Search Latency: {latency_ms} ms                              │",
        f"│ - Scanned Candidate Memories: {len(raw_candidates)}                          │",
        f"│ - Deduplicated & Merged: {dedup_count}                               │",
        f"│ - Top Source Confidence: {top_score * 100:.1f}%                         │",
        "└──────────────────────────────────────────────────────────┘",
        "",
        "The following information was retrieved from your previous research sessions.",
        "Use it to provide deeper, connected, and context-aware analysis.",
        "Cross-reference this memory with new web data for maximum accuracy.",
        "",
    ]
    
    for idx, mem in enumerate(selected_memories, start=1):
        topic_label = mem.get("topic", "Unknown Topic")
        conf_pct    = mem.get("confidence_pct", "N/A")
        date        = mem.get("metadata", {}).get("timestamp", "Unknown Date")
        
        # Include score details in the context block for the agent to know relevance details
        score_breakdown = f"Confidence: {conf_pct} (Vector: {mem['vector_score']*100:.0f}%, Keyword: {mem['keyword_score']*100:.0f}%)"
        
        doc_snippet = mem.get("document", "")[:1200]
        if len(mem.get("document", "")) > 1200:
            doc_snippet += "\n[... content truncated ...]"
            
        lines += [
            f"── Memory {idx}: {topic_label}  ({score_breakdown}) ──",
            f"Recorded: {date}",
            "",
            doc_snippet,
            "",
            "─" * 60,
            "",
        ]
        
    lines.append("══ END OF RETRIEVED MEMORY CONTEXT ══")
    context_block = "\n".join(lines)
    
    return context_block, selected_memories
