"""
CSS language parser for extracting style entities.
"""

import os
import re
from typing import List, Set
import logging

from ..base import BaseFileParser, ParseResult, EntityType

logger = logging.getLogger(__name__)

try:
    import cssutils
    HAS_CSSUTILS = True
    # Suppress cssutils warnings
    cssutils.log.setLevel(logging.ERROR)
except ImportError:
    HAS_CSSUTILS = False
    logger.warning("cssutils not available, CSS parsing will be limited")


class CSSParser(BaseFileParser):
    """Parser for CSS files."""
    
    def __init__(self):
        super().__init__({'.css', '.scss', '.sass', '.less'}, "CSS")
        self.parser_version = "1.0.0"
        
        # Regex patterns for CSS parsing
        self.patterns = {
            'rule': re.compile(r'([^{}]+)\s*\{([^{}]*)\}', re.MULTILINE | re.DOTALL),
            'selector': re.compile(r'([^,{]+)(?=\s*[,{])', re.MULTILINE),
            'property': re.compile(r'([^:;]+):\s*([^;]+);?', re.MULTILINE),
            'media_query': re.compile(r'@media\s+([^{]+)\s*\{', re.MULTILINE | re.IGNORECASE),
            'import': re.compile(r'@import\s+(?:url\()?["\']?([^"\'()]+)["\']?\)?', re.MULTILINE | re.IGNORECASE),
            'keyframes': re.compile(r'@(?:-webkit-|-moz-|-o-)?keyframes\s+([^{]+)\s*\{', re.MULTILINE | re.IGNORECASE),
            'variable': re.compile(r'--([^:;]+):\s*([^;]+);?', re.MULTILINE),
        }
    
    def parse_file(self, file_path: str) -> List[ParseResult]:
        """Parse a CSS file and extract entities."""
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
                metadata={'language': 'css', 'size': len(content)}
            )
            results.append(file_result)
            
            if HAS_CSSUTILS:
                results.extend(self._parse_with_cssutils(content, file_path, lines))
            else:
                results.extend(self._parse_with_regex(content, file_path, lines))
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing CSS file {file_path}: {e}")
            return []
    
    def extract_dependencies(self, file_path: str) -> List[str]:
        """Extract CSS imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Extract @import statements
            import_matches = self.patterns['import'].findall(content)
            dependencies.extend(import_matches)
            
            return dependencies
            
        except Exception as e:
            logger.error(f"Error extracting dependencies from {file_path}: {e}")
            return []
    
    def get_supported_entity_types(self) -> List[EntityType]:
        """Get supported entity types for CSS."""
        return [
            EntityType.FILE,
            EntityType.CSS_RULE,
            EntityType.CSS_SELECTOR,
            EntityType.CSS_PROPERTY
        ]
    
    def _parse_with_cssutils(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Parse CSS using cssutils library."""
        results = []
        
        try:
            sheet = cssutils.parseString(content)
            
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    # CSS Style Rule
                    selector_text = rule.selectorText
                    line_num = self._find_line_number(content, selector_text, lines)
                    
                    # Create selector entity
                    selector_result = ParseResult(
                        name=selector_text,
                        entity_type=EntityType.CSS_SELECTOR,
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        content=selector_text,
                        metadata={
                            'type': 'selector',
                            'language': 'css'
                        }
                    )
                    results.append(selector_result)
                    
                    # Create rule entity
                    rule_content = f"{selector_text} {{ {rule.style.cssText} }}"
                    rule_result = ParseResult(
                        name=f"rule_{len(results)}",
                        entity_type=EntityType.CSS_RULE,
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num + rule_content.count('\n'),
                        content=rule_content,
                        metadata={
                            'selector': selector_text,
                            'properties_count': len(rule.style),
                            'language': 'css'
                        }
                    )
                    results.append(rule_result)
                    
                    # Create property entities
                    for prop in rule.style:
                        prop_result = ParseResult(
                            name=prop.name,
                            entity_type=EntityType.CSS_PROPERTY,
                            file_path=file_path,
                            line_start=line_num,
                            line_end=line_num,
                            content=f"{prop.name}: {prop.value}",
                            metadata={
                                'value': prop.value,
                                'priority': prop.priority,
                                'selector': selector_text,
                                'language': 'css'
                            }
                        )
                        results.append(prop_result)
                
                elif rule.type == rule.MEDIA_RULE:
                    # Media Query
                    media_text = rule.media.mediaText
                    line_num = self._find_line_number(content, f"@media {media_text}", lines)
                    
                    media_result = ParseResult(
                        name=f"media_{media_text}",
                        entity_type=EntityType.CSS_RULE,
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        content=f"@media {media_text}",
                        metadata={
                            'type': 'media_query',
                            'media': media_text,
                            'language': 'css'
                        }
                    )
                    results.append(media_result)
        
        except Exception as e:
            logger.error(f"Error parsing CSS with cssutils: {e}")
            # Fallback to regex parsing
            results.extend(self._parse_with_regex(content, file_path, lines))
        
        return results
    
    def _parse_with_regex(self, content: str, file_path: str, lines: List[str]) -> List[ParseResult]:
        """Parse CSS using regex patterns (fallback)."""
        results = []
        
        # Extract CSS rules
        for i, match in enumerate(self.patterns['rule'].finditer(content)):
            selector_part = match.group(1).strip()
            properties_part = match.group(2).strip()
            
            line_start = content[:match.start()].count('\n') + 1
            line_end = content[:match.end()].count('\n') + 1
            
            # Extract selectors
            selectors = [s.strip() for s in selector_part.split(',')]
            
            for selector in selectors:
                if selector:
                    selector_result = ParseResult(
                        name=selector,
                        entity_type=EntityType.CSS_SELECTOR,
                        file_path=file_path,
                        line_start=line_start,
                        line_end=line_start,
                        content=selector,
                        metadata={
                            'type': 'selector',
                            'language': 'css'
                        }
                    )
                    results.append(selector_result)
            
            # Create rule entity
            rule_content = match.group(0)
            if len(rule_content) > 1000:
                rule_content = rule_content[:1000] + "..."
            
            rule_result = ParseResult(
                name=f"rule_{i + 1}",
                entity_type=EntityType.CSS_RULE,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                content=rule_content,
                metadata={
                    'selector': selector_part,
                    'language': 'css'
                }
            )
            results.append(rule_result)
            
            # Extract properties
            for prop_match in self.patterns['property'].finditer(properties_part):
                prop_name = prop_match.group(1).strip()
                prop_value = prop_match.group(2).strip()
                
                prop_result = ParseResult(
                    name=prop_name,
                    entity_type=EntityType.CSS_PROPERTY,
                    file_path=file_path,
                    line_start=line_start,
                    line_end=line_start,
                    content=f"{prop_name}: {prop_value}",
                    metadata={
                        'value': prop_value,
                        'selector': selector_part,
                        'language': 'css'
                    }
                )
                results.append(prop_result)
        
        # Extract media queries
        for match in self.patterns['media_query'].finditer(content):
            media_condition = match.group(1).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            media_result = ParseResult(
                name=f"media_{media_condition}",
                entity_type=EntityType.CSS_RULE,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=match.group(0),
                metadata={
                    'type': 'media_query',
                    'condition': media_condition,
                    'language': 'css'
                }
            )
            results.append(media_result)
        
        # Extract keyframes
        for match in self.patterns['keyframes'].finditer(content):
            keyframe_name = match.group(1).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            keyframe_result = ParseResult(
                name=keyframe_name,
                entity_type=EntityType.CSS_RULE,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=match.group(0),
                metadata={
                    'type': 'keyframes',
                    'name': keyframe_name,
                    'language': 'css'
                }
            )
            results.append(keyframe_result)
        
        # Extract CSS variables
        for match in self.patterns['variable'].finditer(content):
            var_name = match.group(1).strip()
            var_value = match.group(2).strip()
            line_num = content[:match.start()].count('\n') + 1
            
            var_result = ParseResult(
                name=f"--{var_name}",
                entity_type=EntityType.CSS_PROPERTY,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                content=f"--{var_name}: {var_value}",
                metadata={
                    'type': 'variable',
                    'value': var_value,
                    'language': 'css'
                }
            )
            results.append(var_result)
        
        return results
    
    def _find_line_number(self, content: str, search_text: str, lines: List[str]) -> int:
        """Find the line number of a text in content."""
        try:
            pos = content.find(search_text)
            if pos != -1:
                return content[:pos].count('\n') + 1
        except:
            pass
        return 1