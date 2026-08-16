from typing import List, Dict, Any

def chunk_document(doc: Dict[str, str], chunk_size: int = 600, chunk_overlap: int = 120) -> List[Dict[str, Any]]:
    """
    Chunks document content using a sliding window approach with character boundaries.
    Tries to break at sentence endings or space characters to preserve clarity.
    """
    content = doc["content"]
    title = doc["title"]
    source = doc["source"]
    
    chunks = []
    start = 0
    content_len = len(content)
    chunk_idx = 0
    
    if content_len <= chunk_size:
        return [{
            "title": title,
            "content": content,
            "source": source,
            "chunk_index": 0
        }]
        
    while start < content_len:
        end = start + chunk_size
        
        # If we are not at the end of the text, try to find a sentence boundary nearby
        if end < content_len:
            # Look backwards up to 80 characters for a sentence boundary (. \n)
            found_boundary = False
            for offset in range(0, 80):
                char_idx = end - offset
                if char_idx < content_len and content[char_idx] in ['.', '\n']:
                    end = char_idx + 1 # Include the boundary character
                    found_boundary = True
                    break
                    
            # Fallback to space if no sentence boundary found
            if not found_boundary:
                for offset in range(0, 40):
                    char_idx = end - offset
                    if char_idx < content_len and content[char_idx] == ' ':
                        end = char_idx
                        break
                        
        chunk_text = content[start:end].strip()
        
        if chunk_text:
            chunks.append({
                "title": title,
                "content": chunk_text,
                "source": source,
                "chunk_index": chunk_idx
            })
            chunk_idx += 1
            
        start = end - chunk_overlap
        if start >= content_len:
            break
            
    return chunks
