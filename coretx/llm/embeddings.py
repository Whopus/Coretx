"""
Embedding engine for semantic search and similarity.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from pathlib import Path

from .client import LLMClient
from ..models import CodeEntity, Relationship, AnalysisError


class EmbeddingEngine:
    """Engine for generating and managing code embeddings."""
    
    def __init__(self, llm_client: LLMClient, cache_dir: Optional[str] = None):
        self.llm_client = llm_client
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._load_cache()
    
    def generate_entity_embedding(self, entity: CodeEntity) -> np.ndarray:
        """Generate embedding for a code entity."""
        # Create text representation for embedding
        text = self._entity_to_text(entity)
        
        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        # Generate embedding
        try:
            embeddings = self.llm_client.generate_embeddings([text])
            embedding = np.array(embeddings[0])
            
            # Cache the result
            self._embedding_cache[cache_key] = embedding
            self._save_cache()
            
            return embedding
            
        except Exception as e:
            raise AnalysisError(f"Failed to generate embedding for entity {entity.name}: {e}")
    
    def generate_relationship_embedding(self, relationship: Relationship, 
                                      source_entity: CodeEntity, 
                                      target_entity: CodeEntity) -> np.ndarray:
        """Generate embedding for a relationship."""
        # Create text representation
        text = self._relationship_to_text(relationship, source_entity, target_entity)
        
        # Check cache
        cache_key = self._get_cache_key(text)
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        # Generate embedding
        try:
            embeddings = self.llm_client.generate_embeddings([text])
            embedding = np.array(embeddings[0])
            
            # Cache the result
            self._embedding_cache[cache_key] = embedding
            self._save_cache()
            
            return embedding
            
        except Exception as e:
            raise AnalysisError(f"Failed to generate embedding for relationship {relationship.id}: {e}")
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for a search query."""
        try:
            embeddings = self.llm_client.generate_embeddings([query])
            return np.array(embeddings[0])
        except Exception as e:
            raise AnalysisError(f"Failed to generate query embedding: {e}")
    
    def find_similar_entities(self, 
                            query_embedding: np.ndarray, 
                            entities: List[CodeEntity], 
                            top_k: int = 10,
                            threshold: float = 0.5) -> List[Tuple[CodeEntity, float]]:
        """Find entities most similar to a query embedding."""
        if not entities:
            return []
        
        # Get embeddings for all entities
        entity_embeddings = []
        valid_entities = []
        
        for entity in entities:
            if entity.embedding is not None:
                entity_embeddings.append(entity.embedding)
                valid_entities.append(entity)
            else:
                # Generate embedding if not available
                try:
                    embedding = self.generate_entity_embedding(entity)
                    entity.embedding = embedding
                    entity_embeddings.append(embedding)
                    valid_entities.append(entity)
                except Exception:
                    continue
        
        if not entity_embeddings:
            return []
        
        # Calculate similarities
        entity_matrix = np.vstack(entity_embeddings)
        query_matrix = query_embedding.reshape(1, -1)
        
        similarities = cosine_similarity(query_matrix, entity_matrix)[0]
        
        # Filter by threshold and get top-k
        results = []
        for i, similarity in enumerate(similarities):
            if similarity >= threshold:
                results.append((valid_entities[i], float(similarity)))
        
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def find_similar_relationships(self, 
                                 query_embedding: np.ndarray, 
                                 relationships: List[Relationship], 
                                 entities_map: Dict[str, CodeEntity],
                                 top_k: int = 10,
                                 threshold: float = 0.5) -> List[Tuple[Relationship, float]]:
        """Find relationships most similar to a query embedding."""
        if not relationships:
            return []
        
        # Get embeddings for all relationships
        rel_embeddings = []
        valid_relationships = []
        
        for relationship in relationships:
            if relationship.embedding is not None:
                rel_embeddings.append(relationship.embedding)
                valid_relationships.append(relationship)
            else:
                # Generate embedding if not available
                try:
                    source_entity = entities_map.get(relationship.source_id)
                    target_entity = entities_map.get(relationship.target_id)
                    
                    if source_entity and target_entity:
                        embedding = self.generate_relationship_embedding(
                            relationship, source_entity, target_entity
                        )
                        relationship.embedding = embedding
                        rel_embeddings.append(embedding)
                        valid_relationships.append(relationship)
                except Exception:
                    continue
        
        if not rel_embeddings:
            return []
        
        # Calculate similarities
        rel_matrix = np.vstack(rel_embeddings)
        query_matrix = query_embedding.reshape(1, -1)
        
        similarities = cosine_similarity(query_matrix, rel_matrix)[0]
        
        # Filter by threshold and get top-k
        results = []
        for i, similarity in enumerate(similarities):
            if similarity >= threshold:
                results.append((valid_relationships[i], float(similarity)))
        
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def cluster_entities(self, entities: List[CodeEntity], n_clusters: int = 5) -> Dict[int, List[CodeEntity]]:
        """Cluster entities based on their embeddings."""
        if len(entities) < n_clusters:
            # Return each entity in its own cluster
            return {i: [entity] for i, entity in enumerate(entities)}
        
        # Ensure all entities have embeddings
        embeddings = []
        valid_entities = []
        
        for entity in entities:
            if entity.embedding is not None:
                embeddings.append(entity.embedding)
                valid_entities.append(entity)
            else:
                try:
                    embedding = self.generate_entity_embedding(entity)
                    entity.embedding = embedding
                    embeddings.append(embedding)
                    valid_entities.append(entity)
                except Exception:
                    continue
        
        if len(embeddings) < n_clusters:
            return {i: [entity] for i, entity in enumerate(valid_entities)}
        
        # Perform clustering
        try:
            from sklearn.cluster import KMeans
            
            embedding_matrix = np.vstack(embeddings)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embedding_matrix)
            
            # Group entities by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(valid_entities[i])
            
            return clusters
            
        except ImportError:
            # Fallback: simple distance-based clustering
            return self._simple_clustering(valid_entities, n_clusters)
    
    def _entity_to_text(self, entity: CodeEntity) -> str:
        """Convert entity to text representation for embedding."""
        parts = [
            f"Type: {entity.type.value}",
            f"Name: {entity.name}",
            f"Language: {entity.language}",
        ]
        
        if entity.description:
            parts.append(f"Description: {entity.description}")
        
        # Add code content (truncated)
        if entity.content:
            content = entity.content[:500]  # Limit content length
            parts.append(f"Code: {content}")
        
        # Add metadata
        if entity.metadata:
            metadata_str = " ".join(f"{k}:{v}" for k, v in entity.metadata.items() 
                                   if isinstance(v, (str, int, float, bool)))
            if metadata_str:
                parts.append(f"Metadata: {metadata_str}")
        
        return " | ".join(parts)
    
    def _relationship_to_text(self, relationship: Relationship, 
                            source_entity: CodeEntity, 
                            target_entity: CodeEntity) -> str:
        """Convert relationship to text representation for embedding."""
        parts = [
            f"Relationship: {relationship.type.value}",
            f"From: {source_entity.type.value} {source_entity.name}",
            f"To: {target_entity.type.value} {target_entity.name}",
        ]
        
        if relationship.description:
            parts.append(f"Description: {relationship.description}")
        
        return " | ".join(parts)
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()
    
    def _load_cache(self) -> None:
        """Load embedding cache from disk."""
        if not self.cache_dir:
            return
        
        cache_file = self.cache_dir / "embeddings.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self._embedding_cache = pickle.load(f)
            except Exception:
                self._embedding_cache = {}
    
    def _save_cache(self) -> None:
        """Save embedding cache to disk."""
        if not self.cache_dir:
            return
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / "embeddings.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self._embedding_cache, f)
        except Exception:
            pass
    
    def _simple_clustering(self, entities: List[CodeEntity], n_clusters: int) -> Dict[int, List[CodeEntity]]:
        """Simple clustering fallback when sklearn is not available."""
        # Group by entity type as a simple clustering approach
        type_groups = {}
        for entity in entities:
            entity_type = entity.type
            if entity_type not in type_groups:
                type_groups[entity_type] = []
            type_groups[entity_type].append(entity)
        
        # Convert to numbered clusters
        clusters = {}
        cluster_id = 0
        for entities_list in type_groups.values():
            clusters[cluster_id] = entities_list
            cluster_id += 1
            if cluster_id >= n_clusters:
                break
        
        return clusters