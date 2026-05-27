import os
import warnings
import logging
import threading

# Silence annoying PyTorch/transformers import path warnings
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

# Heavy imports are lazy-loaded inside functions to drastically reduce initial startup time


# -------------------------------------------------------------------
# Beginner-Friendly Explanation:
# This file handles the direct connection to our Vector Database (ChromaDB).
# We use an embedding function to turn text into mathematical vectors.
# By storing vectors instead of plain text, the AI can perform "Semantic Search",
# meaning it can find related ideas based on meaning, not just exact keywords.
# -------------------------------------------------------------------

# Set up the persistent storage location. This ensures memory isn't lost
# when the application stops running.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

_client_lock = threading.Lock()
_cached_client = None
_cached_collection = None

def get_chroma_client():
    """
    Returns a cached global ChromaDB client to prevent SQLite lock issues.
    """
    global _cached_client
    if _cached_client is None:
        with _client_lock:
            if _cached_client is None:
                import chromadb
                _cached_client = chromadb.PersistentClient(path=DB_PATH)
    return _cached_client

def initialize_chroma():
    """
    Initializes the ChromaDB client and creates a collection for our memories.
    A collection is similar to a "table" in a normal database.
    """
    global _cached_collection
    if _cached_collection is not None:
        return _cached_collection
        
    client = get_chroma_client()
    
    # We use Chroma's default embedding function which uses 'all-MiniLM-L6-v2'
    # under the hood, but runs it via ONNX Runtime instead of PyTorch.
    # This is massively faster for CPU execution during both RAG retrieval and saving.
    from chromadb.utils import embedding_functions
    fast_ef = embedding_functions.DefaultEmbeddingFunction()
    
    # Get or create the collection named "research_memory"
    _cached_collection = client.get_or_create_collection(
        name="research_memory",
        embedding_function=fast_ef,
        metadata={"hnsw:space": "cosine"} # Cosine similarity measures the angle between vectors (meaning)
    )
    
    return _cached_collection

def store_research_memory(doc_id: str, document_text: str, metadata: dict):
    """
    Saves a piece of research into the vector database.
    
    Args:
        doc_id (str): A unique identifier for the document.
        document_text (str): The actual text content to be vectorized and saved.
        metadata (dict): Extra information (like topic, timestamp, or document type) 
                         so we can filter results later.
    """
    collection = initialize_chroma()
    
    try:
        # Add the document to our database.
        # The embedding_function automatically converts 'document_text' into a vector!
        collection.add(
            documents=[document_text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"[ChromaDB] Successfully saved memory: {doc_id}")
    except Exception as e:
        print(f"[ChromaDB Error] Failed to save memory: {e}")

def search_related_memories(query_text: str, n_results: int = 2):
    """
    Performs a semantic search to find past research related to the new query.
    
    Args:
        query_text (str): The new topic or question.
        n_results (int): How many past documents to retrieve.
        
    Returns:
        list: A list of dictionaries containing the retrieved documents and their metadata.
    """
    collection = initialize_chroma()
    
    try:
        # Query the collection. It converts query_text to a vector and finds nearest neighbors.
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        # Format the results into a more usable list of dictionaries
        retrieved_memories = []
        if results and results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                memory = {
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if 'distances' in results else None
                }
                retrieved_memories.append(memory)
                
        return retrieved_memories
        
    except Exception as e:
        print(f"[ChromaDB Error] Failed to search memory: {e}")
        return []

def get_all_memories():
    """
    Retrieves all memories currently stored in the vector database.
    Does not require loading the heavy sentence-transformers embedding function.
    """
    try:
        client = get_chroma_client()
        try:
            collection = client.get_collection(name="research_memory")
        except Exception:
            # Collection does not exist yet
            return []
            
        results = collection.get()
        retrieved_memories = []
        
        if results and results.get('documents'):
            for i in range(len(results['documents'])):
                memory = {
                    "id": results['ids'][i],
                    "document": results['documents'][i],
                    "metadata": results['metadatas'][i] if results['metadatas'] else {}
                }
                retrieved_memories.append(memory)
                
        # Sort by timestamp descending if possible
        retrieved_memories.sort(key=lambda x: x['metadata'].get('timestamp', ''), reverse=True)
        return retrieved_memories
        
    except Exception as e:
        print(f"[ChromaDB Error] Failed to retrieve all memories: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════
#  RAG RETRIEVAL LAYER  —  added to support the full RAG pipeline
#  The functions below are the production-grade retrieval interface.
#  They co-exist alongside the original storage functions above.
# ═══════════════════════════════════════════════════════════════════

def initialize_collection():
    """
    Public alias for initialize_chroma().

    Returns the ChromaDB collection with the sentence-transformer embedding
    function already attached. Use this as the clean entry-point for any
    code that needs direct collection access.

    Returns:
        chromadb.Collection: The 'research_memory' collection, ready to use.
    """
    return initialize_chroma()


def add_research_memory(doc_id: str, document_text: str, metadata: dict):
    """
    Enhanced wrapper for store_research_memory() with richer logging.

    Saves a vectorized research document into ChromaDB. The embedding function
    automatically converts document_text into a semantic vector before storage.

    Args:
        doc_id        (str):  Unique identifier for this memory entry.
        document_text (str):  Full text to embed and store.
        metadata      (dict): Structured metadata (topic, timestamp, type, etc.)
    """
    print(f"[Memory Storage] Encoding and archiving memory: {doc_id}")
    store_research_memory(doc_id=doc_id, document_text=document_text, metadata=metadata)


def retrieve_similar_research(query: str, n_results: int = 3,
                               min_similarity: float = 0.20) -> list[dict]:
    """
    RAG Retrieval Core — finds the top-N semantically similar research records.

    How it works:
      1. The query string is embedded by the same sentence-transformer model
         used during storage, producing a 384-dimensional vector.
      2. ChromaDB performs an approximate nearest-neighbour search using HNSW
         with cosine similarity as the distance metric.
      3. Results are ranked by similarity score and filtered by min_similarity.

    Cosine distance → similarity conversion:
      ChromaDB with hnsw:space=cosine stores distances in [0, 2].
      distance 0 → identical   (similarity 1.00 = 100 %)
      distance 1 → orthogonal  (similarity 0.00 =   0 %)
      distance 2 → opposite    (similarity capped at 0)
      Formula: similarity = max(0.0, 1.0 - distance)

    Args:
        query          (str):   The new research topic or question.
        n_results      (int):   Maximum number of memories to retrieve (default 3).
        min_similarity (float): Minimum similarity threshold 0–1 (default 0.20).
                                Results below this are discarded as noise.

    Returns:
        list[dict]: Each dict contains:
            - 'id'              (str)   Memory UUID
            - 'topic'           (str)   Original research topic
            - 'document'        (str)   Full stored text (truncated for context)
            - 'metadata'        (dict)  All stored metadata fields
            - 'similarity_score'(float) 0.0–1.0 similarity to the query
            - 'similarity_pct'  (str)   Human-readable percentage e.g. "87.3%"
            - 'distance'        (float) Raw ChromaDB cosine distance
    """
    print(f"[Memory Retrieval] Searching semantic memory for: '{query}'")

    try:
        collection = initialize_chroma()

        # Guard: ChromaDB errors if n_results > collection size
        total_docs = collection.count()
        if total_docs == 0:
            print("[Memory Retrieval] Memory bank is empty — no past research found.")
            return []

        actual_n = min(n_results, total_docs)

        # Perform the semantic search
        results = collection.query(
            query_texts=[query],
            n_results=actual_n,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []

        if not results or not results.get("documents") or not results["documents"][0]:
            print("[Memory Retrieval] No results returned from ChromaDB.")
            return []

        for i in range(len(results["documents"][0])):
            raw_distance = results["distances"][0][i] if results.get("distances") else 1.0
            similarity   = max(0.0, round(1.0 - raw_distance, 4))

            # Filter out memories that are not relevant enough
            if similarity < min_similarity:
                continue

            metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
            topic    = metadata.get("topic", "Unknown Topic")

            retrieved.append({
                "id":              results["ids"][0][i],
                "topic":           topic,
                "document":        results["documents"][0][i],
                "metadata":        metadata,
                "similarity_score": similarity,
                "similarity_pct":  f"{similarity * 100:.1f}%",
                "distance":        raw_distance,
            })

        # Sort by similarity descending (best match first)
        retrieved.sort(key=lambda x: x["similarity_score"], reverse=True)

        print(f"[Memory Retrieval] Found {len(retrieved)} relevant memories "
              f"(threshold >= {min_similarity * 100:.0f}%).")
        return retrieved

    except Exception as e:
        print(f"[Memory Retrieval Error] Semantic search failed: {e}")
        return []
