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

def save_complete_research(topic: str, full_research: str, summary: str, critique: str):
    """
    Saves the Research, Summary, and Critic Analysis together into the memory database.
    
    Args:
        topic (str): The original topic that was researched.
        full_research (str): The output from the Researcher Agent.
        summary (str): The output from the Summarizer Agent.
        critique (str): The output from the Critic Agent.
    """
    print(f"[*] Memory Manager: Archiving research for topic '{topic}'...")
    
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
        metadata=metadata
    )

def retrieve_related_research(new_topic: str) -> str:
    """
    Retrieves previous research related to a new topic and formats it as context.
    
    Args:
        new_topic (str): The new topic we are about to research.
        
    Returns:
        str: A formatted string containing past research context, or empty string if none found.
    """
    print(f"[*] Memory Manager: Searching for past research related to '{new_topic}'...")
    
    # Search ChromaDB for the top 2 most related past sessions
    past_memories = search_related_memories(query_text=new_topic, n_results=2)
    
    if not past_memories:
        print("[*] Memory Manager: No relevant past memories found.")
        return ""
        
    print(f"[*] Memory Manager: Found {len(past_memories)} related past memories!")
    
    # Format the past memories so we can inject them into the AI's prompt
    context_string = "### PREVIOUS KNOWLEDGE RECOVERED FROM MEMORY ###\n\n"
    
    for idx, memory in enumerate(past_memories):
        topic = memory['metadata'].get('topic', 'Unknown Topic')
        date = memory['metadata'].get('timestamp', 'Unknown Date')
        
        context_string += f"--- Past Research {idx+1}: {topic} (from {date}) ---\n"
        context_string += f"{memory['document'][:1500]}...\n" # Limit length to save tokens
        context_string += "-" * 50 + "\n\n"
        
    return context_string
