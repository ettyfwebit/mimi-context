"""
Document deduplication policies.
"""
import hashlib
from typing import Optional


class DocumentDeduplicator:
    """Handles document deduplication using content hashing."""
    
    def __init__(self):
        pass
    
    def compute_hash(self, text: str) -> str:
        """
        Compute SHA-256 hash of normalized text content.
        
        Args:
            text: Text content to hash
            
        Returns:
            Hexadecimal hash string
        """
        # Normalize whitespace for consistent hashing
        normalized = ' '.join(text.split())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, new_hash: str, existing_hash: Optional[str]) -> bool:
        """
        Check if document is a duplicate based on hash comparison.
        
        Args:
            new_hash: Hash of new document
            existing_hash: Hash of existing document (if any)
            
        Returns:
            True if documents are duplicates
        """
        return existing_hash is not None and new_hash == existing_hash