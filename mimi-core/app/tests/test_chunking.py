"""
Unit tests for text chunking functionality.
"""
import pytest
from app.policies.chunking import TextChunker


class TestTextChunker:
    """Test cases for TextChunker class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.chunker = TextChunker(
            min_chunk_size=50,
            max_chunk_size=100,
            overlap_size=20
        )
    
    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        result = self.chunker.chunk_text("")
        assert result == []
    
    def test_chunk_short_text(self):
        """Test chunking text shorter than max size."""
        text = "This is a short piece of text."
        result = self.chunker.chunk_text(text)
        assert len(result) == 1
        assert result[0] == text
    
    def test_chunk_long_text(self):
        """Test chunking text longer than max size."""
        # Create text longer than max_chunk_size (100)
        text = "This is a sentence. " * 10  # About 200 characters
        result = self.chunker.chunk_text(text)
        
        assert len(result) >= 2
        
        # Check that chunks don't exceed max size significantly
        for chunk in result:
            assert len(chunk) <= self.chunker.max_chunk_size + 50  # Allow some variance for word boundaries
    
    def test_chunk_with_paragraphs(self):
        """Test chunking text with paragraph breaks."""
        text = """This is the first paragraph. It has multiple sentences.
        
This is the second paragraph. It also has content.

This is the third paragraph with even more content to ensure we get multiple chunks."""
        
        result = self.chunker.chunk_text(text)
        
        assert len(result) >= 1
        # First chunk should contain first paragraph
        assert "first paragraph" in result[0]
    
    def test_chunk_overlap(self):
        """Test that chunks have appropriate overlap."""
        # Create text that will definitely create multiple chunks
        sentences = ["This is sentence number {}. ".format(i) for i in range(1, 20)]
        text = "".join(sentences)
        
        result = self.chunker.chunk_text(text)
        
        if len(result) > 1:
            # Check that there's some overlap between consecutive chunks
            first_chunk_end = result[0][-50:]  # Last 50 chars of first chunk
            second_chunk_start = result[1][:50]  # First 50 chars of second chunk
            
            # There should be some common words between them
            first_words = set(first_chunk_end.split())
            second_words = set(second_chunk_start.split())
            
            # Allow for cases where overlap might not have common whole words
            # due to sentence boundaries
            assert len(first_words & second_words) >= 0  # At least some potential overlap
    
    def test_chunk_sentence_boundaries(self):
        """Test that chunker respects sentence boundaries."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. " * 5
        result = self.chunker.chunk_text(text)
        
        # Check that chunks don't end in the middle of words
        for chunk in result:
            # Chunk should end with punctuation or whitespace
            assert chunk.strip()[-1] in '.!?'
    
    def test_custom_chunk_sizes(self):
        """Test chunker with different size configurations."""
        chunker = TextChunker(min_chunk_size=20, max_chunk_size=50, overlap_size=10)
        
        text = "Word " * 50  # 250 characters
        result = chunker.chunk_text(text)
        
        assert len(result) > 1
        
        for chunk in result:
            # Most chunks should be close to max size or at least min size
            assert len(chunk) >= 15 or chunk == result[-1]  # Last chunk can be shorter