"""
Text chunking policies.
"""
import re
from typing import List


class TextChunker:
    """Handles text chunking with configurable overlap."""
    
    def __init__(self, 
                 min_chunk_size: int = 800, 
                 max_chunk_size: int = 1200, 
                 overlap_size: int = 150):
        """
        Initialize text chunker.
        
        Args:
            min_chunk_size: Minimum chunk size in characters
            max_chunk_size: Maximum chunk size in characters  
            overlap_size: Overlap between chunks in characters
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= self.max_chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Determine end position
            end = start + self.max_chunk_size
            
            if end >= len(text):
                # Last chunk
                chunk = text[start:]
                if len(chunk.strip()) > 0:
                    chunks.append(chunk.strip())
                break
            
            # Try to break at natural boundaries
            chunk_end = self._find_break_point(text, start, end)
            chunk = text[start:chunk_end].strip()
            
            if len(chunk) >= self.min_chunk_size or not chunks:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(chunk_end - self.overlap_size, start + 1)
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 0]
    
    def _find_break_point(self, text: str, start: int, preferred_end: int) -> int:
        """
        Find the best break point for a chunk.
        
        Args:
            text: Full text
            start: Start position
            preferred_end: Preferred end position
            
        Returns:
            Actual end position
        """
        # Look for natural break points in order of preference
        search_start = max(start + self.min_chunk_size, preferred_end - 200)
        # Limit search to reasonable range but don't exceed max boundary
        search_end = min(preferred_end + 50, len(text))  # Allow small overage for natural breaks
        search_text = text[search_start:search_end]
        
        # Try paragraph breaks first
        paragraph_match = re.search(r'\n\s*\n', search_text)
        if paragraph_match:
            break_point = search_start + paragraph_match.start()
            return min(break_point, search_end)
        
        # Try sentence endings
        sentence_matches = list(re.finditer(r'[.!?]\s+', search_text))
        if sentence_matches:
            # Use the last sentence break within range
            break_point = search_start + sentence_matches[-1].end()
            return min(break_point, search_end)
        
        # Try line breaks
        line_matches = list(re.finditer(r'\n', search_text))
        if line_matches:
            break_point = search_start + line_matches[-1].start()
            return min(break_point, search_end)
        
        # Fall back to word boundaries
        word_matches = list(re.finditer(r'\s+', search_text))
        if word_matches:
            break_point = search_start + word_matches[-1].start()
            return min(break_point, search_end)
        
        # Last resort: use preferred end
        return min(preferred_end, len(text))