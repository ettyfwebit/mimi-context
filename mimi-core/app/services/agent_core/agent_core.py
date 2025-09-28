"""
Main agent core service for orchestrating RAG queries and LLM responses.
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.agent import AgentResponse, CitationItem, ConversationTurn, ConversationMemory
from app.services.agent_core.rag_client import RagClient
from app.services.agent_core.llm_client import LLMClient, create_llm_client
from app.infra.logging import get_logger

logger = get_logger("services.agent_core.agent_core")


class AgentCore:
    """Main agent service for handling conversational queries."""
    
    def __init__(
        self,
        rag_client: RagClient,
        llm_client: LLMClient,
        enable_memory: bool = False,
        memory_size: int = 3
    ):
        self.rag_client = rag_client
        self.llm_client = llm_client
        self.enable_memory = enable_memory
        self.memory_size = memory_size
        self.conversation_memory: Dict[str, ConversationMemory] = {}
    
    def _build_prompt(
        self, 
        question: str, 
        chunks: List[Dict[str, Any]], 
        conversation_history: Optional[List[ConversationTurn]] = None
    ) -> str:
        """
        Build the prompt for the LLM including context from chunks and conversation history.
        
        Args:
            question: User's question
            chunks: Retrieved chunks from RAG
            conversation_history: Previous conversation turns
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Add conversation context if available
        if conversation_history and len(conversation_history) > 0:
            prompt_parts.append("## Previous Conversation Context:")
            for turn in conversation_history[-self.memory_size:]:
                prompt_parts.append(f"Q: {turn.question}")
                prompt_parts.append(f"A: {turn.answer}")
                prompt_parts.append("")
        
        # Add retrieved context
        prompt_parts.append("## Context Information:")
        if chunks:
            for i, chunk in enumerate(chunks, 1):
                doc_id = chunk.get("doc_id", "unknown")
                # Use full_text if available, otherwise fall back to snippet
                text_content = chunk.get("full_text") or chunk.get("snippet", "")
                prompt_parts.append(f"Document {i} (ID: {doc_id}):")
                prompt_parts.append(text_content)
                prompt_parts.append("")
        else:
            prompt_parts.append("No relevant context found.")
            prompt_parts.append("")
        
        # Add the main instruction
        prompt_parts.extend([
            "## Instructions:",
            "You are a helpful assistant that answers the current user question based only on the provided context.",
            "Answer in 3-6 sentences maximum, using clear and concise natural language.",
            "Paraphrase the information in your own words - do not copy-paste entire sections.",
            "Do not use enumerated lists or bullet points; write in prose.",
            "Place numeric citations [1], [2] inline only at key points where you reference specific documents.",
            "Use each citation marker only once or twice - do not repeat in every sentence.",
            "Always include at least one citation marker in your answer.",
            "At the end of the answer, always include a 'Sources:' line mapping markers to their document paths.",
            "If the context doesn't contain enough information, say clearly: 'I don't have enough information to answer.'",
            "",
            f"## User Question:\n{question}\n",
            "## Answer:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_citations(self, chunks: List[Dict[str, Any]]) -> List[CitationItem]:
        """Extract citation information from chunks."""
        citations = []
        for chunk in chunks:
            doc_id = chunk.get("doc_id", "")
            path = chunk.get("path")
            if doc_id:
                citations.append(CitationItem(doc_id=doc_id, path=path))
        return citations
    
    def _deduplicate_chunks_by_source(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate chunks by doc_id + path combination, keeping the first occurrence.
        
        Args:
            chunks: List of chunks to deduplicate
            
        Returns:
            List of unique chunks by source
        """
        seen_sources = set()
        unique_chunks = []
        
        for chunk in chunks:
            doc_id = chunk.get("doc_id", "")
            path = chunk.get("path", "")
            source_key = (doc_id, path)
            
            if source_key not in seen_sources and doc_id:
                seen_sources.add(source_key)
                unique_chunks.append(chunk)
        
        return unique_chunks

    def _format_answer_with_sources(self, answer: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Format the answer to include Sources section with deduplicated citations.
        
        Args:
            answer: Raw answer from LLM
            chunks: Retrieved chunks used for context
            
        Returns:
            Formatted answer with Sources section
        """
        import re
        
        if not chunks:
            return answer
        
        # Clean the answer - remove any trailing whitespace
        formatted_answer = answer.strip()
        
        # Find which citation numbers were actually used in the answer
        citation_pattern = r'\[(\d+)\]'
        used_citation_nums = set()
        
        for match in re.finditer(citation_pattern, formatted_answer):
            try:
                citation_num = int(match.group(1))
                if 1 <= citation_num <= len(chunks):
                    used_citation_nums.add(citation_num)
            except ValueError:
                continue
        
        # If no citations found, include all chunks but deduplicated
        if not used_citation_nums:
            # Deduplicate all chunks
            unique_chunks = self._deduplicate_chunks_by_source(chunks)
            # Update answer to reference [1] if no citations were used
            if unique_chunks:
                formatted_answer += " [1]"
        else:
            # Get only the chunks that were actually cited
            cited_chunks = []
            for num in sorted(used_citation_nums):
                idx = num - 1  # Convert to 0-based index
                if 0 <= idx < len(chunks):
                    cited_chunks.append(chunks[idx])
            
            # Deduplicate the cited chunks
            unique_chunks = self._deduplicate_chunks_by_source(cited_chunks)
            
            # Update citation numbers in answer to match deduplicated sources
            if len(unique_chunks) < len(cited_chunks):
                # Need to remap citations since we deduplicated
                # Create mapping from original chunks to unique chunks
                chunk_to_unique_idx = {}
                for i, chunk in enumerate(cited_chunks):
                    doc_id = chunk.get("doc_id", "")
                    path = chunk.get("path", "")
                    
                    # Find this chunk in unique_chunks
                    for j, unique_chunk in enumerate(unique_chunks):
                        if (unique_chunk.get("doc_id", "") == doc_id and 
                            unique_chunk.get("path", "") == path):
                            chunk_to_unique_idx[i] = j + 1  # 1-based for display
                            break
                
                # Replace citations in answer to match unique numbering
                def replace_citation(match):
                    try:
                        orig_num = int(match.group(1))
                        chunk_idx = orig_num - 1
                        if chunk_idx in chunk_to_unique_idx:
                            return f"[{chunk_to_unique_idx[chunk_idx]}]"
                        return match.group(0)
                    except (ValueError, KeyError):
                        return match.group(0)
                
                formatted_answer = re.sub(citation_pattern, replace_citation, formatted_answer)
        
        if not unique_chunks:
            return formatted_answer
        
        # Add Sources section
        sources_lines = ["\n\nSources:"]
        for i, chunk in enumerate(unique_chunks, 1):
            doc_id = chunk.get("doc_id", "unknown")
            source_line = f"[{i}] {doc_id}"
            sources_lines.append(source_line)
        
        formatted_answer += "\n".join(sources_lines)
        return formatted_answer
    
    def _get_conversation_history(self, session_id: str) -> Optional[List[ConversationTurn]]:
        """Get conversation history for a session."""
        if not self.enable_memory or not session_id:
            return None
        
        memory = self.conversation_memory.get(session_id)
        return memory.turns if memory else None
    
    def _save_conversation_turn(self, session_id: str, question: str, answer: str):
        """Save a conversation turn to memory."""
        if not self.enable_memory or not session_id:
            return
        
        turn = ConversationTurn(
            question=question,
            answer=answer,
            timestamp=datetime.utcnow().isoformat()
        )
        
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = ConversationMemory(
                session_id=session_id,
                turns=[]
            )
        
        memory = self.conversation_memory[session_id]
        memory.turns.append(turn)
        
        # Keep only the last N turns
        if len(memory.turns) > self.memory_size:
            memory.turns = memory.turns[-self.memory_size:]
        
        logger.info(f"Saved conversation turn for session {session_id}")
    
    async def process_query(
        self, 
        question: str, 
        top_k: int = 3, 
        session_id: Optional[str] = None
    ) -> AgentResponse:
        """
        Process a user query through the complete RAG + LLM pipeline.
        
        Args:
            question: User's natural language question
            top_k: Number of top chunks to retrieve
            session_id: Optional session ID for conversation memory
            
        Returns:
            AgentResponse with answer, citations, and raw chunks
        """
        try:
            logger.info(f"Processing query: {question}")
            
            # Step 1: Query RAG for relevant chunks
            chunks = await self.rag_client.query(question, top_k)
            
            # Step 2: Get conversation history if memory is enabled
            conversation_history = self._get_conversation_history(session_id)
            
            # Step 3: Build prompt with context and history
            prompt = self._build_prompt(question, chunks, conversation_history)
            
            # Step 4: Generate response using LLM
            raw_answer = await self.llm_client.generate_response(prompt)
            
            # Step 5: Format answer with Sources section
            formatted_answer = self._format_answer_with_sources(raw_answer, chunks)
            
            # Step 6: Extract citations (for backward compatibility)
            citations = self._extract_citations(chunks)
            
            # Step 7: Save to conversation memory if enabled (use raw answer for memory)
            self._save_conversation_turn(session_id, question, raw_answer)
            
            logger.info(f"Successfully processed query with {len(chunks)} chunks and {len(citations)} citations")
            
            return AgentResponse(
                answer=formatted_answer,
                citations=citations,
                raw_chunks=chunks
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Return a graceful error response
            return AgentResponse(
                answer="I apologize, but I encountered an error while processing your question. Please try again.",
                citations=[],
                raw_chunks=[]
            )


def create_agent_core(
    rag_endpoint_url: str = "http://localhost:8080/rag/query",
    backend: str = "openai",
    openai_api_key: Optional[str] = None,
    openai_model: str = "gpt-4o-mini",
    ollama_base_url: str = "http://localhost:11434",
    ollama_model: str = "mistral",
    temperature: float = 0.7,
    max_tokens: int = 1000,
    enable_memory: bool = False,
    memory_size: int = 3
) -> AgentCore:
    """Factory function to create a configured AgentCore instance."""
    
    rag_client = RagClient(rag_endpoint_url)
    
    llm_client = create_llm_client(
        backend=backend,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return AgentCore(
        rag_client=rag_client,
        llm_client=llm_client,
        enable_memory=enable_memory,
        memory_size=memory_size
    )