"""Graph searcher for querying code dependency graphs."""

from typing import List, Dict, Set, Optional, Tuple, Any
import networkx as nx
from pathlib import Path

from .types import NodeType, EdgeType, CodeNode
from ...config import GraphConfig

import logging
logger = logging.getLogger(__name__)


class GraphSearcher:
    """Provides search capabilities over code dependency graphs."""
    
    def __init__(self, graph: nx.MultiDiGraph, config: GraphConfig):
        self.graph = graph
        self.config = config
        self._build_indices()
    
    def _build_indices(self) -> None:
        """Build search indices for efficient querying."""
        self.name_index: Dict[str, List[str]] = {}
        self.type_index: Dict[str, List[str]] = {}
        self.path_index: Dict[str, str] = {}
        
        for node_id, attrs in self.graph.nodes(data=True):
            name = attrs.get('name', '')
            node_type = attrs.get('type', '')
            path = attrs.get('path', '')
            
            # Name index
            if name not in self.name_index:
                self.name_index[name] = []
            self.name_index[name].append(node_id)
            
            # Type index
            if node_type not in self.type_index:
                self.type_index[node_type] = []
            self.type_index[node_type].append(node_id)
            
            # Path index
            if path:
                self.path_index[path] = node_id
    
    def search_by_name(self, name: str, node_type: Optional[NodeType] = None) -> List[str]:
        """Search nodes by name, optionally filtered by type."""
        candidates = self.name_index.get(name, [])
        
        if node_type:
            type_str = node_type.value
            candidates = [
                node_id for node_id in candidates
                if self.graph.nodes[node_id].get('type') == type_str
            ]
        
        return candidates
    
    def search_by_type(self, node_type: NodeType) -> List[str]:
        """Search all nodes of a specific type."""
        return self.type_index.get(node_type.value, [])
    
    def search_by_path(self, path: str) -> Optional[str]:
        """Search node by file path."""
        return self.path_index.get(path)
    
    def fuzzy_search_by_name(self, query: str, threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Fuzzy search nodes by name."""
        from difflib import SequenceMatcher
        
        results = []
        for name, node_ids in self.name_index.items():
            similarity = SequenceMatcher(None, query.lower(), name.lower()).ratio()
            if similarity >= threshold:
                for node_id in node_ids:
                    results.append((node_id, similarity))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None,
                     direction: str = 'both') -> List[str]:
        """Get neighboring nodes."""
        neighbors = []
        
        if direction in ['out', 'both']:
            for _, target, attrs in self.graph.out_edges(node_id, data=True):
                if not edge_type or attrs.get('type') == edge_type.value:
                    neighbors.append(target)
        
        if direction in ['in', 'both']:
            for source, _, attrs in self.graph.in_edges(node_id, data=True):
                if not edge_type or attrs.get('type') == edge_type.value:
                    neighbors.append(source)
        
        return list(set(neighbors))
    
    def get_contained_entities(self, node_id: str) -> List[str]:
        """Get all entities contained within a node."""
        return self.get_neighbors(node_id, EdgeType.CONTAINS, direction='out')
    
    def get_container(self, node_id: str) -> Optional[str]:
        """Get the container of a node."""
        containers = self.get_neighbors(node_id, EdgeType.CONTAINS, direction='in')
        return containers[0] if containers else None
    
    def get_dependencies(self, node_id: str) -> Dict[str, List[str]]:
        """Get all dependencies of a node."""
        dependencies = {}
        
        for edge_type in EdgeType:
            if edge_type != EdgeType.CONTAINS:
                deps = self.get_neighbors(node_id, edge_type, direction='out')
                if deps:
                    dependencies[edge_type.value] = deps
        
        return dependencies
    
    def get_dependents(self, node_id: str) -> Dict[str, List[str]]:
        """Get all nodes that depend on this node."""
        dependents = {}
        
        for edge_type in EdgeType:
            if edge_type != EdgeType.CONTAINS:
                deps = self.get_neighbors(node_id, edge_type, direction='in')
                if deps:
                    dependents[edge_type.value] = deps
        
        return dependents
    
    def find_path(self, source_id: str, target_id: str, 
                 max_length: int = 5) -> Optional[List[str]]:
        """Find shortest path between two nodes."""
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            if len(path) <= max_length + 1:  # +1 because path includes both endpoints
                return path
        except nx.NetworkXNoPath:
            pass
        return None
    
    def get_subgraph(self, node_ids: List[str], include_neighbors: bool = False) -> nx.MultiDiGraph:
        """Extract subgraph containing specified nodes."""
        if include_neighbors:
            extended_nodes = set(node_ids)
            for node_id in node_ids:
                extended_nodes.update(self.get_neighbors(node_id))
            node_ids = list(extended_nodes)
        
        return self.graph.subgraph(node_ids).copy()
    
    def get_node_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a node."""
        if node_id not in self.graph:
            return None
        
        attrs = self.graph.nodes[node_id]
        
        # Get relationships
        dependencies = self.get_dependencies(node_id)
        dependents = self.get_dependents(node_id)
        contained = self.get_contained_entities(node_id)
        container = self.get_container(node_id)
        
        return {
            'id': node_id,
            'attributes': attrs,
            'dependencies': dependencies,
            'dependents': dependents,
            'contained_entities': contained,
            'container': container
        }
    
    def search_related_entities(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for entities related to a query."""
        results = []
        
        # Direct name matches
        direct_matches = []
        for name, node_ids in self.name_index.items():
            if query.lower() in name.lower():
                for node_id in node_ids:
                    direct_matches.append((node_id, 1.0))
        
        # Fuzzy matches
        fuzzy_matches = self.fuzzy_search_by_name(query, threshold=0.6)
        
        # Combine and deduplicate
        all_matches = {}
        for node_id, score in direct_matches + fuzzy_matches:
            if node_id not in all_matches or all_matches[node_id] < score:
                all_matches[node_id] = score
        
        # Sort by score and limit results
        sorted_matches = sorted(all_matches.items(), key=lambda x: x[1], reverse=True)
        
        for node_id, score in sorted_matches[:max_results]:
            node_info = self.get_node_info(node_id)
            if node_info:
                node_info['relevance_score'] = score
                results.append(node_info)
        
        return results
    
    def get_file_entities(self, file_path: str) -> List[str]:
        """Get all entities (classes, functions) in a file."""
        file_node_id = self.search_by_path(file_path)
        if not file_node_id:
            return []
        
        entities = []
        contained = self.get_contained_entities(file_node_id)
        
        for entity_id in contained:
            entity_type = self.graph.nodes[entity_id].get('type')
            if entity_type in ['class', 'function']:
                entities.append(entity_id)
                
                # If it's a class, also get its methods
                if entity_type == 'class':
                    methods = self.get_contained_entities(entity_id)
                    entities.extend(methods)
        
        return entities