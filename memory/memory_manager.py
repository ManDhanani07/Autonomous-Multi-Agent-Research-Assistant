import uuid
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
                             summary: str, critique: str, workspace: str = "default"):
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

    from memory.chroma_store import add_research_memory
    add_research_memory(
        doc_id=session_id,
        document_text=combined_document,
        metadata=metadata,
        workspace=workspace
    )
    print(f"[Memory Manager] Research memory saved: {session_id}")


def search_memory_context(query: str,
                           n_results: int = 3,
                           min_similarity: float = 0.20,
                           workspace: str = "default"
                           ) -> tuple[str, list]:
    """
    RAG Context Builder — retrieves and formats related memories for agent injection.

    This is the primary interface between the Researcher Agent and the memory system.
    It retrieves semantically similar past research and formats it into a clean
    context block that can be directly injected into the LLM prompt.

    Workflow:
        query → retrieve_similar_research() → filter by threshold
              → format as structured context → return for prompt injection

    Args:
        query          (str):   The new research topic.
        n_results      (int):   Max memories to retrieve (default 3).
        min_similarity (float): Minimum relevance threshold (default 0.20 = 20%).
        workspace      (str):   The active workspace to retrieve from.

    Returns:
        tuple[str, list]:
            - context_block (str):  Formatted string ready to inject into prompt.
                                    Empty string "" if no relevant memories found.
            - memories      (list): Raw memory dicts for UI display (may be empty).
                                    Each dict matches the retrieve_similar_research() schema.
    """
    print(f"[Memory Retrieval] Searching semantic memory in workspace '{workspace}' for: '{query}'")

    from memory.chroma_store import retrieve_similar_research

    try:
        memories = retrieve_similar_research(
            query=query,
            n_results=n_results,
            min_similarity=min_similarity,
            workspace=workspace
        )
    except Exception as e:
        print(f"[Memory Retrieval Error] Failed to search memory: {e}")
        return "", []

    # ── No relevant memories ───────────────────────────────────────────────
    if not memories:
        print("[Memory Retrieval] No relevant memory found. Proceeding without context.")
        return "", []

    print(f"[Memory Retrieval] Found {len(memories)} relevant memories.")

    # ── Build the formatted context block ─────────────────────────────────
    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║         RETRIEVED SEMANTIC MEMORY CONTEXT (RAG)          ║",
        "╚══════════════════════════════════════════════════════════╝",
        "",
        "The following information was retrieved from your previous research sessions.",
        "Use it to provide deeper, connected, and context-aware analysis.",
        "Cross-reference this memory with new web data for maximum accuracy.",
        "",
    ]

    for idx, mem in enumerate(memories, start=1):
        topic_label = mem.get("topic", "Unknown Topic")
        sim_pct     = mem.get("similarity_pct", "N/A")
        date        = mem.get("metadata", {}).get("timestamp", "Unknown Date")

        # Truncate document to save tokens (top 1200 chars = ~300 tokens)
        doc_snippet = mem.get("document", "")[:1200]
        if len(mem.get("document", "")) > 1200:
            doc_snippet += "\n[... content truncated ...]"

        lines += [
            f"── Memory {idx}: {topic_label}  (Relevance: {sim_pct}) ──",
            f"Recorded: {date}",
            "",
            doc_snippet,
            "",
            "─" * 60,
            "",
        ]

    lines.append("══ END OF RETRIEVED MEMORY CONTEXT ══")
    context_block = "\n".join(lines)

    print(f"[Memory Injection] Context block prepared — "
          f"{len(memories)} memory/memories ready to inject into Researcher Agent.")

    return context_block, memories
