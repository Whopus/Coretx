"""
Markdown language parser for extracting documentation entities.
"""

import os
import re
from typing import List, Set
import logging

from ..base import BaseFileParser, ParseResult, EntityType

logger = logging.getLogger(__name__)


class MarkdownParser(BaseFileParser):
    """Parser for Markdown files."""
    
    def __init__(self):
        super().__init__({'.md', '.markdown', '.mdown', '.mkd'}, "Markdown")
        self.parser_version = "1.0.0"
        
        # Regex patterns for Markdown parsing
        self.patterns = {
            'heading': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'code_block': re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL),
            'inline_code': re.compile(r'`([^`]+)`'),
            'link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            'image': re.compile(r'!\[([^\]]*)\]\(([^)]+)\)'),
            'list_item': re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE),
            'numbered_list': re.compile(r'^[\s]*\d+\.\s+(.+)$', re.MULTILINE),
            'table': re.compile(r'^\|(.+)\|$', re.MULTILINE),
            'blockquote': re.compile(r'^>\s+(.+)$', re.MULTILINE),
        }
    
    def parse_file(self, file_path: str) -> List[ParseResult]:
        """Parse a Markdown file and extract entities."""
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
                metadata={'language': 'markdown', 'size': len(content)}
            )
            results.append(file_result)
            
            # Extract different types of entities
            results.extend(self._extract_headings(content, file_path, lines))
            results.extend(self._extract_code_blocks(content, file_path, lines))
            results.extend(self._extract_links(content, file_path, lines))
            results.extend(self._extract_text_sections(content, file_path, lines))
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing Markdown file {file_path}: {e}")
            return []
    
    def extract_dependencies(self, file_path: str) -> List[str]:
        """Extract links and references from Markdown."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Extract links
            link_matches = self.patterns['link'].findall(content)
            for _, url in link_matches:
                if not url.startswith(('http://', 'https://', 'mailto:')):
                    dependencies.append(url)
            
            # Extract image references
            image_matches = self.patterns['image'].findall(content)
            for _, url in image_matches:
                if not url.startswith(('http://', 'https://')):
                    dependencies.append(url)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Error extracting dependencies from {file_path}: {e}")
            return []
    
    def get_supported_entity_types(self) -> List[EntityType]:
        """Get supported entity types for Markdown."""
        return [
            EntityType.FILE,
            EntityType.HEADING,
            EntityType.CODE_BLOCK,
            EntityType.LINK,
            EntityType.TEXT_SECTION
        ]
    
    def _extract_headings(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract heading entities."""
        results = []
        
        for match in self.patterns['heading'].finditer(content):
            hashes = match.group(1)
            heading_text = match.group(2).strip()
            level = len(hashes)
            line_num = content[:match.start()].count('\n') + 1
            
            result = ParseResult(
                name=heading_text,
                entity_type=EntityType.HEADING,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=match.group(0),
                metadata={
                    'level': level,
                    'language': 'markdown'
                }
            )
            results.append(result)
        
        return results
    
    def _extract_code_blocks(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract code block entities."""
        results = []
        
        for match in self.patterns['code_block'].finditer(content):
            language = match.group(1) or 'text'
            code_content = match.group(2)
            line_start = content[:match.start()].count('\n') + 1
            line_end = content[:match.end()].count('\n') + 1
            
            # Create a name based on the language and position
            name = f"code_block_{language}_{line_start}"
            
            result = ParseResult(
                name=name,
                entity_type=EntityType.CODE_BLOCK,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                content=code_content,
                metadata={
                    'language': language,
                    'block_type': 'fenced'
                }
            )
            results.append(result)
        
        return results
    
    def _extract_links(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract link entities."""
        results = []
        
        for match in self.patterns['link'].finditer(content):
            link_text = match.group(1)
            link_url = match.group(2)
            line_num = content[:match.start()].count('\n') + 1
            
            result = ParseResult(
                name=link_text,
                entity_type=EntityType.LINK,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=match.group(0),
                metadata={
                    'url': link_url,
                    'type': 'link',
                    'language': 'markdown'
                }
            )
            results.append(result)
        
        return results
    
    def _extract_text_sections(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Extract text sections between headings."""
        results = []
        
        # Find all headings to determine sections
        headings = list(self.patterns['heading'].finditer(content))
        
        if not headings:
            # No headings, treat entire content as one section
            if content.strip():
                result = ParseResult(
                    name="main_content",
                    entity_type=EntityType.TEXT_SECTION,
                    file_path=file_path,
                    line_start=1,
                    line_end=len(lines),
                    content=content[:1000] + "..." if len(content) > 1000 else content,
                    metadata={'language': 'markdown'}
                )
                results.append(result)
            return results
        
        # Extract sections between headings
        for i, heading in enumerate(headings):
            heading_line = content[:heading.start()].count('\n') + 1
            
            # Determine section end
            if i + 1 < len(headings):
                next_heading = headings[i + 1]
                section_end_line = content[:next_heading.start()].count('\n')
            else:
                section_end_line = len(lines)
            
            # Extract section content
            if section_end_line > heading_line:
                section_lines = lines[heading_line:section_end_line]
                section_content = '\n'.join(section_lines).strip()
                
                if section_content:
                    section_name = f"section_{heading.group(2).strip()[:30]}"
                    
                    result = ParseResult(
                        name=section_name,
                        entity_type=EntityType.TEXT_SECTION,
                        file_path=file_path,
                        line_start=heading_line + 1,
                        line_end=section_end_line,
                        content=section_content[:1000] + "..." if len(section_content) > 1000 else section_content,
                        metadata={
                            'heading': heading.group(2).strip(),
                            'language': 'markdown'
                        }
                    )
                    results.append(result)
        
        return results