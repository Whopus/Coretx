"""
Knowledge graph implementation for code entities and relationships.

This module provides the core graph data structure and algorithms for
storing, querying, and manipulating code knowledge graphs.
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import networkx as nx
import numpy as np

from .models import (
    CodeEntity, 
    Relationship, 
    EntityType, 
    RelationshipType,
    GraphStats,
    GraphError
)


class CodeGraph:
    """Knowledge graph for code entities and relationships."""
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = project_path
        self._graph = nx.MultiDiGraph()
        self._entities: Dict[str, CodeEntity] = {}
        self._relationships: Dict[str, Relationship] = {}
        self._entity_index: Dict[str, Set[str]] = {}  # For fast lookups
        self._embedding_index: Optional[Any] = None  # For vector search
        
    @property
    def nodes(self) -> List[CodeEntity]:
        """Get all code entities in the graph."""
        return list(self._entities.values())
    
    @property
    def edges(self) -> List[Relationship]:
        """Get all relationships in the graph."""
        return list(self._relationships.values())
    
    def add_entity(self, entity: CodeEntity) -> None:
        """Add a code entity to the graph."""
        if entity.id in self._entities:
            # Update existing entity
            self._entities[entity.id] = entity
        else:
            # Add new entity
            self._entities[entity.id] = entity
            self._graph.add_node(entity.id, entity=entity)
            
        # Update indices
        self._update_entity_index(entity)
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the graph."""
        # Ensure both entities exist
        if relationship.source_id not in self._entities:
            raise GraphError(f"Source entity {relationship.source_id} not found")
        if relationship.target_id not in self._entities:
            raise GraphError(f"Target entity {relationship.target_id} not found")
        
        self._relationships[relationship.id] = relationship
        self._graph.add_edge(
            relationship.source_id,
            relationship.target_id,
            key=relationship.id,
            relationship=relationship
        )
    
    def find_entity(self, name: str) -> Optional[CodeEntity]:
        """Find entity by name."""
        # Direct lookup first
        for entity in self._entities.values():
            if entity.name == name:
                return entity
        
        # Fuzzy search in index
        if name in self._entity_index:
            entity_ids = self._entity_index[name]
            if entity_ids:
                return self._entities[next(iter(entity_ids))]
        
        return None
    
    def find_entities(
        self, 
        entity_type: Optional[EntityType] = None,
        name_pattern: Optional[str] = None,
        path_pattern: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[CodeEntity]:
        """Find entities matching criteria."""
        results = []
        
        for entity in self._entities.values():
            # Type filter
            if entity_type and entity.type != entity_type:
                continue
                
            # Name pattern filter
            if name_pattern and not self._match_pattern(entity.name, name_pattern):
                continue
                
            # Path pattern filter
            if path_pattern and not self._match_pattern(entity.path, path_pattern):
                continue
                
            # Language filter
            if language and entity.language != language:
                continue
                
            results.append(entity)
        
        return results
    
    def get_dependencies(self, entity: CodeEntity) -> List[CodeEntity]:
        """Get all dependencies of an entity."""
        dependencies = []
        
        if entity.id in self._graph:
            for successor in self._graph.successors(entity.id):
                dependencies.append(self._entities[successor])
        
        return dependencies
    
    def get_dependents(self, entity: CodeEntity) -> List[CodeEntity]:
        """Get all entities that depend on this one."""
        dependents = []
        
        if entity.id in self._graph:
            for predecessor in self._graph.predecessors(entity.id):
                dependents.append(self._entities[predecessor])
        
        return dependents
    
    def get_relationships(
        self, 
        source: Optional[CodeEntity] = None,
        target: Optional[CodeEntity] = None,
        relationship_type: Optional[RelationshipType] = None
    ) -> List[Relationship]:
        """Get relationships matching criteria."""
        results = []
        
        for relationship in self._relationships.values():
            # Source filter
            if source and relationship.source_id != source.id:
                continue
                
            # Target filter
            if target and relationship.target_id != target.id:
                continue
                
            # Type filter
            if relationship_type and relationship.type != relationship_type:
                continue
                
            results.append(relationship)
        
        return results
    
    def subgraph(self, entities: List[CodeEntity]) -> 'CodeGraph':
        """Extract a subgraph containing specified entities."""
        subgraph = CodeGraph()
        entity_ids = {entity.id for entity in entities}
        
        # Add entities
        for entity in entities:
            subgraph.add_entity(entity)
        
        # Add relationships between included entities
        for relationship in self._relationships.values():
            if (relationship.source_id in entity_ids and 
                relationship.target_id in entity_ids):
                subgraph.add_relationship(relationship)
        
        return subgraph
    
    def find_paths(
        self, 
        source: CodeEntity, 
        target: CodeEntity, 
        max_depth: int = 5
    ) -> List[List[CodeEntity]]:
        """Find paths between two entities."""
        if source.id not in self._graph or target.id not in self._graph:
            return []
        
        try:
            # Find all simple paths
            paths = list(nx.all_simple_paths(
                self._graph, 
                source.id, 
                target.id, 
                cutoff=max_depth
            ))
            
            # Convert to entity paths
            entity_paths = []
            for path in paths:
                entity_path = [self._entities[entity_id] for entity_id in path]
                entity_paths.append(entity_path)
            
            return entity_paths
        except nx.NetworkXNoPath:
            return []
    
    def find_shortest_path(self, source: CodeEntity, target: CodeEntity) -> Optional[List[CodeEntity]]:
        """Find shortest path between two entities."""
        if source.id not in self._graph or target.id not in self._graph:
            return None
        
        try:
            path = nx.shortest_path(self._graph, source.id, target.id)
            return [self._entities[entity_id] for entity_id in path]
        except nx.NetworkXNoPath:
            return None
    
    def get_connected_components(self) -> List[List[CodeEntity]]:
        """Get connected components in the graph."""
        components = []
        
        # Convert to undirected for component analysis
        undirected = self._graph.to_undirected()
        
        for component in nx.connected_components(undirected):
            entities = [self._entities[entity_id] for entity_id in component]
            components.append(entities)
        
        return components
    
    def find_circular_dependencies(self) -> List[List[CodeEntity]]:
        """Find circular dependencies in the graph."""
        cycles = []
        
        try:
            # Find strongly connected components with more than one node
            sccs = list(nx.strongly_connected_components(self._graph))
            
            for scc in sccs:
                if len(scc) > 1:
                    entities = [self._entities[entity_id] for entity_id in scc]
                    cycles.append(entities)
        except Exception:
            pass
        
        return cycles
    
    def get_entity_metrics(self, entity: CodeEntity) -> Dict[str, Any]:
        """Get metrics for a specific entity."""
        if entity.id not in self._graph:
            return {}
        
        node_id = entity.id
        
        return {
            "in_degree": self._graph.in_degree(node_id),
            "out_degree": self._graph.out_degree(node_id),
            "total_degree": self._graph.degree(node_id),
            "clustering": nx.clustering(self._graph.to_undirected(), node_id),
            "betweenness_centrality": nx.betweenness_centrality(self._graph).get(node_id, 0),
            "pagerank": nx.pagerank(self._graph).get(node_id, 0),
        }
    
    def get_graph_stats(self) -> GraphStats:
        """Get statistics about the graph."""
        entity_counts = {}
        for entity_type in EntityType:
            entity_counts[entity_type] = len([
                e for e in self._entities.values() if e.type == entity_type
            ])
        
        relationship_counts = {}
        for rel_type in RelationshipType:
            relationship_counts[rel_type] = len([
                r for r in self._relationships.values() if r.type == rel_type
            ])
        
        language_breakdown = {}
        for entity in self._entities.values():
            if entity.language:
                language_breakdown[entity.language] = language_breakdown.get(entity.language, 0) + 1
        
        file_count = len(set(entity.path for entity in self._entities.values()))
        total_lines = sum(entity.size for entity in self._entities.values())
        
        return GraphStats(
            total_entities=len(self._entities),
            total_relationships=len(self._relationships),
            entity_counts=entity_counts,
            relationship_counts=relationship_counts,
            language_breakdown=language_breakdown,
            file_count=file_count,
            total_lines=total_lines,
            analysis_time=0.0  # Would be set by analyzer
        )
    
    def save(self, path: str, format: str = "json") -> None:
        """Save the graph to disk."""
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            self._save_json(save_path)
        elif format == "pickle":
            self._save_pickle(save_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def load(self, path: str, format: str = "json") -> None:
        """Load the graph from disk."""
        load_path = Path(path)
        
        if not load_path.exists():
            raise FileNotFoundError(f"Graph file not found: {path}")
        
        if format == "json":
            self._load_json(load_path)
        elif format == "pickle":
            self._load_pickle(load_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    @classmethod
    def load_from_path(cls, path: str, format: str = "json") -> 'CodeGraph':
        """Load a graph from disk."""
        graph = cls()
        graph.load(path, format)
        return graph
    
    def export(self, path: str, format: str = "graphml") -> None:
        """Export graph for external tools."""
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "graphml":
            nx.write_graphml(self._graph, export_path)
        elif format == "gexf":
            nx.write_gexf(self._graph, export_path)
        elif format == "cytoscape":
            self._export_cytoscape(export_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _update_entity_index(self, entity: CodeEntity) -> None:
        """Update search indices for an entity."""
        # Index by name
        if entity.name not in self._entity_index:
            self._entity_index[entity.name] = set()
        self._entity_index[entity.name].add(entity.id)
        
        # Index by qualified name
        if hasattr(entity, 'qualified_name') and entity.qualified_name != entity.name:
            if entity.qualified_name not in self._entity_index:
                self._entity_index[entity.qualified_name] = set()
            self._entity_index[entity.qualified_name].add(entity.id)
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """Simple pattern matching with wildcards."""
        if '*' not in pattern:
            return pattern in text
        
        # Convert glob pattern to regex
        import re
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.search(regex_pattern, text))
    
    def _save_json(self, path: Path) -> None:
        """Save graph as JSON."""
        data = {
            "project_path": self.project_path,
            "entities": [self._entity_to_dict(e) for e in self._entities.values()],
            "relationships": [self._relationship_to_dict(r) for r in self._relationships.values()]
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=self._json_serializer)
    
    def _load_json(self, path: Path) -> None:
        """Load graph from JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.project_path = data.get("project_path")
        
        # Load entities
        for entity_data in data.get("entities", []):
            entity = self._dict_to_entity(entity_data)
            self.add_entity(entity)
        
        # Load relationships
        for rel_data in data.get("relationships", []):
            relationship = self._dict_to_relationship(rel_data)
            try:
                self.add_relationship(relationship)
            except GraphError:
                # Skip relationships with missing entities
                pass
    
    def _save_pickle(self, path: Path) -> None:
        """Save graph as pickle."""
        data = {
            "project_path": self.project_path,
            "entities": self._entities,
            "relationships": self._relationships,
            "graph": self._graph
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def _load_pickle(self, path: Path) -> None:
        """Load graph from pickle."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.project_path = data.get("project_path")
        self._entities = data.get("entities", {})
        self._relationships = data.get("relationships", {})
        self._graph = data.get("graph", nx.MultiDiGraph())
        
        # Rebuild indices
        for entity in self._entities.values():
            self._update_entity_index(entity)
    
    def _entity_to_dict(self, entity: CodeEntity) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization."""
        return {
            "id": entity.id,
            "type": entity.type.value,
            "name": entity.name,
            "path": entity.path,
            "line_start": entity.line_start,
            "line_end": entity.line_end,
            "description": entity.description,
            "content": entity.content,
            "language": entity.language,
            "metadata": entity.metadata,
            "embedding": entity.embedding.tolist() if entity.embedding is not None else None
        }
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> CodeEntity:
        """Convert dictionary to entity."""
        embedding = None
        if data.get("embedding"):
            embedding = np.array(data["embedding"])
        
        return CodeEntity(
            id=data["id"],
            type=EntityType(data["type"]),
            name=data["name"],
            path=data["path"],
            line_start=data["line_start"],
            line_end=data["line_end"],
            description=data.get("description", ""),
            content=data.get("content", ""),
            language=data.get("language", ""),
            metadata=data.get("metadata", {}),
            embedding=embedding
        )
    
    def _relationship_to_dict(self, relationship: Relationship) -> Dict[str, Any]:
        """Convert relationship to dictionary for serialization."""
        return {
            "id": relationship.id,
            "type": relationship.type.value,
            "source_id": relationship.source_id,
            "target_id": relationship.target_id,
            "description": relationship.description,
            "metadata": relationship.metadata,
            "confidence": relationship.confidence,
            "embedding": relationship.embedding.tolist() if relationship.embedding is not None else None
        }
    
    def _dict_to_relationship(self, data: Dict[str, Any]) -> Relationship:
        """Convert dictionary to relationship."""
        embedding = None
        if data.get("embedding"):
            embedding = np.array(data["embedding"])
        
        return Relationship(
            id=data["id"],
            type=RelationshipType(data["type"]),
            source_id=data["source_id"],
            target_id=data["target_id"],
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
            confidence=data.get("confidence", 1.0),
            embedding=embedding
        )
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for numpy arrays and other objects."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _export_cytoscape(self, path: Path) -> None:
        """Export graph in Cytoscape.js format."""
        nodes = []
        edges = []
        
        for entity in self._entities.values():
            nodes.append({
                "data": {
                    "id": entity.id,
                    "label": entity.name,
                    "type": entity.type.value,
                    "path": entity.path,
                    "language": entity.language
                }
            })
        
        for relationship in self._relationships.values():
            edges.append({
                "data": {
                    "id": relationship.id,
                    "source": relationship.source_id,
                    "target": relationship.target_id,
                    "type": relationship.type.value,
                    "label": relationship.type.value
                }
            })
        
        cytoscape_data = {
            "elements": {
                "nodes": nodes,
                "edges": edges
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cytoscape_data, f, indent=2)