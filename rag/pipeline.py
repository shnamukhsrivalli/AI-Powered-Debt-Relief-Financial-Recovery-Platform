from pathlib import Path
from config.settings import KNOWLEDGE_DIR, DATA_DIR
from rag.document_loader import load_knowledge_documents
from rag.chunker import chunk_document
from rag.vector_store import VectorStore
from ai.gemini_service import GeminiService
from typing import Dict, Any, List

class RAGPipeline:
    """
    RAG Pipeline orchestrator.
    Handles indexing setup, similarity retrieval, and grounded GenAI responses.
    """
    def __init__(self):
        self.knowledge_dir = KNOWLEDGE_DIR
        # Store index files in the data directory
        self.vector_store = VectorStore(DATA_DIR / "vector_index")
        self.ai_service = GeminiService()
        
    def initialize_rag(self, force_rebuild: bool = False):
        """
        Automated seeding and indexing.
        Loads knowledge documents, chunks them, embeds them, and saves to FAISS.
        """
        if not self.vector_store.is_built() or force_rebuild:
            # 1. Load documents
            docs = load_knowledge_documents(self.knowledge_dir)
            
            # 2. Chunk documents
            all_chunks = []
            for doc in docs:
                chunks = chunk_document(doc)
                all_chunks.extend(chunks)
                
            # 3. Embed & index
            if all_chunks:
                self.vector_store.build_index(all_chunks)
            else:
                raise ValueError("No knowledge documents found to index. Seed documents in data/knowledge/ first.")
        else:
            # Load existing index in memory
            self.vector_store.load_index()
            
    def get_grounded_answer(self, query: str, k: int = 2) -> Dict[str, Any]:
        """
        Searches the local FAISS index, retrieves the top-K chunks,
        creates a grounded context, and queries Gemini.
        """
        # Load index if not initialized
        self.vector_store.load_index()
        
        # 1. Search index
        matches = self.vector_store.similarity_search(query, k=k)
        
        if not matches:
            # Fallback if vector store is empty or failed
            return {
                "answer": "I couldn't retrieve any matching documentation from the local database. Please ensure the knowledge base is seeded.",
                "sources": []
            }
            
        # 2. Build context text
        context_parts = []
        sources = []
        
        for idx, (chunk, score) in enumerate(matches):
            context_parts.append(
                f"--- SOURCE {idx+1}: {chunk['title']} (File: {chunk['source']}) ---\n"
                f"{chunk['content']}\n"
            )
            sources.append({
                "title": chunk["title"],
                "source": chunk["source"],
                "score": score
            })
            
        context_str = "\n".join(context_parts)
        
        # 3. Build grounding prompt
        prompt = f"""
You are the AI Financial Recovery Assistant. Answer the user's question using ONLY the provided educational sources below.
If the answer cannot be found in the sources, state: "I'm sorry, but that information is not covered in our knowledge hub."
Do not invent facts, and do not make assumptions outside the sources.

### CONTEXT / EDUCATIONAL SOURCES
{context_str}

### USER QUESTION
{query}

### GROUNDED ANSWER
Provide your answer in a clear, educational, and structured format. Cite which source you are referencing where appropriate.
"""
        system_instruction = "You are a grounded RAG financial assistant. Answer strictly based on the provided context."
        answer = self.ai_service.generate_text(prompt, system_instruction=system_instruction, temperature=0.1)
        
        return {
            "answer": answer,
            "sources": sources
        }
