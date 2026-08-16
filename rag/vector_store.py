import os
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
from ai.gemini_service import GeminiService

class VectorStore:
    """
    Wraps the FAISS library for local vector similarity searches.
    Generates embeddings via Gemini's official text-embedding-004 model.
    Saves and loads the index from disk to optimize performance.
    """
    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.index_file = index_dir / "faiss_index.bin"
        self.chunks_file = index_dir / "chunks.pkl"
        
        self.dimension = 768  # text-embedding-004 dimension size
        self.index = None
        self.chunks: List[Dict[str, Any]] = []
        self.ai_service = GeminiService()
        
        # Ensure directories exist
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
    def is_built(self) -> bool:
        """Returns True if the index and chunks files exist on disk."""
        return self.index_file.exists() and self.chunks_file.exists()
        
    def build_index(self, chunks: List[Dict[str, Any]]):
        """
        Builds the FAISS index by generating embeddings for all chunks.
        Saves the FAISS index and Pickle chunk data to disk.
        """
        if not chunks:
            return
            
        self.chunks = chunks
        
        # 1. Generate embeddings for each chunk
        embeddings_list = []
        for c in chunks:
            # We embed a combination of Title + Content for richer context retrieval
            text_to_embed = f"Title: {c['title']}\nContent: {c['content']}"
            vector = self.ai_service.get_embeddings(text_to_embed)
            embeddings_list.append(vector)
            
        # Convert to float32 numpy array
        np_embeddings = np.array(embeddings_list).astype('float32')
        
        # 2. Setup FAISS Index
        # IndexFlatL2 compares using L2 distance (Euclidean).
        # Normalizing vectors first converts L2 search into Inner Product/Cosine similarity.
        faiss.normalize_L2(np_embeddings)
        
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product for Cosine Similarity
        self.index.add(np_embeddings)
        
        # 3. Save to disk
        faiss.write_index(self.index, str(self.index_file))
        with open(self.chunks_file, "wb") as f:
            pickle.dump(self.chunks, f)
            
    def load_index(self):
        """Loads FAISS index and Pickle chunk metadata from disk."""
        if self.is_built():
            self.index = faiss.read_index(str(self.index_file))
            with open(self.chunks_file, "rb") as f:
                self.chunks = pickle.load(f)
                
    def similarity_search(self, query: str, k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Performs inner product cosine similarity search on the index.
        Returns:
            List of tuples: [(chunk_dict, similarity_score), ...]
        """
        if not self.index or not self.chunks:
            # Try to load if not loaded in memory
            self.load_index()
            
        if not self.index or not self.chunks:
            return []
            
        # Get query embedding
        query_vector = self.ai_service.get_embeddings(query)
        np_query = np.array([query_vector]).astype('float32')
        faiss.normalize_L2(np_query)
        
        # Search index
        scores, indices = self.index.search(np_query, k)
        
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx != -1 and idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))
                
        return results
