"""
HTML language parser for extracting web document entities.
"""

import os
import re
from typing import List, Set, Optional
import logging

from ..base import BaseFileParser, ParseResult, EntityType

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup, Tag
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logger.warning("BeautifulSoup4 not available, HTML parsing will be limited")


class HTMLParser(BaseFileParser):
    """Parser for HTML files."""
    
    def __init__(self):
        super().__init__({'.html', '.htm', '.xhtml'}, "HTML")
        self.parser_version = "1.0.0"
        
        # Regex patterns for HTML parsing (fallback when BS4 not available)
        self.patterns = {
            'tag': re.compile(r'<(\w+)(?:\s+[^>]*)?>.*?</\1>', re.DOTALL | re.IGNORECASE),
            'self_closing': re.compile(r'<(\w+)(?:\s+[^>]*)?/>', re.IGNORECASE),
            'css_link': re.compile(r'<link[^>]*href=["\']([^"\']*\.css)["\']', re.IGNORECASE),
            'js_script': re.compile(r'<script[^>]*src=["\']([^"\']*\.js)["\']', re.IGNORECASE),
            'inline_css': re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE),
            'inline_js': re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE),
            'id_attr': re.compile(r'id=["\']([^"\']+)["\']', re.IGNORECASE),
            'class_attr': re.compile(r'class=["\']([^"\']+)["\']', re.IGNORECASE),
        }
    
    def parse_file(self, file_path: str) -> List[ParseResult]:
        """Parse an HTML file and extract entities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            results = []
            lines = content.splitlines()
            
            # Add file entity
            file_result = ParseResult(
                name=os.path.basename(file_path),
                entity_type=EntityType.FILE,
                file_path=file_path,
                line_start=1,
                line_end=len(lines),
                content=content[:500] + "..." if len(content) > 500 else content,
                metadata={'language': 'html', 'size': len(content)}
            )
            results.append(file_result)
            
            if HAS_BS4:
                results.extend(self._parse_with_bs4(content, file_path, lines))
            else:
                results.extend(self._parse_with_regex(content, file_path, lines))
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing HTML file {file_path}: {e}")
            return []
    
    def extract_dependencies(self, file_path: str) -> List[str]:
        """Extract CSS and JS dependencies from HTML."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Extract CSS links
            css_matches = self.patterns['css_link'].findall(content)
            dependencies.extend(css_matches)
            
            # Extract JS scripts
            js_matches = self.patterns['js_script'].findall(content)
            dependencies.extend(js_matches)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Error extracting dependencies from {file_path}: {e}")
            return []
    
    def get_supported_entity_types(self) -> List[EntityType]:
        """Get supported entity types for HTML."""
        return [
            EntityType.FILE,
            EntityType.HTML_ELEMENT
        ]
    
    def _parse_with_bs4(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Parse HTML using BeautifulSoup4."""
        results = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract significant elements
            significant_tags = ['html', 'head', 'body', 'header', 'nav', 'main', 
                              'section', 'article', 'aside', 'footer', 'div', 'form']
            
            for tag_name in significant_tags:
                elements = soup.find_all(tag_name)
                for i, element in enumerate(elements):
                    result = self._create_element_result(element, tag_name, i, file_path, content, lines)
                    if result:
                        results.append(result)
            
            # Extract elements with IDs
            id_elements = soup.find_all(attrs={'id': True})
            for element in id_elements:
                if element.name not in significant_tags:  # Avoid duplicates
                    result = self._create_element_result(element, element.name, 0, file_path, content, lines, use_id=True)
                    if result:
                        results.append(result)
        
        except Exception as e:
            logger.error(f"Error parsing HTML with BeautifulSoup: {e}")
            # Fallback to regex parsing
            results.extend(self._parse_with_regex(content, file_path, lines))
        
        return results
    
    def _create_element_result(self, element: Tag, tag_name: str, index: int, 
                             file_path: str, content: str, lines: List[str], 
                             use_id: bool = False) -> Optional[ParseResult]:
        """Create a ParseResult for an HTML element."""
        try:
            # Get element position in content
            element_str = str(element)
            start_pos = content.find(element_str)
            if start_pos == -1:
                return None
            
            line_start = content[:start_pos].count('\n') + 1
            line_end = content[:start_pos + len(element_str)].count('\n') + 1
            
            # Create element name
            if use_id and element.get('id'):
                name = f"{tag_name}#{element.get('id')}"
            else:
                name = f"{tag_name}_{index + 1}"
            
            # Extract attributes
            attrs = dict(element.attrs) if element.attrs else {}
            
            # Get element content (truncated)
            element_content = element_str
            if len(element_content) > 1000:
                element_content = element_content[:1000] + "..."
            
            result = ParseResult(
                name=name,
                entity_type=EntityType.HTML_ELEMENT,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                content=element_content,
                metadata={
                    'tag': tag_name,
                    'attributes': attrs,
                    'language': 'html'
                }
            )
            
            return result
            
        except Exception as e:
            logger.debug(f"Error creating element result: {e}")
            return None
    
    def _parse_with_regex(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Parse HTML using regex patterns (fallback)."""
        results = []
        
        # Extract major HTML tags
        major_tags = ['html', 'head', 'body', 'header', 'nav', 'main', 
                     'section', 'article', 'aside', 'footer', 'div', 'form']
        
        for tag in major_tags:
            pattern = re.compile(f'<{tag}(?:\\s+[^>]*)?>.*?</{tag}>', re.DOTALL | re.IGNORECASE)
            
            for i, match in enumerate(pattern.finditer(content)):
                line_start = content[:match.start()].count('\n') + 1
                line_end = content[:match.end()].count('\n') + 1
                
                # Extract ID if present
                id_match = self.patterns['id_attr'].search(match.group(0))
                element_id = id_match.group(1) if id_match else None
                
                # Extract classes if present
                class_match = self.patterns['class_attr'].search(match.group(0))
                classes = class_match.group(1).split() if class_match else []
                
                name = f"{tag}#{element_id}" if element_id else f"{tag}_{i + 1}"
                
                element_content = match.group(0)
                if len(element_content) > 1000:
                    element_content = element_content[:1000] + "..."
                
                result = ParseResult(
                    name=name,
                    entity_type=EntityType.HTML_ELEMENT,
                    file_path=file_path,
                    line_start=line_start,
                    line_end=line_end,
                    content=element_content,
                    metadata={
                        'tag': tag,
                        'id': element_id,
                        'classes': classes,
                        'language': 'html'
                    }
                )
                results.append(result)
        
        return results