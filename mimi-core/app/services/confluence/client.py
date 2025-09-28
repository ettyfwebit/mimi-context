"""
Confluence REST API client for fetching pages and metadata.
"""
import asyncio
import aiohttp
import re
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from urllib.parse import urljoin, quote
from app.models.confluence import ConfluencePage
from app.infra.config import get_settings
from app.infra.logging import get_logger


class ConfluenceClient:
    """Client for interacting with Confluence REST API."""
    
    def __init__(self):
        """Initialize Confluence client."""
        self.settings = get_settings()
        self.logger = get_logger("services.confluence.client")
        self.base_url = self.settings.confluence_base_url
        self.auth_token = self.settings.confluence_auth_token
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.base_url or not self.auth_token:
            self.logger.warning("Confluence configuration incomplete - client disabled")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _ensure_session(self):
        """Ensure HTTP session exists."""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
    
    def _is_configured(self) -> bool:
        """Check if Confluence client is properly configured."""
        return bool(self.base_url and self.auth_token)
    
    async def _make_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Confluence API with retry logic."""
        if not self._is_configured():
            raise ValueError("Confluence client not properly configured")
        
        await self._ensure_session()
        url = urljoin(self.base_url, f"/rest/api/{path}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 429:
                        # Rate limited - exponential backoff
                        wait_time = (2 ** attempt) + (attempt * 0.1)  # Add jitter
                        self.logger.warning(f"Rate limited, waiting {wait_time}s (attempt {attempt + 1})")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if response.status >= 500:
                        # Server error - retry
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt)
                            self.logger.warning(f"Server error {response.status}, retrying in {wait_time}s")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    if response.status >= 400:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=error_text
                        )
                    
                    return await response.json()
            
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    self.logger.warning(f"Request failed: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise
        
        raise Exception(f"Max retries ({max_retries}) exceeded")
    
    async def discover_pages(
        self, 
        space_key: Optional[str] = None,
        root_page_id: Optional[str] = None,
        include_labels: List[str] = None,
        exclude_labels: List[str] = None,
        path_prefix: Optional[str] = None,
        max_pages: int = 2000,
        max_depth: int = 5
    ) -> List[ConfluencePage]:
        """
        Discover pages based on scope and filters.
        
        Args:
            space_key: Space to search (alternative to root_page_id)
            root_page_id: Root page ID to start from (alternative to space_key)
            include_labels: Only include pages with these labels
            exclude_labels: Exclude pages with these labels
            path_prefix: Optional path prefix filter
            max_pages: Maximum number of pages to discover
            max_depth: Maximum traversal depth
            
        Returns:
            List of discovered pages
        """
        include_labels = include_labels or []
        exclude_labels = exclude_labels or []
        
        self.logger.info(
            f"Discovering pages: space={space_key}, root={root_page_id}, "
            f"include_labels={include_labels}, exclude_labels={exclude_labels}, "
            f"max_pages={max_pages}, max_depth={max_depth}"
        )
        
        discovered_pages = []
        visited_ids: Set[str] = set()
        
        if space_key:
            # Start with space discovery
            discovered_pages.extend(await self._discover_by_space(
                space_key, include_labels, exclude_labels, path_prefix, max_pages, visited_ids
            ))
        elif root_page_id:
            # Start with page hierarchy discovery
            discovered_pages.extend(await self._discover_by_hierarchy(
                root_page_id, include_labels, exclude_labels, path_prefix, 
                max_pages, max_depth, visited_ids, current_depth=0
            ))
        else:
            raise ValueError("Either space_key or root_page_id must be provided")
        
        self.logger.info(f"Discovered {len(discovered_pages)} pages")
        return discovered_pages[:max_pages]
    
    async def _discover_by_space(
        self,
        space_key: str,
        include_labels: List[str],
        exclude_labels: List[str],
        path_prefix: Optional[str],
        max_pages: int,
        visited_ids: Set[str]
    ) -> List[ConfluencePage]:
        """Discover pages within a space."""
        pages = []
        start = 0
        limit = 50
        
        while len(pages) < max_pages:
            params = {
                'spaceKey': space_key,
                'limit': limit,
                'start': start,
                'expand': 'version,metadata.labels,ancestors'
            }
            
            try:
                response = await self._make_request('GET', 'content', params=params)
                results = response.get('results', [])
                
                if not results:
                    break
                
                for page_data in results:
                    if page_data['id'] in visited_ids:
                        continue
                    
                    page = await self._parse_page_data(page_data)
                    if page and self._should_include_page(page, include_labels, exclude_labels, path_prefix):
                        pages.append(page)
                        visited_ids.add(page.page_id)
                
                start += limit
                
            except Exception as e:
                self.logger.error(f"Error discovering pages in space {space_key}: {e}")
                break
        
        return pages
    
    async def _discover_by_hierarchy(
        self,
        page_id: str,
        include_labels: List[str],
        exclude_labels: List[str],
        path_prefix: Optional[str],
        max_pages: int,
        max_depth: int,
        visited_ids: Set[str],
        current_depth: int
    ) -> List[ConfluencePage]:
        """Discover pages by traversing hierarchy from root page."""
        if current_depth > max_depth or len(visited_ids) >= max_pages:
            return []
        
        if page_id in visited_ids:
            return []
        
        pages = []
        
        try:
            # Get page details
            params = {'expand': 'version,metadata.labels,ancestors'}
            page_data = await self._make_request('GET', f'content/{page_id}', params=params)
            page = await self._parse_page_data(page_data)
            
            if page and self._should_include_page(page, include_labels, exclude_labels, path_prefix):
                pages.append(page)
                visited_ids.add(page_id)
            
            # Get child pages
            if current_depth < max_depth:
                child_params = {'limit': 50, 'expand': 'version,metadata.labels,ancestors'}
                children_response = await self._make_request('GET', f'content/{page_id}/child/page', params=child_params)
                
                for child_data in children_response.get('results', []):
                    child_pages = await self._discover_by_hierarchy(
                        child_data['id'], include_labels, exclude_labels, path_prefix,
                        max_pages, max_depth, visited_ids, current_depth + 1
                    )
                    pages.extend(child_pages)
                    
                    if len(visited_ids) >= max_pages:
                        break
        
        except Exception as e:
            self.logger.error(f"Error discovering page hierarchy for {page_id}: {e}")
        
        return pages
    
    async def fetch_page_content(self, page_id: str) -> Optional[ConfluencePage]:
        """
        Fetch full content for a specific page.
        
        Args:
            page_id: Confluence page ID
            
        Returns:
            Page with content or None if error
        """
        try:
            params = {
                'expand': 'body.storage,version,metadata.labels,ancestors'
            }
            page_data = await self._make_request('GET', f'content/{page_id}', params=params)
            
            page = await self._parse_page_data(page_data, include_content=True)
            return page
            
        except Exception as e:
            self.logger.error(f"Error fetching content for page {page_id}: {e}")
            return None
    
    async def _parse_page_data(self, page_data: Dict[str, Any], include_content: bool = False) -> Optional[ConfluencePage]:
        """Parse Confluence page data into ConfluencePage model."""
        try:
            # Extract basic fields
            page_id = page_data['id']
            title = page_data['title']
            version_data = page_data.get('version', {})
            version = version_data.get('number', 1)
            updated_at_str = version_data.get('when', '')
            updated_by = version_data.get('by', {}).get('displayName', 'Unknown')
            space_key = page_data.get('space', {}).get('key', '')
            
            # Parse timestamp
            updated_at = datetime.now()
            if updated_at_str:
                try:
                    # Confluence timestamps are ISO format
                    updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                except ValueError:
                    self.logger.warning(f"Could not parse timestamp: {updated_at_str}")
            
            # Extract labels
            labels = []
            metadata = page_data.get('metadata', {})
            labels_data = metadata.get('labels', {}).get('results', [])
            for label_data in labels_data:
                labels.append(label_data.get('name', ''))
            
            # Extract ancestors (page hierarchy)
            ancestors = []
            ancestors_data = page_data.get('ancestors', [])
            for ancestor in ancestors_data:
                ancestors.append(ancestor.get('title', ''))
            
            # Extract content if requested
            content = None
            if include_content:
                body = page_data.get('body', {})
                storage = body.get('storage', {})
                content = storage.get('value', '')
            
            # Build URL
            url = f"{self.base_url}/pages/{page_id}" if self.base_url else None
            
            return ConfluencePage(
                page_id=page_id,
                title=title,
                version=version,
                updated_at=updated_at,
                updated_by=updated_by,
                space_key=space_key,
                labels=labels,
                ancestors=ancestors,
                content=content,
                url=url
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing page data: {e}")
            return None
    
    def _should_include_page(
        self,
        page: ConfluencePage,
        include_labels: List[str],
        exclude_labels: List[str],
        path_prefix: Optional[str]
    ) -> bool:
        """Check if page should be included based on filters."""
        # Check exclude labels first
        if exclude_labels:
            for exclude_label in exclude_labels:
                if exclude_label in page.labels:
                    return False
        
        # Check include labels
        if include_labels:
            has_included_label = False
            for include_label in include_labels:
                if include_label in page.labels:
                    has_included_label = True
                    break
            if not has_included_label:
                return False
        
        # Check path prefix
        if path_prefix:
            page_path = page.url or f"{page.space_key}/{page.title}"
            if not page_path.startswith(path_prefix):
                return False
        
        return True