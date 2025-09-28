"""
Text normalization policies.
"""
import re
from typing import Optional
from bs4 import BeautifulSoup


class TextNormalizer:
    """Handles text normalization and cleaning."""
    
    def __init__(self):
        # Patterns for common boilerplate elements
        self.nav_patterns = [
            r'<nav[^>]*>.*?</nav>',
            r'<header[^>]*>.*?</header>',
            r'<footer[^>]*>.*?</footer>',
        ]
        
        self.toc_patterns = [
            r'(?i)table\s+of\s+contents?',
            r'(?i)contents?:\s*\n',
            r'(?i)in\s+this\s+article',
        ]
    
    def normalize(self, text: str, format_hint: Optional[str] = None) -> str:
        """
        Normalize text by removing boilerplate and converting HTML to text.
        
        Args:
            text: Raw input text
            format_hint: Optional format hint (html, markdown, etc.)
            
        Returns:
            Normalized text
        """
        # Convert HTML to text if detected or hinted
        if format_hint == "html" or self._is_html(text):
            text = self._html_to_text(text)
        
        # Remove common boilerplate patterns
        text = self._remove_navigation_elements(text)
        text = self._remove_table_of_contents(text)
        
        # Clean up whitespace
        text = self._normalize_whitespace(text)
        
        return text.strip()
    
    def _is_html(self, text: str) -> bool:
        """Check if text appears to be HTML."""
        return bool(re.search(r'<[^>]+>', text))
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        return text
    
    def _remove_navigation_elements(self, text: str) -> str:
        """Remove navigation elements from HTML."""
        for pattern in self.nav_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
        return text
    
    def _remove_table_of_contents(self, text: str) -> str:
        """Remove table of contents sections."""
        for pattern in self.toc_patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Fix line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text