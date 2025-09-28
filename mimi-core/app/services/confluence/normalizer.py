"""
Confluence content normalization for converting storage format to clean text.
"""
import re
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup, NavigableString
from app.infra.logging import get_logger


class ConfluenceNormalizer:
    """Normalizer for Confluence storage format content."""
    
    def __init__(self):
        """Initialize normalizer."""
        self.logger = get_logger("services.confluence.normalizer")
    
    def normalize_content(self, storage_content: str) -> Tuple[str, Optional[str]]:
        """
        Normalize Confluence storage format content to clean text.
        
        Args:
            storage_content: Confluence storage format HTML/XML
            
        Returns:
            Tuple of (normalized_text, detected_language)
        """
        if not storage_content:
            return "", None
        
        try:
            # Parse the storage format content
            soup = BeautifulSoup(storage_content, 'html.parser')
            
            # Remove unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Convert to structured text
            text_parts = []
            self._extract_structured_text(soup, text_parts)
            
            # Clean and format the text
            normalized_text = self._clean_text('\n'.join(text_parts))
            
            # Simple language detection
            detected_lang = self._detect_language(normalized_text)
            
            return normalized_text, detected_lang
            
        except Exception as e:
            self.logger.error(f"Error normalizing content: {e}")
            # Fallback to simple text extraction
            soup = BeautifulSoup(storage_content, 'html.parser')
            return soup.get_text(), None
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup):
        """Remove unwanted elements from the parsed content."""
        # Remove common Confluence macros that don't add meaningful content
        unwanted_selectors = [
            'ac\\:structured-macro[ac\\:name="toc"]',  # Table of contents
            'ac\\:structured-macro[ac\\:name="breadcrumb"]',  # Breadcrumbs
            'ac\\:structured-macro[ac\\:name="pagetree"]',  # Page tree
            'ac\\:structured-macro[ac\\:name="recently-updated"]',  # Recently updated
            'ac\\:structured-macro[ac\\:name="children"]',  # Child pages
            '.confluence-information-macro',  # Info boxes (often noise)
            '.code-header',  # Code block headers
            '.line-numbers',  # Line numbers in code
            '[data-macro-name="toc"]',  # Alternative TOC
            '[data-macro-name="breadcrumb"]',  # Alternative breadcrumb
        ]
        
        for selector in unwanted_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    elem.decompose()
            except Exception:
                # CSS selector might not work with all parsers, continue
                pass
        
        # Also remove by tag name for common unwanted elements
        unwanted_tags = ['script', 'style', 'nav']
        for tag in unwanted_tags:
            for elem in soup.find_all(tag):
                elem.decompose()
    
    def _extract_structured_text(self, soup: BeautifulSoup, text_parts: List[str], heading_level: int = 0):
        """Extract text while preserving structure with headings."""
        for element in soup.children:
            if isinstance(element, NavigableString):
                text = element.strip()
                if text:
                    text_parts.append(text)
            else:
                tag_name = element.name.lower() if element.name else ''
                
                # Handle headings
                if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(tag_name[1])
                    heading_text = element.get_text().strip()
                    if heading_text:
                        # Add heading with appropriate markdown-style prefix
                        prefix = '#' * level
                        text_parts.append(f"\n{prefix} {heading_text}\n")
                
                # Handle paragraphs and divs
                elif tag_name in ['p', 'div']:
                    para_text = element.get_text().strip()
                    if para_text:
                        text_parts.append(f"\n{para_text}\n")
                
                # Handle lists
                elif tag_name in ['ul', 'ol']:
                    self._extract_list_text(element, text_parts)
                
                # Handle tables
                elif tag_name == 'table':
                    table_text = self._extract_table_text(element)
                    if table_text:
                        text_parts.append(f"\n{table_text}\n")
                
                # Handle code blocks
                elif tag_name in ['pre', 'code']:
                    code_text = element.get_text().strip()
                    if code_text:
                        text_parts.append(f"\n```\n{code_text}\n```\n")
                
                # Handle links (preserve link text and URL if meaningful)
                elif tag_name == 'a':
                    link_text = element.get_text().strip()
                    href = element.get('href', '')
                    if link_text and href and href.startswith('http'):
                        text_parts.append(f"[{link_text}]({href})")
                    elif link_text:
                        text_parts.append(link_text)
                
                # Handle images (preserve alt text)
                elif tag_name == 'img':
                    alt_text = element.get('alt', '')
                    if alt_text:
                        text_parts.append(f"(Image: {alt_text})")
                
                # Handle Confluence-specific elements
                elif tag_name == 'ac:structured-macro':
                    self._handle_confluence_macro(element, text_parts)
                
                # For other elements, recurse
                else:
                    self._extract_structured_text(element, text_parts, heading_level)
    
    def _extract_list_text(self, list_element, text_parts: List[str]):
        """Extract text from list elements."""
        text_parts.append("\n")
        for li in list_element.find_all('li', recursive=False):
            li_text = li.get_text().strip()
            if li_text:
                text_parts.append(f"• {li_text}")
        text_parts.append("\n")
    
    def _extract_table_text(self, table_element) -> str:
        """Extract meaningful text from tables."""
        rows = []
        for tr in table_element.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                cell_text = td.get_text().strip()
                if cell_text:
                    cells.append(cell_text)
            if cells:
                rows.append(' | '.join(cells))
        
        if len(rows) <= 3:  # Small table - include all content
            return '\n'.join(rows)
        else:  # Large table - just indicate presence
            return f"(Table with {len(rows)} rows)"
    
    def _handle_confluence_macro(self, macro_element, text_parts: List[str]):
        """Handle Confluence-specific macro elements."""
        macro_name = macro_element.get('ac:name', '')
        
        # Handle code blocks
        if macro_name == 'code':
            # Look for the actual code content
            plain_text = macro_element.find('ac:plain-text-body')
            if plain_text:
                code_text = plain_text.get_text().strip()
                if code_text:
                    text_parts.append(f"\n```\n{code_text}\n```\n")
        
        # Handle info/warning/tip boxes
        elif macro_name in ['info', 'warning', 'note', 'tip']:
            rich_body = macro_element.find('ac:rich-text-body')
            if rich_body:
                body_text = rich_body.get_text().strip()
                if body_text:
                    text_parts.append(f"\n**{macro_name.title()}:** {body_text}\n")
        
        # Handle include/excerpt macros (get the content)
        elif macro_name in ['include', 'excerpt']:
            content = macro_element.get_text().strip()
            if content:
                text_parts.append(f"\n{content}\n")
        
        # For other macros, try to extract any meaningful text
        else:
            macro_text = macro_element.get_text().strip()
            if macro_text and len(macro_text) < 200:  # Avoid very long macro content
                text_parts.append(macro_text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and format the extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines -> double
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces -> single
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)  # Trim lines
        
        # Remove empty lines at start/end
        text = text.strip()
        
        return text
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Simple language detection based on common patterns."""
        # Very basic language detection - could be enhanced with proper language detection library
        if not text:
            return None
        
        # Count English vs non-English characteristics
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        text_lower = text.lower()
        
        english_count = sum(1 for word in english_words if f' {word} ' in text_lower)
        
        if english_count > 2:
            return 'en'
        
        # Could add more language detection logic here
        return None
    
    def extract_sections(self, normalized_text: str) -> List[Tuple[str, str]]:
        """
        Extract sections from normalized text based on headings.
        
        Args:
            normalized_text: Text with markdown-style headings
            
        Returns:
            List of (section_title, section_content) tuples
        """
        sections = []
        lines = normalized_text.split('\n')
        current_section_title = None
        current_section_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Check if this is a heading
            if line.startswith('#'):
                # Save previous section if exists
                if current_section_title and current_section_lines:
                    section_content = '\n'.join(current_section_lines).strip()
                    if section_content:
                        sections.append((current_section_title, section_content))
                
                # Start new section
                current_section_title = line.lstrip('# ').strip()
                current_section_lines = []
            else:
                if line:  # Only add non-empty lines
                    current_section_lines.append(line)
        
        # Add final section
        if current_section_title and current_section_lines:
            section_content = '\n'.join(current_section_lines).strip()
            if section_content:
                sections.append((current_section_title, section_content))
        
        # If no sections found, treat entire text as one section
        if not sections and normalized_text.strip():
            sections.append(("", normalized_text.strip()))
        
        return sections