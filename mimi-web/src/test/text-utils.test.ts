import { describe, it, expect } from 'vitest';
import { 
  generateSnippet, 
  highlightText, 
  isUrl, 
  formatFileSize, 
  generateCitation 
} from '../utils/text';

describe('Text Utils', () => {
  describe('generateSnippet', () => {
    it('should generate a snippet around keyword matches', () => {
      const text = 'This is a long text that contains some important information about React components and their usage in modern applications.';
      const query = 'React components';
      const snippet = generateSnippet(text, query, 50);
      
      expect(snippet).toContain('React');
      expect(snippet.length).toBeLessThanOrEqual(60); // Including ellipsis
    });

    it('should return truncated text when no query matches', () => {
      const text = 'This is some text without matches.';
      const query = 'nonexistent';
      const snippet = generateSnippet(text, query, 10);
      
      expect(snippet.startsWith('This')).toBe(true);
      expect(snippet.endsWith('...')).toBe(true);
    });

    it('should handle empty inputs', () => {
      expect(generateSnippet('', 'query')).toBe('');
      expect(generateSnippet('text', '')).toBe('text');
    });
  });

  describe('highlightText', () => {
    it('should highlight matching words', () => {
      const text = 'The quick brown fox jumps';
      const query = 'quick fox';
      const highlighted = highlightText(text, query);
      
      expect(highlighted).toContain('<mark');
      expect(highlighted).toContain('quick');
      expect(highlighted).toContain('fox');
    });

    it('should be case insensitive', () => {
      const text = 'React Components are great';
      const query = 'react components';
      const highlighted = highlightText(text, query);
      
      expect(highlighted).toContain('<mark');
    });
  });

  describe('isUrl', () => {
    it('should detect valid URLs', () => {
      expect(isUrl('https://example.com')).toBe(true);
      expect(isUrl('http://localhost:3000')).toBe(true);
    });

    it('should reject invalid URLs', () => {
      expect(isUrl('not-a-url')).toBe(false);
      expect(isUrl('ftp://example.com')).toBe(false);
    });
  });

  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1048576)).toBe('1 MB');
    });
  });

  describe('generateCitation', () => {
    it('should generate proper citation format', () => {
      const chunk = {
        chunk_id: 'chunk-123',
        doc_id: 'doc-456',
        source: 'upload',
        path: '/documents/test.pdf',
        score: 0.85,
        snippet: 'Some text...',
      };
      
      const citation = generateCitation(chunk);
      expect(citation).toBe('Source: /documents/test.pdf (doc_id: doc-456)');
    });
  });
});
