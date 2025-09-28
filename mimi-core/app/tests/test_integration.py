"""
Integration tests for document ingestion pipeline.
"""
import pytest
from datetime import datetime
from app.models import IngestInput, DocumentRecord
from app.services.pipeline_core import DocumentProcessor
from app.services.metadata import MetadataService


class TestPipelineIntegration:
    """Integration tests for the document processing pipeline."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.processor = DocumentProcessor()
    
    def test_process_simple_document(self):
        """Test processing a simple text document."""
        # Create test input
        ingest_input = IngestInput(
            doc_id="test:sample.md",
            source="test",
            path="sample.md",
            text="This is a sample document for testing. It contains multiple sentences to ensure proper chunking.",
            lang="en"
        )
        
        # Process document
        chunks = self.processor.process_document(ingest_input)
        
        # Verify results
        assert len(chunks) >= 1
        assert chunks[0].doc_id == "test:sample.md"
        assert chunks[0].ord == 0
        assert "sample document" in chunks[0].text
        
        # Verify metadata
        assert chunks[0].metadata["source"] == "test"
        assert chunks[0].metadata["path"] == "sample.md"
        assert chunks[0].metadata["doc_id"] == "test:sample.md"
    
    def test_process_long_document(self):
        """Test processing a longer document that creates multiple chunks."""
        # Create longer text content
        long_text = """
        This is a comprehensive document about various topics. It contains multiple paragraphs and sections.
        
        Section 1: Introduction
        This section introduces the main concepts and provides background information. The text is designed
        to be long enough to create multiple chunks during processing.
        
        Section 2: Main Content
        This section contains the primary information. It includes detailed explanations and examples
        that help illustrate the key points being discussed.
        
        Section 3: Advanced Topics
        Here we delve into more complex subjects that require deeper understanding. The content builds
        upon the foundation established in earlier sections.
        
        Conclusion
        This document serves as a comprehensive guide to the subject matter, providing both introductory
        and advanced information for readers at different levels of expertise.
        """
        
        ingest_input = IngestInput(
            doc_id="test:long_doc.md",
            source="test",
            path="long_doc.md",
            text=long_text.strip()
        )
        
        # Process document
        chunks = self.processor.process_document(ingest_input)
        
        # Verify multiple chunks created
        assert len(chunks) >= 2
        
        # Verify chunk ordering
        for i, chunk in enumerate(chunks):
            assert chunk.ord == i
            assert chunk.doc_id == "test:long_doc.md"
        
        # Verify first chunk contains introduction
        assert any("Introduction" in chunk.text for chunk in chunks)
    
    def test_process_html_document(self):
        """Test processing HTML content."""
        html_content = """
        <html>
        <head><title>Test Document</title></head>
        <body>
        <nav>Navigation menu</nav>
        <header>Header content</header>
        <main>
        <h1>Main Content</h1>
        <p>This is the main paragraph content that should be extracted.</p>
        <p>This is another paragraph with <strong>important</strong> information.</p>
        </main>
        <footer>Footer content</footer>
        </body>
        </html>
        """
        
        ingest_input = IngestInput(
            doc_id="test:html_doc.html",
            source="test",
            path="html_doc.html",
            text=html_content
        )
        
        # Process document
        chunks = self.processor.process_document(ingest_input)
        
        # Verify HTML was normalized
        assert len(chunks) >= 1
        normalized_text = chunks[0].text
        
        # Should contain main content but not HTML tags
        assert "main paragraph content" in normalized_text
        assert "important information" in normalized_text
        assert "<nav>" not in normalized_text
        assert "<p>" not in normalized_text
    
    def test_document_hash_consistency(self):
        """Test that document hashing is consistent."""
        text1 = "This is test content."
        text2 = "This is test content."  # Same content
        text3 = "This is different content."
        
        hash1 = self.processor.compute_document_hash(text1)
        hash2 = self.processor.compute_document_hash(text2)
        hash3 = self.processor.compute_document_hash(text3)
        
        # Same content should produce same hash
        assert hash1 == hash2
        
        # Different content should produce different hash
        assert hash1 != hash3
    
    def test_duplicate_detection(self):
        """Test document duplicate detection."""
        text = "This is test content for duplicate detection."
        hash_value = self.processor.compute_document_hash(text)
        
        # Test duplicate detection
        assert self.processor.is_duplicate_document(hash_value, hash_value) == True
        assert self.processor.is_duplicate_document(hash_value, "different_hash") == False
        assert self.processor.is_duplicate_document(hash_value, None) == False
    
    @pytest.mark.asyncio
    async def test_metadata_service_integration(self):
        """Test integration with metadata service."""
        # Initialize metadata service
        metadata_service = MetadataService()
        await metadata_service.initialize()
        
        # Create test document record
        doc_record = DocumentRecord(
            doc_id="test:integration.md",
            source="test",
            path="integration.md",
            hash="test_hash_123",
            lang="en",
            updated_at=datetime.utcnow()
        )
        
        # Save document
        success = await metadata_service.create_document(doc_record)
        assert success == True
        
        # Retrieve document
        retrieved_doc = await metadata_service.get_document("test:integration.md")
        assert retrieved_doc is not None
        assert retrieved_doc.doc_id == "test:integration.md"
        assert retrieved_doc.source == "test"
        assert retrieved_doc.hash == "test_hash_123"
        
        # Clean up
        await metadata_service.delete_document("test:integration.md")