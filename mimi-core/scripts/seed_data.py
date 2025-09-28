#!/usr/bin/env python3
"""
Seed script to add sample documents for testing.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import IngestInput, DocumentRecord, EventRecord
from app.services.pipeline_core import DocumentProcessor
from app.services.metadata import MetadataService
from app.infra.logging import setup_logger, get_logger
from app.infra.config import get_settings


SAMPLE_DOCUMENTS = [
    {
        "filename": "booking_guide.md",
        "content": """# Ticket Booking Guide

## How to Book a Ticket

To book a ticket in our system, follow these simple steps:

1. **Select Your Destination**: Navigate to the booking page and choose your desired destination from the dropdown menu.

2. **Choose Travel Dates**: Pick your departure and return dates using the calendar widget.

3. **Select Passengers**: Add passenger information including names and age categories.

4. **Payment**: Complete the booking by providing payment information and confirming your purchase.

## Booking Policies

- Tickets can be booked up to 6 months in advance
- Changes to bookings are allowed up to 24 hours before departure
- Cancellation fees may apply depending on the ticket type

## Customer Support

If you need help with booking, contact our support team at support@example.com or call 1-800-TICKETS.
""",
        "lang": "en"
    },
    {
        "filename": "system_overview.md", 
        "content": """# System Overview

## Mimi Core Features

Mimi Core is an intelligent document management and retrieval system that provides:

### Document Processing
- Automatic text extraction and normalization
- Intelligent chunking for optimal search performance
- Duplicate detection and deduplication
- Multi-language support

### Search Capabilities
- Semantic search using vector embeddings
- Contextual snippet extraction
- Relevance scoring and ranking
- Filter-based queries

### Administrative Features
- Document management and tracking
- Event logging and monitoring
- System health monitoring
- Usage analytics

## Architecture

The system is built with a modular architecture supporting:
- FastAPI-based REST API
- Vector storage (Qdrant/OpenAI)
- SQLite metadata storage
- Configurable processing policies

This design enables easy scaling and migration to microservices as needed.
""",
        "lang": "en"
    },
    {
        "filename": "faq.md",
        "content": """# Frequently Asked Questions

## General Questions

**Q: What file formats are supported?**
A: The system currently supports plain text (.txt) and Markdown (.md) files. PDF support is planned for future releases.

**Q: How large can uploaded documents be?**
A: The default maximum file size is 10MB. This can be configured by administrators.

**Q: Is there a limit on the number of documents?**
A: There are no hard limits on document count, but performance may vary based on your vector storage configuration.

## Technical Questions

**Q: How does the search work?**
A: The system uses semantic search powered by OpenAI embeddings and vector similarity matching to find relevant content.

**Q: Can I search in multiple languages?**  
A: Yes, the system supports multi-language documents and can detect document language automatically.

**Q: How is duplicate content handled?**
A: The system automatically detects and skips duplicate documents based on content hashing.

## Troubleshooting

**Q: Why isn't my document showing up in search results?**
A: Check that the document was successfully ingested by viewing the admin panel. Also ensure your search query is relevant to the document content.

**Q: What should I do if upload fails?**
A: Verify the file format is supported, the file size is under the limit, and the file is UTF-8 encoded text.
""",
        "lang": "en"
    }
]


async def seed_documents():
    """Seed the database with sample documents."""
    
    # Setup logging
    settings = get_settings()
    setup_logger(settings.app_env)
    logger = get_logger("scripts.seed")
    
    logger.info("Starting document seeding...")
    
    try:
        # Initialize services
        metadata_service = MetadataService()
        await metadata_service.initialize()
        
        processor = DocumentProcessor()
        
        # Process each sample document
        for doc_data in SAMPLE_DOCUMENTS:
            doc_id = f"seed:{doc_data['filename']}"
            
            logger.info(f"Processing document: {doc_id}")
            
            # Check if document already exists
            existing_doc = await metadata_service.get_document(doc_id)
            if existing_doc:
                logger.info(f"Document {doc_id} already exists, skipping")
                continue
            
            # Create ingest input
            ingest_input = IngestInput(
                doc_id=doc_id,
                source="seed",
                path=f"samples/{doc_data['filename']}",
                text=doc_data["content"],
                lang=doc_data.get("lang")
            )
            
            # Process document
            chunks = processor.process_document(ingest_input)
            
            # Compute hash
            content_hash = processor.compute_document_hash(doc_data["content"])
            
            # Create document record
            doc_record = DocumentRecord(
                doc_id=doc_id,
                source="seed",
                path=f"samples/{doc_data['filename']}",
                hash=content_hash,
                lang=doc_data.get("lang"),
                updated_at=datetime.utcnow()
            )
            
            # Save to metadata store
            await metadata_service.create_document(doc_record)
            await metadata_service.save_chunks(chunks)
            
            # Log event
            await metadata_service.create_event(EventRecord(
                type="seed",
                ref=doc_id,
                status="success",
                details={"chunks_created": len(chunks)},
                created_at=datetime.utcnow()
            ))
            
            print(f"✓ Seeded document: {doc_data['filename']} ({len(chunks)} chunks)")
        
        logger.info("Document seeding completed successfully")
        print(f"\n✓ Seeding completed! Added {len(SAMPLE_DOCUMENTS)} sample documents.")
        print("Note: Vector embeddings are created when documents are uploaded via the API.")
        
    except Exception as e:
        logger.error(f"Document seeding failed: {e}")
        print(f"✗ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_documents())