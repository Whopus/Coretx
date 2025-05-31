"""
Code analyzer for building knowledge graphs from source code.
"""

import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from .models import AnalysisConfig, CodeEntity, Relationship, AnalysisError
from .graph import CodeGraph
from .parsers.registry import ParserRegistry
from .llm.semantic_analyzer import SemanticAnalyzer
from .utils.file_utils import FileScanner
from .utils.progress import ProgressReporter


class CodeAnalyzer:
    """Analyzes codebases to build knowledge graphs."""
    
    def __init__(
        self, 
        parser_registry: ParserRegistry,
        semantic_analyzer: SemanticAnalyzer,
        config: AnalysisConfig
    ):
        self.parser_registry = parser_registry
        self.semantic_analyzer = semantic_analyzer
        self.config = config
        self.logger = logging.getLogger("coretx.analyzer")
    
    def analyze_project(self, project_path: Path, existing_graph: Optional[CodeGraph] = None) -> CodeGraph:
        """Analyze an entire project and build a knowledge graph."""
        if existing_graph:
            graph = existing_graph
        else:
            graph = CodeGraph(str(project_path))
        
        # Scan for files
        scanner = FileScanner(self.config)
        files = scanner.scan_directory(project_path)
        
        if not files:
            self.logger.warning(f"No supported files found in {project_path}")
            return graph
        
        self.logger.info(f"Found {len(files)} files to analyze")
        
        # Parse files and extract entities/relationships
        with ProgressReporter(len(files), "Parsing files") as progress:
            entities, relationships = self._parse_files(files, progress)
        
        # Add entities to graph
        self.logger.info(f"Adding {len(entities)} entities to graph")
        for entity in entities:
            graph.add_entity(entity)
        
        # Add relationships to graph
        self.logger.info(f"Adding {len(relationships)} relationships to graph")
        for relationship in relationships:
            try:
                graph.add_relationship(relationship)
            except Exception as e:
                self.logger.debug(f"Skipped relationship {relationship.id}: {e}")
        
        # Perform semantic analysis
        if entities and self.semantic_analyzer:
            self.logger.info("Performing semantic analysis")
            graph = self.semantic_analyzer.analyze_graph(graph)
        
        return graph
    
    def analyze_file(self, file_path: Path) -> Tuple[List[CodeEntity], List[Relationship]]:
        """Analyze a single file."""
        try:
            if not self.parser_registry.can_parse(str(file_path)):
                return [], []
            
            # Check file size
            if file_path.stat().st_size > self.config.max_file_size:
                self.logger.warning(f"Skipping large file: {file_path}")
                return [], []
            
            # Parse the file
            entities, relationships = self.parser_registry.parse_file(str(file_path))
            
            self.logger.debug(f"Parsed {file_path}: {len(entities)} entities, {len(relationships)} relationships")
            return entities, relationships
            
        except Exception as e:
            self.logger.error(f"Failed to analyze {file_path}: {e}")
            return [], []
    
    def update_graph(self, graph: CodeGraph, changed_files: List[str]) -> CodeGraph:
        """Update graph with changes to specific files."""
        changed_paths = [Path(f) for f in changed_files]
        
        # Remove entities from changed files
        entities_to_remove = []
        for entity in graph.nodes:
            if any(str(path) in entity.path for path in changed_paths):
                entities_to_remove.append(entity)
        
        # Remove old entities and their relationships
        for entity in entities_to_remove:
            self._remove_entity_from_graph(graph, entity)
        
        # Re-analyze changed files
        new_entities = []
        new_relationships = []
        
        for file_path in changed_paths:
            if file_path.exists():
                entities, relationships = self.analyze_file(file_path)
                new_entities.extend(entities)
                new_relationships.extend(relationships)
        
        # Add new entities and relationships
        for entity in new_entities:
            graph.add_entity(entity)
        
        for relationship in new_relationships:
            try:
                graph.add_relationship(relationship)
            except Exception:
                pass  # Skip invalid relationships
        
        # Perform semantic analysis on new entities
        if new_entities:
            analyzed_entities = self.semantic_analyzer.analyze_entities_batch(new_entities)
            for entity in analyzed_entities:
                graph.add_entity(entity)
        
        return graph
    
    def _parse_files(self, files: List[Path], progress: ProgressReporter) -> Tuple[List[CodeEntity], List[Relationship]]:
        """Parse multiple files in parallel."""
        all_entities = []
        all_relationships = []
        
        # Determine number of workers
        max_workers = min(4, len(files))
        
        if max_workers == 1 or len(files) < 10:
            # Sequential processing for small numbers of files
            for file_path in files:
                entities, relationships = self.analyze_file(file_path)
                all_entities.extend(entities)
                all_relationships.extend(relationships)
                progress.update(1)
        else:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self.analyze_file, file_path): file_path 
                    for file_path in files
                }
                
                # Collect results
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        entities, relationships = future.result()
                        all_entities.extend(entities)
                        all_relationships.extend(relationships)
                    except Exception as e:
                        self.logger.error(f"Failed to process {file_path}: {e}")
                    finally:
                        progress.update(1)
        
        return all_entities, all_relationships
    
    def _remove_entity_from_graph(self, graph: CodeGraph, entity: CodeEntity) -> None:
        """Remove an entity and its relationships from the graph."""
        # Remove relationships involving this entity
        relationships_to_remove = []
        for relationship in graph.edges:
            if relationship.source_id == entity.id or relationship.target_id == entity.id:
                relationships_to_remove.append(relationship)
        
        # Remove from internal structures
        if entity.id in graph._entities:
            del graph._entities[entity.id]
        
        if entity.id in graph._graph:
            graph._graph.remove_node(entity.id)
        
        for relationship in relationships_to_remove:
            if relationship.id in graph._relationships:
                del graph._relationships[relationship.id]