"""
Tests for Confluence integration functionality.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.models.confluence import (
    ConfluenceFullSyncRequest, ConfluencePage, JobStatus
)
from app.services.confluence import ConfluenceClient, ConfluenceJobManager, ConfluenceSyncWorker


class TestConfluenceClient:
    """Test Confluence client functionality."""
    
    @pytest.fixture
    def mock_confluence_client(self):
        """Create a mock Confluence client."""
        with patch('app.services.confluence.client.ConfluenceClient._is_configured', return_value=True):
            client = ConfluenceClient()
            client.base_url = "https://test.atlassian.net"
            client.auth_token = "test_token"
            return client
    
    @pytest.mark.asyncio
    async def test_discover_pages_by_space(self, mock_confluence_client):
        """Test page discovery by space key."""
        # Mock API response
        mock_response = {
            'results': [
                {
                    'id': '12345',
                    'title': 'Test Page',
                    'space': {'key': 'TEST'},
                    'version': {'number': 1, 'when': '2023-01-01T00:00:00.000Z', 'by': {'displayName': 'Test User'}},
                    'metadata': {'labels': {'results': []}},
                    'ancestors': []
                }
            ]
        }
        
        mock_confluence_client._make_request = AsyncMock(return_value=mock_response)
        
        pages = await mock_confluence_client.discover_pages(space_key="TEST")
        
        assert len(pages) == 1
        assert pages[0].page_id == "12345"
        assert pages[0].title == "Test Page"
        assert pages[0].space_key == "TEST"
    
    @pytest.mark.asyncio
    async def test_fetch_page_content(self, mock_confluence_client):
        """Test fetching page content."""
        mock_response = {
            'id': '12345',
            'title': 'Test Page',
            'space': {'key': 'TEST'},
            'version': {'number': 1, 'when': '2023-01-01T00:00:00.000Z', 'by': {'displayName': 'Test User'}},
            'metadata': {'labels': {'results': []}},
            'ancestors': [],
            'body': {
                'storage': {
                    'value': '<p>This is test content</p>'
                }
            }
        }
        
        mock_confluence_client._make_request = AsyncMock(return_value=mock_response)
        
        page = await mock_confluence_client.fetch_page_content("12345")
        
        assert page is not None
        assert page.content == '<p>This is test content</p>'
    
    def test_should_include_page_filters(self, mock_confluence_client):
        """Test page filtering logic."""
        page = ConfluencePage(
            page_id="12345",
            title="Test Page",
            version=1,
            updated_at=datetime.now(),
            updated_by="Test User",
            space_key="TEST",
            labels=["public", "kb"],
            ancestors=[]
        )
        
        # Test include labels
        assert mock_confluence_client._should_include_page(page, ["public"], [], None)
        assert not mock_confluence_client._should_include_page(page, ["private"], [], None)
        
        # Test exclude labels
        assert not mock_confluence_client._should_include_page(page, [], ["public"], None)
        assert mock_confluence_client._should_include_page(page, [], ["private"], None)


class TestConfluenceJobManager:
    """Test Confluence job manager."""
    
    @pytest.fixture
    def job_manager(self):
        """Create job manager instance."""
        return ConfluenceJobManager()
    
    def test_create_job(self, job_manager):
        """Test job creation."""
        request = ConfluenceFullSyncRequest(
            space_key="TEST",
            max_pages=100,
            max_depth=3,
            dry_run=True
        )
        
        job_id = job_manager.create_job(request)
        
        assert job_id is not None
        assert job_id.startswith("conf-sync-")
        
        status = job_manager.get_job_status(job_id)
        assert status is not None
        assert status.status == JobStatus.QUEUED
        assert status.progress.discovered_pages == 0
    
    def test_update_job_progress(self, job_manager):
        """Test job progress updates."""
        request = ConfluenceFullSyncRequest(space_key="TEST")
        job_id = job_manager.create_job(request)
        
        job_manager.increment_progress(job_id, discovered_pages=5, fetched_pages=3)
        
        status = job_manager.get_job_status(job_id)
        assert status.progress.discovered_pages == 5
        assert status.progress.fetched_pages == 3
    
    def test_cancel_job(self, job_manager):
        """Test job cancellation."""
        request = ConfluenceFullSyncRequest(space_key="TEST")
        job_id = job_manager.create_job(request)
        
        success = job_manager.cancel_job(job_id)
        assert success
        
        status = job_manager.get_job_status(job_id)
        assert status.status == JobStatus.CANCELLED
        assert job_manager.is_job_cancelled(job_id)
    
    def test_add_report_entry(self, job_manager):
        """Test adding report entries."""
        request = ConfluenceFullSyncRequest(space_key="TEST")
        job_id = job_manager.create_job(request)
        
        job_manager.add_report_entry(job_id, "indexed", {
            "page_id": "12345",
            "title": "Test Page",
            "chunks": 3
        })
        
        report = job_manager.get_job_report(job_id, "indexed")
        assert len(report) == 1
        assert report[0]["page_id"] == "12345"


class TestConfluenceNormalizer:
    """Test Confluence content normalization."""
    
    @pytest.fixture
    def normalizer(self):
        """Create normalizer instance."""
        from app.services.confluence.normalizer import ConfluenceNormalizer
        return ConfluenceNormalizer()
    
    def test_normalize_simple_content(self, normalizer):
        """Test normalization of simple HTML content."""
        storage_content = "<p>This is a test paragraph.</p>"
        
        normalized_text, lang = normalizer.normalize_content(storage_content)
        
        assert "This is a test paragraph." in normalized_text
        assert lang is None  # Simple text, no language detection
    
    def test_normalize_with_headings(self, normalizer):
        """Test preservation of heading structure."""
        storage_content = """
        <h1>Main Title</h1>
        <p>Introduction paragraph</p>
        <h2>Section Title</h2>
        <p>Section content</p>
        """
        
        normalized_text, _ = normalizer.normalize_content(storage_content)
        
        assert "# Main Title" in normalized_text
        assert "## Section Title" in normalized_text
        assert "Introduction paragraph" in normalized_text
        assert "Section content" in normalized_text
    
    def test_extract_sections(self, normalizer):
        """Test section extraction from normalized text."""
        normalized_text = """
        # Introduction
        This is the introduction content.
        
        ## Setup
        This explains the setup process.
        
        ### Prerequisites
        List of prerequisites.
        """
        
        sections = normalizer.extract_sections(normalized_text)
        
        assert len(sections) == 3
        assert sections[0][0] == "Introduction"
        assert "introduction content" in sections[0][1]
        assert sections[1][0] == "Setup"
        assert "setup process" in sections[1][1]
    
    def test_remove_unwanted_elements(self, normalizer):
        """Test removal of TOC and other unwanted elements."""
        storage_content = """
        <ac:structured-macro ac:name="toc">
            <ac:parameter ac:name="maxLevel">3</ac:parameter>
        </ac:structured-macro>
        <p>Actual content here</p>
        <script>alert('malicious')</script>
        """
        
        normalized_text, _ = normalizer.normalize_content(storage_content)
        
        assert "Actual content here" in normalized_text
        assert "toc" not in normalized_text.lower()
        assert "script" not in normalized_text.lower()
        assert "malicious" not in normalized_text


class TestConfluenceSyncWorker:
    """Test Confluence sync worker."""
    
    @pytest.fixture
    def sync_worker(self):
        """Create sync worker instance."""
        return ConfluenceSyncWorker()
    
    @pytest.fixture
    def mock_job_manager(self):
        """Create mock job manager."""
        job_manager = MagicMock()
        job_manager.is_job_cancelled.return_value = False
        job_manager.get_job_request.return_value = ConfluenceFullSyncRequest(
            space_key="TEST",
            dry_run=False
        )
        return job_manager
    
    def test_chunk_text_by_size(self, sync_worker):
        """Test text chunking logic."""
        text = "This is a long text that should be chunked into smaller pieces when it exceeds the target size limit."
        
        chunks = sync_worker._chunk_text_by_size(text, target_size=50, overlap=10)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 60 for chunk in chunks)  # Allow for some overlap
        
        # Test that chunks have overlap
        if len(chunks) > 1:
            # Some words should appear in multiple chunks due to overlap
            combined = " ".join(chunks)
            assert len(combined) > len(text)  # Due to overlap
    
    @pytest.mark.asyncio
    async def test_create_confluence_chunks(self, sync_worker):
        """Test Confluence-specific chunk creation."""
        page = ConfluencePage(
            page_id="12345",
            title="Test Page",
            version=1,
            updated_at=datetime.now(),
            updated_by="Test User",
            space_key="TEST",
            labels=["public"],
            ancestors=["Parent Page"],
            url="https://test.atlassian.net/pages/12345"
        )
        
        normalized_text = """
        # Section 1
        This is the content of section 1 with enough text to create multiple chunks.
        
        # Section 2  
        This is the content of section 2 with more text content.
        """
        
        content_hash = "test_hash"
        detected_lang = "en"
        
        chunks = await sync_worker._create_confluence_chunks(
            page, normalized_text, content_hash, detected_lang
        )
        
        assert len(chunks) > 0
        
        # Check chunk metadata
        first_chunk = chunks[0]
        assert first_chunk.metadata["source"] == "confluence"
        assert first_chunk.metadata["space_key"] == "TEST"
        assert first_chunk.metadata["page_id"] == "12345"
        assert first_chunk.metadata["page_title"] == "Test Page"
        assert first_chunk.metadata["labels"] == ["public"]
        assert first_chunk.metadata["ancestors"] == ["Parent Page"]
        assert first_chunk.metadata["lang"] == "en"
        assert first_chunk.metadata["hash"] == "test_hash"


if __name__ == "__main__":
    pytest.main([__file__])