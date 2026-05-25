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
    
    # We use sentence-transformers to convert text to vectors.
    # 'all-MiniLM-L6-v2' is a fast and lightweight model perfect for our needs.
    try:
        import sentence_transformers
    except ImportError:
        pass
        
    from chromadb.utils import embedding_functions
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Get or create the collection named "research_memory"
    _cached_collection = client.get_or_create_collection(
        name="research_memory",
        embedding_function=sentence_transformer_ef,
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
