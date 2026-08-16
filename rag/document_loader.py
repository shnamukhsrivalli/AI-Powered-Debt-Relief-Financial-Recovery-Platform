import os
from pathlib import Path
from typing import List, Dict

def load_knowledge_documents(knowledge_dir: Path) -> List[Dict[str, str]]:
    """
    Loads all markdown (.md) documents from the knowledge directory.
    Returns:
        List of dicts: [{"title": str, "content": str, "source": str}]
    """
    documents = []
    if not os.path.exists(knowledge_dir):
        return documents
        
    for filename in os.listdir(knowledge_dir):
        if filename.endswith(".md"):
            file_path = knowledge_dir / filename
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Extracted title from filename (or header)
                title = filename.replace(".md", "").replace("_", " ").title()
                documents.append({
                    "title": title,
                    "content": content,
                    "source": filename
                })
            except Exception as e:
                # Log error or skip
                continue
                
    return documents
