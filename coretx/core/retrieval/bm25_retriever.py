"""BM25-based text retrieval for code search."""

import pickle
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import networkx as nx
from collections import defaultdict
import logging

from ...config import RetrievalConfig

logger = logging.getLogger(__name__)


class BM25Retriever:
    """BM25-based retriever for code entities."""
    
    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.documents: Dict[str, str] = {}
        self.doc_frequencies: Dict[str, int] = {}
        self.idf_cache: Dict[str, float] = {}
        self.avg_doc_length = 0.0
        self.doc_lengths: Dict[str, int] = {}
        self.is_built = False
    
    def build_index(self, graph: nx.MultiDiGraph, repo_path: Optional[Path] = None) -> None:
        """Build BM25 index from graph nodes."""
        logger.info("Building BM25 index...")
        
        self.documents.clear()
        self.doc_frequencies.clear()
        self.idf_cache.clear()
        self.doc_lengths.clear()
        
        # Extract documents from graph nodes
        for node_id, attrs in graph.nodes(data=True):
            doc_text = self._extract_document_text(node_id, attrs, repo_path)
            if doc_text:
                self.documents[node_id] = doc_text
        
        # Build term frequencies and document frequencies
        self._build_term_frequencies()
        self._compute_idf()
        
        self.is_built = True
        logger.info(f"BM25 index built with {len(self.documents)} documents")
    
    def _extract_document_text(self, node_id: str, attrs: Dict[str, Any], 
                              repo_path: Optional[Path]) -> str:
        """Extract searchable text from a node."""
        text_parts = []
        
        # Add node name
        name = attrs.get('name', '')
        if name:
            text_parts.append(name)
        
        # Add docstring if available
        docstring = attrs.get('docstring', '')
        if docstring:
            text_parts.append(docstring)
        
        # For file nodes, add file content (first few lines)
        if attrs.get('type') == 'file' and repo_path:
            file_path = attrs.get('path')
            if file_path:
                try:
                    full_path = repo_path / file_path if not Path(file_path).is_absolute() else Path(file_path)
                    if full_path.exists() and full_path.suffix == '.py':
                        with open(full_path, 'r', encoding='utf-8') as f:
                            # Read first 50 lines for indexing
                            lines = [f.readline().strip() for _ in range(50)]
                            content = ' '.join(line for line in lines if line and not line.startswith('#'))
                            if content:
                                text_parts.append(content)
                except Exception as e:
                    logger.debug(f"Could not read file {file_path}: {e}")
        
        # Add metadata
        for key, value in attrs.items():
            if key in ['args', 'returns'] and isinstance(value, (list, str)):
                text_parts.append(str(value))
        
        return ' '.join(text_parts)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Simple tokenization - split on non-alphanumeric, convert to lowercase
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [token for token in tokens if len(token) > 1]  # Filter single characters
    
    def _build_term_frequencies(self) -> None:
        """Build term frequencies for all documents."""
        total_length = 0
        
        for doc_id, text in self.documents.items():
            tokens = self._tokenize(text)
            self.doc_lengths[doc_id] = len(tokens)
            total_length += len(tokens)
            
            # Count term frequencies in this document
            term_counts = defaultdict(int)
            for token in tokens:
                term_counts[token] += 1
            
            # Update document frequencies
            for term in term_counts:
                if term not in self.doc_frequencies:
                    self.doc_frequencies[term] = 0
                self.doc_frequencies[term] += 1
        
        self.avg_doc_length = total_length / len(self.documents) if self.documents else 0
    
    def _compute_idf(self) -> None:
        """Compute IDF values for all terms."""
        import math
        
        num_docs = len(self.documents)
        for term, df in self.doc_frequencies.items():
            self.idf_cache[term] = math.log((num_docs - df + 0.5) / (df + 0.5))
    
    def _compute_bm25_score(self, query_terms: List[str], doc_id: str) -> float:
        """Compute BM25 score for a document given query terms."""
        if doc_id not in self.documents:
            return 0.0
        
        doc_text = self.documents[doc_id]
        doc_tokens = self._tokenize(doc_text)
        doc_length = self.doc_lengths[doc_id]
        
        # Count term frequencies in document
        term_counts = defaultdict(int)
        for token in doc_tokens:
            term_counts[token] += 1
        
        score = 0.0
        for term in query_terms:
            if term in term_counts:
                tf = term_counts[term]
                idf = self.idf_cache.get(term, 0.0)
                
                # BM25 formula
                numerator = tf * (self.config.bm25_k1 + 1)
                denominator = tf + self.config.bm25_k1 * (
                    1 - self.config.bm25_b + 
                    self.config.bm25_b * (doc_length / self.avg_doc_length)
                )
                
                score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Tuple[str, float]]:
        """Search for relevant documents using BM25."""
        if not self.is_built:
            raise ValueError("Index not built. Call build_index() first.")
        
        if top_k is None:
            top_k = self.config.top_k
        
        query_terms = self._tokenize(query)
        if not query_terms:
            return []
        
        # Score all documents
        scores = []
        for doc_id in self.documents:
            score = self._compute_bm25_score(query_terms, doc_id)
            if score > 0:
                scores.append((doc_id, score))
        
        # Sort by score descending and return top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def save_index(self, path: Path) -> None:
        """Save the built index to disk."""
        if not self.is_built:
            raise ValueError("Index not built. Call build_index() first.")
        
        index_data = {
            'documents': self.documents,
            'doc_frequencies': self.doc_frequencies,
            'idf_cache': self.idf_cache,
            'avg_doc_length': self.avg_doc_length,
            'doc_lengths': self.doc_lengths,
            'config': self.config
        }
        
        with open(path, 'wb') as f:
            pickle.dump(index_data, f)
        
        logger.info(f"BM25 index saved to {path}")
    
    def load_index(self, path: Path) -> None:
        """Load a pre-built index from disk."""
        with open(path, 'rb') as f:
            index_data = pickle.load(f)
        
        self.documents = index_data['documents']
        self.doc_frequencies = index_data['doc_frequencies']
        self.idf_cache = index_data['idf_cache']
        self.avg_doc_length = index_data['avg_doc_length']
        self.doc_lengths = index_data['doc_lengths']
        
        self.is_built = True
        logger.info(f"BM25 index loaded from {path}")
    
    def get_document_text(self, doc_id: str) -> Optional[str]:
        """Get the indexed text for a document."""
        return self.documents.get(doc_id)