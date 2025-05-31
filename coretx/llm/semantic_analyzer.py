"""
Semantic analyzer for understanding code meaning and intent.
"""

from typing import Dict, List, Optional, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .client import LLMClient
from .embeddings import EmbeddingEngine
from ..models import CodeEntity, Relationship, AnalysisError
from ..graph import CodeGraph


class SemanticAnalyzer:
    """Analyzes code semantics using LLMs."""
    
    def __init__(self, llm_client: LLMClient, embedding_engine: EmbeddingEngine):
        self.llm_client = llm_client
        self.embedding_engine = embedding_engine
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def analyze_entity(self, entity: CodeEntity, context: Optional[str] = None) -> CodeEntity:
        """Analyze a single code entity for semantic information."""
        try:
            # Generate semantic analysis
            semantic_info = self.llm_client.analyze_code_semantics(
                entity.content, 
                entity.language, 
                context or ""
            )
            
            # Generate description if not present
            if not entity.description:
                entity.description = self.llm_client.generate_description(
                    entity.name, 
                    entity.type.value, 
                    entity.content, 
                    entity.language
                )
            
            # Generate embedding
            if entity.embedding is None:
                entity.embedding = self.embedding_engine.generate_entity_embedding(entity)
            
            # Update metadata with semantic information
            entity.metadata.update({
                "semantic_analysis": semantic_info,
                "analyzed": True
            })
            
            return entity
            
        except Exception as e:
            # Don't fail the entire analysis for one entity
            entity.metadata["analysis_error"] = str(e)
            return entity
    
    def analyze_entities_batch(self, entities: List[CodeEntity], 
                             context: Optional[str] = None,
                             max_workers: int = 4) -> List[CodeEntity]:
        """Analyze multiple entities in parallel."""
        if not entities:
            return []
        
        # Process in batches to avoid overwhelming the LLM
        batch_size = min(10, len(entities))
        analyzed_entities = []
        
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]
            
            # Process batch
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(self.analyze_entity, entity, context)
                    for entity in batch
                ]
                
                for future in futures:
                    try:
                        analyzed_entity = future.result(timeout=30)
                        analyzed_entities.append(analyzed_entity)
                    except Exception as e:
                        # Add the original entity with error info
                        entity = batch[len(analyzed_entities) % len(batch)]
                        entity.metadata["analysis_error"] = str(e)
                        analyzed_entities.append(entity)
        
        return analyzed_entities
    
    def analyze_relationships(self, relationships: List[Relationship], 
                            entities_map: Dict[str, CodeEntity]) -> List[Relationship]:
        """Analyze relationships for semantic information."""
        analyzed_relationships = []
        
        for relationship in relationships:
            try:
                source_entity = entities_map.get(relationship.source_id)
                target_entity = entities_map.get(relationship.target_id)
                
                if not source_entity or not target_entity:
                    analyzed_relationships.append(relationship)
                    continue
                
                # Generate description if not present
                if not relationship.description:
                    relationship.description = self._generate_relationship_description(
                        relationship, source_entity, target_entity
                    )
                
                # Generate embedding
                if relationship.embedding is None:
                    relationship.embedding = self.embedding_engine.generate_relationship_embedding(
                        relationship, source_entity, target_entity
                    )
                
                relationship.metadata["analyzed"] = True
                analyzed_relationships.append(relationship)
                
            except Exception as e:
                relationship.metadata["analysis_error"] = str(e)
                analyzed_relationships.append(relationship)
        
        return analyzed_relationships
    
    def analyze_graph(self, graph: CodeGraph) -> CodeGraph:
        """Perform semantic analysis on an entire graph."""
        # Analyze entities
        entities = list(graph.nodes)
        analyzed_entities = self.analyze_entities_batch(entities)
        
        # Update entities in graph
        for entity in analyzed_entities:
            graph.add_entity(entity)
        
        # Analyze relationships
        relationships = list(graph.edges)
        entities_map = {entity.id: entity for entity in analyzed_entities}
        analyzed_relationships = self.analyze_relationships(relationships, entities_map)
        
        # Update relationships in graph
        for relationship in analyzed_relationships:
            try:
                graph.add_relationship(relationship)
            except Exception:
                pass  # Skip invalid relationships
        
        return graph
    
    def extract_semantic_relationships(self, entity: CodeEntity, 
                                     related_entities: List[CodeEntity]) -> List[Dict[str, Any]]:
        """Extract semantic relationships between entities using LLM."""
        if not related_entities:
            return []
        
        try:
            # Prepare entity names for LLM
            entity_names = [e.name for e in related_entities]
            
            # Use LLM to extract relationships
            relationships = self.llm_client.extract_relationships(
                entity.content, 
                entity.language, 
                entity_names
            )
            
            return relationships
            
        except Exception as e:
            return []
    
    def infer_entity_purpose(self, entity: CodeEntity, graph: CodeGraph) -> str:
        """Infer the purpose of an entity based on its context in the graph."""
        try:
            # Get related entities
            dependencies = graph.get_dependencies(entity)
            dependents = graph.get_dependents(entity)
            
            # Create context
            context_parts = []
            
            if dependencies:
                dep_names = [dep.name for dep in dependencies[:5]]
                context_parts.append(f"Uses: {', '.join(dep_names)}")
            
            if dependents:
                dep_names = [dep.name for dep in dependents[:5]]
                context_parts.append(f"Used by: {', '.join(dep_names)}")
            
            context = " | ".join(context_parts)
            
            # Generate purpose description
            prompt = f"""Based on the code and context, what is the main purpose of this {entity.type.value}?

Name: {entity.name}
Context: {context}

Code:
```{entity.language}
{entity.content[:300]}...
```

Provide a concise 1-sentence description of its purpose."""
            
            return self.llm_client.generate_completion(prompt, max_tokens=50)
            
        except Exception:
            return f"A {entity.type.value} named {entity.name}"
    
    def detect_code_patterns(self, entities: List[CodeEntity]) -> Dict[str, List[CodeEntity]]:
        """Detect common code patterns across entities."""
        patterns = {
            "singletons": [],
            "factories": [],
            "observers": [],
            "decorators": [],
            "adapters": [],
            "controllers": [],
            "services": [],
            "utilities": [],
            "models": [],
            "views": []
        }
        
        for entity in entities:
            entity_name = entity.name.lower()
            entity_content = entity.content.lower()
            
            # Simple pattern detection based on naming and content
            if "singleton" in entity_name or "instance" in entity_content:
                patterns["singletons"].append(entity)
            elif "factory" in entity_name or "create" in entity_name:
                patterns["factories"].append(entity)
            elif "observer" in entity_name or "listener" in entity_name:
                patterns["observers"].append(entity)
            elif "decorator" in entity_name or "@" in entity_content:
                patterns["decorators"].append(entity)
            elif "adapter" in entity_name or "wrapper" in entity_name:
                patterns["adapters"].append(entity)
            elif "controller" in entity_name:
                patterns["controllers"].append(entity)
            elif "service" in entity_name:
                patterns["services"].append(entity)
            elif "util" in entity_name or "helper" in entity_name:
                patterns["utilities"].append(entity)
            elif "model" in entity_name or "entity" in entity_name:
                patterns["models"].append(entity)
            elif "view" in entity_name or "template" in entity_name:
                patterns["views"].append(entity)
        
        # Remove empty patterns
        return {k: v for k, v in patterns.items() if v}
    
    def analyze_code_quality(self, entity: CodeEntity) -> Dict[str, Any]:
        """Analyze code quality metrics for an entity."""
        try:
            prompt = f"""Analyze the code quality of this {entity.type.value}:

```{entity.language}
{entity.content}
```

Rate the following aspects (1-10 scale) and provide brief explanations:
- Readability
- Maintainability  
- Complexity
- Performance
- Security

Return as JSON:
{{
    "readability": {{"score": 8, "notes": "Clear naming"}},
    "maintainability": {{"score": 7, "notes": "Well structured"}},
    "complexity": {{"score": 6, "notes": "Moderate complexity"}},
    "performance": {{"score": 8, "notes": "Efficient implementation"}},
    "security": {{"score": 9, "notes": "No obvious vulnerabilities"}},
    "overall_score": 7.6,
    "suggestions": ["Add more comments", "Consider breaking into smaller functions"]
}}"""
            
            response = self.llm_client.generate_completion(prompt, max_tokens=300)
            
            import json
            return json.loads(response)
            
        except Exception:
            return {
                "readability": {"score": 5, "notes": "Unable to analyze"},
                "maintainability": {"score": 5, "notes": "Unable to analyze"},
                "complexity": {"score": 5, "notes": "Unable to analyze"},
                "performance": {"score": 5, "notes": "Unable to analyze"},
                "security": {"score": 5, "notes": "Unable to analyze"},
                "overall_score": 5.0,
                "suggestions": []
            }
    
    def _generate_relationship_description(self, relationship: Relationship, 
                                         source_entity: CodeEntity, 
                                         target_entity: CodeEntity) -> str:
        """Generate a description for a relationship."""
        rel_type = relationship.type.value
        source_name = source_entity.name
        target_name = target_entity.name
        
        descriptions = {
            "calls": f"{source_name} calls {target_name}",
            "imports": f"{source_name} imports {target_name}",
            "inherits": f"{source_name} inherits from {target_name}",
            "implements": f"{source_name} implements {target_name}",
            "uses": f"{source_name} uses {target_name}",
            "contains": f"{source_name} contains {target_name}",
            "depends_on": f"{source_name} depends on {target_name}",
            "references": f"{source_name} references {target_name}"
        }
        
        return descriptions.get(rel_type, f"{source_name} {rel_type} {target_name}")