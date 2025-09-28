"""
Document processing pipeline implementation.
"""
import uuid
from typing import Dict, Any, Optional, List
from app.policies import TextNormalizer, TextChunker, LanguageDetector, DocumentDeduplicator
from app.models import IngestInput, ChunkItem
from app.infra.logging import get_logger


class DocumentProcessor:
    """Core document processing pipeline."""
    
    def __init__(self):
        """Initialize document processor with policy components."""
        self.normalizer = TextNormalizer()
        self.chunker = TextChunker()
        self.deduplicator = DocumentDeduplicator()
        self.language_detector = LanguageDetector()
        self.logger = get_logger("pipeline.processor")
    
    def process_document(self, ingest_input: IngestInput) -> List[ChunkItem]:
        """
        Process a document through the full pipeline.
        
        Args:
            ingest_input: Document to process
            
        Returns:
            List of chunk items ready for indexing
        """
        self.logger.info(
            "Processing document",
            extra={
                "doc_id": ingest_input.doc_id,
                "source": ingest_input.source,
                "text_length": len(ingest_input.text)
            }
        )
        
        # Step 1: Normalize text
        normalized_text = self.normalizer.normalize(ingest_input.text)
        
        # Step 2: Detect language if not provided
        detected_lang = ingest_input.lang
        if not detected_lang and self.language_detector.is_supported():
            detected_lang = self.language_detector.detect_language(normalized_text)
        
        # Step 3: Chunk the normalized text
        chunks = self.chunker.chunk_text(normalized_text)
        
        # Step 4: Create chunk items with metadata
        chunk_items = []
        for ord_idx, chunk_text in enumerate(chunks):
            # Generate a UUID for Qdrant compatibility while keeping readable reference
            chunk_uuid = str(uuid.uuid4())
            original_chunk_id = f"{ingest_input.doc_id}::c{ord_idx}"
            
            chunk_metadata = {
                "doc_id": ingest_input.doc_id,
                "source": ingest_input.source,
                "path": ingest_input.path,
                "lang": detected_lang,
                "ord": ord_idx,
                "original_id": original_chunk_id  # Keep original ID for reference
            }
            
            chunk_item = ChunkItem(
                id=chunk_uuid,  # Use UUID for Qdrant
                doc_id=ingest_input.doc_id,
                ord=ord_idx,
                text=chunk_text,
                metadata=chunk_metadata
            )
            
            chunk_items.append(chunk_item)
        
        self.logger.info(
            "Document processed successfully",
            extra={
                "doc_id": ingest_input.doc_id,
                "chunks_created": len(chunk_items),
                "detected_lang": detected_lang
            }
        )
        
        return chunk_items
    
    def compute_document_hash(self, text: str) -> str:
        """Compute hash for document deduplication."""
        return self.deduplicator.compute_hash(text)
    
    def is_duplicate_document(self, new_hash: str, existing_hash: str = None) -> bool:
        """Check if document is a duplicate."""
        return self.deduplicator.is_duplicate(new_hash, existing_hash)