# website_extractor.py
import re
import json
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from functools import lru_cache
from config import (
    DEFAULT_USER_AGENT, REQUEST_TIMEOUT, 
    EXCLUDE_PATTERNS, PRIORITY_PATTERNS
)

class WebsiteExtractor:
    def __init__(self, base_url):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.all_links = []
        self.filtered_links = []
        self.visited_urls = set()
        
        # Persistent session for connection reuse
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': DEFAULT_USER_AGENT})
        
        # Precompile URL regex pattern
        self.url_pattern = re.compile(r'https?://[^\s\'"]+|/[^\s\'"]+')
        
        # Filtering patterns
        self.exclude_patterns = EXCLUDE_PATTERNS
        self.priority_patterns = PRIORITY_PATTERNS
    
    @lru_cache(maxsize=32)
    def _get_soup(self, url=None):
        """Get BeautifulSoup with cache using lru_cache decorator"""
        if url is None:
            url = self.base_url
            
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
            
    def get_page_content(self, url=None):
        """Extract text content from a page"""
        soup = self._get_soup(url)
        if not soup:
            return ""
        
        # Remove script and style elements
        for tag in soup.select('script, style'):
            tag.decompose()
            
        # Get text with space separator and strip whitespace
        text = soup.get_text(separator=' ', strip=True)
        
        # Normalize whitespace
        return re.sub(r'\s+', ' ', text).strip()
    
    def extract_links(self, url=None):
        """Extract links using all available extractors"""
        soup = self._get_soup(url)
        if not soup:
            return []
            
        links = set()
        current_url = url if url else self.base_url
        
        # Run all extractors
        extractors = [
            self._extract_a_tags,
            self._extract_data_attributes,
            self._extract_json_structures,
            self._extract_from_scripts
        ]
        
        for extractor in extractors:
            try:
                found_links = extractor(soup)
                links.update(found_links)
            except Exception as e:
                logging.error(f"Error in extractor {extractor.__name__}: {e}")
        
        # Convert to absolute URLs
        absolute_links = [urljoin(current_url, link) for link in links]
        self.all_links = list(set(absolute_links))
        return self.all_links
    
    def _extract_a_tags(self, soup):
        """Basic extractor for <a> tags"""
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href and not href.startswith(('javascript:', '#', 'mailto:', 'tel:')):
                links.add(href)
        return links
    
    def _extract_data_attributes(self, soup):
        """Extract URLs from data-* attributes"""
        links = set()
        for tag in soup.find_all(True):
            for attr, value in tag.attrs.items():
                if isinstance(value, str) and ('/' in value or 'http' in value):
                    urls = self.url_pattern.findall(value)
                    links.update(urls)
        return links
    
    def _extract_json_structures(self, soup):
        """Extract URLs from JSON structures in attributes"""
        links = set()
        
        # Look for attributes that might contain JSON
        json_attrs = ['data-props', 'data-json', 'data-config', 'data-settings']
        
        for attr in json_attrs:
            for tag in soup.find_all(attrs={attr: True}):
                try:
                    data = json.loads(tag[attr])
                    links.update(self._extract_urls_from_obj(data))
                except Exception:
                    pass
        return links
    
    def _extract_from_scripts(self, soup):
        """Extract URLs from scripts"""
        links = set()
        for script in soup.find_all('script'):
            if script.string:
                urls = self.url_pattern.findall(script.string)
                links.update(urls)
        return links
    
    def _extract_urls_from_obj(self, obj):
        """Extract URLs from JSON objects recursively"""
        links = set()
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['href', 'url', 'link', 'src'] and isinstance(value, str) and value and not value.startswith('#'):
                    links.add(value)
                elif isinstance(value, (dict, list)):
                    links.update(self._extract_urls_from_obj(value))
        elif isinstance(obj, list):
            for item in obj:
                links.update(self._extract_urls_from_obj(item))
        return links
    
    def filter_links(self):
        """Filter links by domain and patterns"""
        # Filter by same domain
        domain_links = [link for link in self.all_links if self.domain in urlparse(link).netloc]
        
        # Exclude unwanted files and pages
        filtered = []
        for link in domain_links:
            if not any(exclude.lower() in link.lower() for exclude in self.exclude_patterns):
                filtered.append(link)
        
        # Prioritize important links
        priority = []
        regular = []
        
        for link in filtered:
            if any(pattern in link.lower() for pattern in self.priority_patterns):
                priority.append(link)
            else:
                regular.append(link)
                
        self.filtered_links = priority + regular
        logging.info(f"Filtered links: {len(self.filtered_links)} (out of {len(self.all_links)} total)")
        return self.filtered_links