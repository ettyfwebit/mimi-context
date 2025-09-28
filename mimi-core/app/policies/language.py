"""
Language detection policies.
"""
from typing import Optional


class LanguageDetector:
    """Handles language detection for documents."""
    
    def __init__(self):
        """Initialize language detector."""
        self._detector_available = False
        try:
            import langdetect
            self._detector_available = True
        except ImportError:
            pass
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of text content.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Language code (e.g., 'en', 'es') or None if detection fails
        """
        if not self._detector_available or not text.strip():
            return None
        
        try:
            import langdetect
            return langdetect.detect(text)
        except Exception:
            # Language detection can fail on short texts or mixed content
            return None
    
    def is_supported(self) -> bool:
        """Check if language detection is available."""
        return self._detector_available