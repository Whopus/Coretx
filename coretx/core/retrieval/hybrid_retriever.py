"""Hybrid retriever combining BM25 and graph-based search."""

from typing import List, Dict, Tuple, Optional, Set
import networkx as nx
from pathlib import Path

from .bm25_retriever import BM25Retriever
from ..graph.searcher import GraphSearcher
from ..graph.types import NodeType
from ...config import RetrievalConfig

import logging
logger = logging.getLogger(__name__)


class HybridRetriever:
    """Combines BM25 text search with graph-based structural search."""
    
    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.bm25_retriever = BM25Retriever(config)
        self.graph_searcher: Optional[GraphSearcher] = None
        self.graph: Optional[nx.MultiDiGraph] = None
    
    def build_index(self, graph: nx.MultiDiGraph, repo_path: Optional[Path] = None) -> None:
        """Build hybrid index from graph."""
        logger.info("Building hybrid retrieval index...")
        
        self.graph = graph
        self.graph_searcher = GraphSearcher(graph, self.config)
        self.bm25_retriever.build_index(graph, repo_path)
        
        logger.info("Hybrid retrieval index built successfully")
    
    def search(self, query: str, search_type: str = "hybrid", 
              top_k: Optional[int] = None) -> List[Dict]:
        """
        Search using hybrid approach.
        
        Args:
            query: Search query
            search_type: "hybrid", "text", "graph", or "structure"
            top_k: Number of results to return
        """
        if top_k is None:
            top_k = self.config.top_k
        
        if search_type == "text":
            return self._text_search(query, top_k)
        elif search_type == "graph":
            return self._graph_search(query, top_k)
        elif search_type == "structure":
            return self._structure_search(query, top_k)
        else:  # hybrid
            return self._hybrid_search(query, top_k)
    
    def _text_search(self, query: str, top_k: int) -> List[Dict]:
        """Pure BM25 text search."""
        results = self.bm25_retriever.search(query, top_k)
        
        formatted_results = []
        for node_id, score in results:
            node_info = self.graph_searcher.get_node_info(node_id)
            if node_info:
                formatted_results.append({
                    'node_id': node_id,
                    'score': score,
                    'search_type': 'text',
                    'node_info': node_info
                })
        
        return formatted_results
    
    def _graph_search(self, query: str, top_k: int) -> List[Dict]:
        """Graph-based search using entity names and relationships."""
        results = self.graph_searcher.search_related_entities(query, top_k)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                'node_id': result['id'],
                'score': result['relevance_score'],
                'search_type': 'graph',
                'node_info': result
            })
        
        return formatted_results
    
    def _structure_search(self, query: str, top_k: int) -> List[Dict]:
        """Structure-based search focusing on code organization."""
        # Parse query for structural hints
        query_lower = query.lower()
        results = []
        
        # Look for file-related queries
        if any(word in query_lower for word in ['file', 'module', 'script']):
            file_nodes = self.graph_searcher.search_by_type(NodeType.FILE)
            for node_id in file_nodes[:top_k]:
                node_info = self.graph_searcher.get_node_info(node_id)
                if node_info and query_lower in node_info['attributes'].get('name', '').lower():
                    results.append({
                        'node_id': node_id,
                        'score': 1.0,
                        'search_type': 'structure',
                        'node_info': node_info
                    })
        
        # Look for class-related queries
        if any(word in query_lower for word in ['class', 'object', 'type']):
            class_nodes = self.graph_searcher.search_by_type(NodeType.CLASS)
            for node_id in class_nodes[:top_k]:
                node_info = self.graph_searcher.get_node_info(node_id)
                if node_info and query_lower in node_info['attributes'].get('name', '').lower():
                    results.append({
                        'node_id': node_id,
                        'score': 1.0,
                        'search_type': 'structure',
                        'node_info': node_info
                    })
        
        # Look for function-related queries
        if any(word in query_lower for word in ['function', 'method', 'def']):
            func_nodes = self.graph_searcher.search_by_type(NodeType.FUNCTION)
            for node_id in func_nodes[:top_k]:
                node_info = self.graph_searcher.get_node_info(node_id)
                if node_info and query_lower in node_info['attributes'].get('name', '').lower():
                    results.append({
                        'node_id': node_id,
                        'score': 1.0,
                        'search_type': 'structure',
                        'node_info': node_info
                    })
        
        return results[:top_k]
    
    def _hybrid_search(self, query: str, top_k: int) -> List[Dict]:
        """Hybrid search combining text and graph approaches."""
        # Get results from both approaches
        text_results = self._text_search(query, top_k * 2)
        graph_results = self._graph_search(query, top_k * 2)
        
        # Combine and re-rank results
        combined_results = {}
        
        # Add text results with weight
        for result in text_results:
            node_id = result['node_id']
            combined_results[node_id] = {
                **result,
                'combined_score': result['score'] * 0.6,  # Text weight
                'text_score': result['score'],
                'graph_score': 0.0
            }
        
        # Add graph results with weight
        for result in graph_results:
            node_id = result['node_id']
            if node_id in combined_results:
                # Boost score for nodes found by both methods
                combined_results[node_id]['combined_score'] += result['score'] * 0.4 + 0.2
                combined_results[node_id]['graph_score'] = result['score']
                combined_results[node_id]['search_type'] = 'hybrid'
            else:
                combined_results[node_id] = {
                    **result,
                    'combined_score': result['score'] * 0.4,  # Graph weight
                    'text_score': 0.0,
                    'graph_score': result['score'],
                    'search_type': 'graph'
                }
        
        # Sort by combined score and return top-k
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    def search_by_entity_type(self, entity_type: str, query: str = "", 
                             top_k: Optional[int] = None) -> List[Dict]:
        """Search for specific entity types."""
        if top_k is None:
            top_k = self.config.top_k
        
        # Map entity type string to NodeType
        type_mapping = {
            'file': NodeType.FILE,
            'class': NodeType.CLASS,
            'function': NodeType.FUNCTION,
            'directory': NodeType.DIRECTORY
        }
        
        node_type = type_mapping.get(entity_type.lower())
        if not node_type:
            return []
        
        # Get all nodes of the specified type
        node_ids = self.graph_searcher.search_by_type(node_type)
        
        # If query is provided, filter by relevance
        if query:
            scored_results = []
            query_terms = query.lower().split()
            
            for node_id in node_ids:
                node_info = self.graph_searcher.get_node_info(node_id)
                if not node_info:
                    continue
                
                # Simple relevance scoring based on name matching
                name = node_info['attributes'].get('name', '').lower()
                score = 0.0
                
                for term in query_terms:
                    if term in name:
                        score += 1.0
                    elif any(term in word for word in name.split('_')):
                        score += 0.5
                
                if score > 0 or not query_terms:
                    scored_results.append((node_id, score, node_info))
            
            # Sort by score
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            results = []
            for node_id, score, node_info in scored_results[:top_k]:
                results.append({
                    'node_id': node_id,
                    'score': score,
                    'search_type': 'entity_type',
                    'node_info': node_info
                })
            
            return results
        else:
            # Return all nodes of the type
            results = []
            for node_id in node_ids[:top_k]:
                node_info = self.graph_searcher.get_node_info(node_id)
                if node_info:
                    results.append({
                        'node_id': node_id,
                        'score': 1.0,
                        'search_type': 'entity_type',
                        'node_info': node_info
                    })
            
            return results
    
    def find_related_entities(self, node_id: str, relation_type: str = "all",
                             max_depth: int = 2) -> List[Dict]:
        """Find entities related to a given node."""
        if not self.graph_searcher:
            return []
        
        related_nodes = set()
        
        if relation_type in ["all", "dependencies"]:
            deps = self.graph_searcher.get_dependencies(node_id)
            for dep_list in deps.values():
                related_nodes.update(dep_list)
        
        if relation_type in ["all", "dependents"]:
            dependents = self.graph_searcher.get_dependents(node_id)
            for dep_list in dependents.values():
                related_nodes.update(dep_list)
        
        if relation_type in ["all", "contained"]:
            contained = self.graph_searcher.get_contained_entities(node_id)
            related_nodes.update(contained)
        
        if relation_type in ["all", "container"]:
            container = self.graph_searcher.get_container(node_id)
            if container:
                related_nodes.add(container)
        
        # Convert to result format
        results = []
        for related_id in related_nodes:
            node_info = self.graph_searcher.get_node_info(related_id)
            if node_info:
                results.append({
                    'node_id': related_id,
                    'score': 1.0,
                    'search_type': 'related',
                    'node_info': node_info
                })
        
        return results
    
    def save_index(self, path: Path) -> None:
        """Save the hybrid index to disk."""
        self.bm25_retriever.save_index(path / "bm25_index.pkl")
        
        # Save graph separately if needed
        import pickle
        with open(path / "graph.pkl", 'wb') as f:
            pickle.dump(self.graph, f)
        
        logger.info(f"Hybrid index saved to {path}")
    
    def load_index(self, path: Path, graph: Optional[nx.MultiDiGraph] = None) -> None:
        """Load a pre-built hybrid index from disk."""
        self.bm25_retriever.load_index(path / "bm25_index.pkl")
        
        if graph is not None:
            self.graph = graph
        else:
            # Load graph from disk
            import pickle
            with open(path / "graph.pkl", 'rb') as f:
                self.graph = pickle.load(f)
        
        self.graph_searcher = GraphSearcher(self.graph, self.config)
        
        logger.info(f"Hybrid index loaded from {path}")