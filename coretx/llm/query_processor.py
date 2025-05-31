"""
Query processor for natural language queries over code graphs.
"""

from typing import Dict, List, Optional, Any, Tuple
import re

from .client import LLMClient
from .embeddings import EmbeddingEngine
from ..models import (
    QueryResult, 
    ContextResult, 
    TraceResult,
    CodeEntity, 
    Relationship,
    FileContext,
    EntityType,
    RelationshipType
)
from ..graph import CodeGraph


class QueryProcessor:
    """Processes natural language queries over code graphs."""
    
    def __init__(self, llm_client: LLMClient, embedding_engine: EmbeddingEngine):
        self.llm_client = llm_client
        self.embedding_engine = embedding_engine
    
    def process_query(self, query: str, graph: CodeGraph, 
                     max_results: int = 10) -> QueryResult:
        """Process a natural language query against the code graph."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_engine.generate_query_embedding(query)
            
            # Find relevant entities
            relevant_entities = self.embedding_engine.find_similar_entities(
                query_embedding, graph.nodes, top_k=max_results
            )
            
            # Find relevant relationships
            entities_map = {entity.id: entity for entity in graph.nodes}
            relevant_relationships = self.embedding_engine.find_similar_relationships(
                query_embedding, graph.edges, entities_map, top_k=max_results
            )
            
            # Extract entities and relationships
            entities = [entity for entity, _ in relevant_entities]
            relationships = [rel for rel, _ in relevant_relationships]
            
            # Generate context
            context = self._build_context(entities, relationships, graph)
            
            # Use LLM to answer the query
            entity_names = [entity.name for entity in entities[:10]]
            llm_response = self.llm_client.answer_query(query, context, entity_names)
            
            # Build file contexts
            file_contexts = self._build_file_contexts(entities)
            
            return QueryResult(
                summary=llm_response.get("answer", "No answer available"),
                code_context=context,
                entities=entities,
                relationships=relationships,
                confidence=llm_response.get("confidence", 0.5),
                suggestions=llm_response.get("suggestions", []),
                files=file_contexts,
                metadata={
                    "query": query,
                    "entity_scores": [score for _, score in relevant_entities],
                    "relationship_scores": [score for _, score in relevant_relationships]
                }
            )
            
        except Exception as e:
            return QueryResult(
                summary=f"Error processing query: {str(e)}",
                code_context="",
                entities=[],
                relationships=[],
                confidence=0.0,
                suggestions=[],
                files=[]
            )
    
    def locate_code(self, problem_description: str, graph: CodeGraph) -> ContextResult:
        """Locate relevant code for a specific problem or task."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_engine.generate_query_embedding(problem_description)
            
            # Find relevant entities with higher threshold for precision
            relevant_entities = self.embedding_engine.find_similar_entities(
                query_embedding, graph.nodes, top_k=20, threshold=0.6
            )
            
            entities = [entity for entity, _ in relevant_entities]
            
            # Find entry points (high-level entities)
            entry_points = self._find_entry_points(entities, graph)
            
            # Build minimal closure
            closure_entities = self._build_minimal_closure(entities, graph)
            
            # Generate context
            minimal_closure = self._format_minimal_closure(closure_entities)
            
            # Build file contexts
            file_contexts = self._build_file_contexts(closure_entities)
            
            # Generate flow diagram
            flow_diagram = self._generate_flow_diagram(closure_entities, graph)
            
            # Generate fix suggestions
            fix_suggestions = self._generate_fix_suggestions(problem_description, closure_entities)
            
            # Generate analysis summary
            analysis_summary = self._generate_analysis_summary(problem_description, closure_entities)
            
            return ContextResult(
                minimal_closure=minimal_closure,
                files=file_contexts,
                entry_points=entry_points,
                flow_diagram=flow_diagram,
                fix_suggestions=fix_suggestions,
                analysis_summary=analysis_summary,
                confidence=sum(score for _, score in relevant_entities) / len(relevant_entities) if relevant_entities else 0.0
            )
            
        except Exception as e:
            return ContextResult(
                minimal_closure=f"Error locating code: {str(e)}",
                files=[],
                entry_points=[],
                flow_diagram="",
                fix_suggestions=[],
                analysis_summary="Analysis failed"
            )
    
    def trace_dependencies(self, entity_name: str, graph: CodeGraph, 
                          direction: str = "both", max_depth: int = 3) -> TraceResult:
        """Trace dependencies of a code entity."""
        # Find the entity
        entity = graph.find_entity(entity_name)
        if not entity:
            return TraceResult(
                entity=None,
                dependencies=[],
                dependents=[],
                paths=[],
                depth=0,
                metadata={"error": f"Entity '{entity_name}' not found"}
            )
        
        dependencies = []
        dependents = []
        paths = []
        
        if direction in ["forward", "both"]:
            dependencies = self._trace_forward_dependencies(entity, graph, max_depth)
        
        if direction in ["backward", "both"]:
            dependents = self._trace_backward_dependencies(entity, graph, max_depth)
        
        # Find paths between entity and its dependencies/dependents
        for dep in dependencies[:5]:  # Limit to avoid too many paths
            entity_paths = graph.find_paths(entity, dep, max_depth)
            paths.extend(entity_paths)
        
        for dep in dependents[:5]:
            entity_paths = graph.find_paths(dep, entity, max_depth)
            paths.extend(entity_paths)
        
        return TraceResult(
            entity=entity,
            dependencies=dependencies,
            dependents=dependents,
            paths=paths,
            depth=max_depth,
            metadata={
                "direction": direction,
                "total_dependencies": len(dependencies),
                "total_dependents": len(dependents),
                "total_paths": len(paths)
            }
        )
    
    def _build_context(self, entities: List[CodeEntity], 
                      relationships: List[Relationship], 
                      graph: CodeGraph) -> str:
        """Build context string from entities and relationships."""
        context_parts = []
        
        # Add entity information
        if entities:
            context_parts.append("=== RELEVANT ENTITIES ===")
            for entity in entities[:5]:  # Limit to top 5
                context_parts.append(f"\n{entity.type.value.upper()}: {entity.name}")
                if entity.description:
                    context_parts.append(f"Description: {entity.description}")
                if entity.content:
                    # Add truncated content
                    content = entity.content[:200]
                    context_parts.append(f"Code: {content}...")
                context_parts.append("")
        
        # Add relationship information
        if relationships:
            context_parts.append("=== RELEVANT RELATIONSHIPS ===")
            entities_map = {entity.id: entity for entity in graph.nodes}
            
            for rel in relationships[:5]:  # Limit to top 5
                source = entities_map.get(rel.source_id)
                target = entities_map.get(rel.target_id)
                if source and target:
                    context_parts.append(f"{source.name} {rel.type.value} {target.name}")
                    if rel.description:
                        context_parts.append(f"  {rel.description}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_file_contexts(self, entities: List[CodeEntity]) -> List[FileContext]:
        """Build file contexts from entities."""
        file_map = {}
        
        for entity in entities:
            if entity.path not in file_map:
                file_map[entity.path] = {
                    "entities": [],
                    "content": entity.content if entity.type.value == "module" else ""
                }
            file_map[entity.path]["entities"].append(entity)
        
        file_contexts = []
        for path, data in file_map.items():
            file_contexts.append(FileContext(
                path=path,
                content=data["content"],
                entities=data["entities"],
                relevance_score=1.0
            ))
        
        return file_contexts
    
    def _find_entry_points(self, entities: List[CodeEntity], graph: CodeGraph) -> List[CodeEntity]:
        """Find entry points (high-level entities) in the entity list."""
        entry_points = []
        
        for entity in entities:
            # Consider entities with few dependencies as entry points
            dependencies = graph.get_dependencies(entity)
            dependents = graph.get_dependents(entity)
            
            # Entry points typically have more dependents than dependencies
            if len(dependents) > len(dependencies) or entity.type in [EntityType.MODULE, EntityType.CLASS]:
                entry_points.append(entity)
        
        return entry_points[:3]  # Limit to top 3
    
    def _build_minimal_closure(self, entities: List[CodeEntity], graph: CodeGraph) -> List[CodeEntity]:
        """Build minimal closure of entities needed for understanding."""
        closure = set(entities)
        
        # Add immediate dependencies for context
        for entity in entities[:5]:  # Limit to avoid explosion
            dependencies = graph.get_dependencies(entity)
            for dep in dependencies[:2]:  # Add top 2 dependencies
                closure.add(dep)
        
        return list(closure)
    
    def _format_minimal_closure(self, entities: List[CodeEntity]) -> str:
        """Format entities into a minimal closure string."""
        if not entities:
            return "No relevant code found."
        
        # Group by file
        file_groups = {}
        for entity in entities:
            if entity.path not in file_groups:
                file_groups[entity.path] = []
            file_groups[entity.path].append(entity)
        
        closure_parts = []
        for file_path, file_entities in file_groups.items():
            closure_parts.append(f"=== FILE: {file_path} ===")
            
            for entity in sorted(file_entities, key=lambda e: e.line_start):
                closure_parts.append(f"\n{entity.type.value.upper()}: {entity.name} (lines {entity.line_start}-{entity.line_end})")
                if entity.description:
                    closure_parts.append(f"Description: {entity.description}")
                
                # Add relevant code snippet
                if entity.content and len(entity.content) < 500:
                    closure_parts.append(f"```{entity.language}")
                    closure_parts.append(entity.content)
                    closure_parts.append("```")
                elif entity.content:
                    closure_parts.append(f"```{entity.language}")
                    closure_parts.append(entity.content[:300] + "...")
                    closure_parts.append("```")
                
                closure_parts.append("")
        
        return "\n".join(closure_parts)
    
    def _generate_flow_diagram(self, entities: List[CodeEntity], graph: CodeGraph) -> str:
        """Generate a simple ASCII flow diagram."""
        if not entities:
            return "No entities to diagram."
        
        # Simple text-based flow
        flow_parts = ["=== FLOW DIAGRAM ==="]
        
        # Find relationships between entities
        entity_ids = {entity.id for entity in entities}
        relevant_rels = []
        
        for rel in graph.edges:
            if rel.source_id in entity_ids and rel.target_id in entity_ids:
                relevant_rels.append(rel)
        
        # Build simple flow
        entities_map = {entity.id: entity for entity in graph.nodes}
        
        for rel in relevant_rels[:10]:  # Limit to avoid clutter
            source = entities_map.get(rel.source_id)
            target = entities_map.get(rel.target_id)
            if source and target:
                arrow = "→" if rel.type.value in ["calls", "uses"] else "↔"
                flow_parts.append(f"{source.name} {arrow} {target.name} ({rel.type.value})")
        
        return "\n".join(flow_parts)
    
    def _generate_fix_suggestions(self, problem: str, entities: List[CodeEntity]) -> List[str]:
        """Generate fix suggestions for the problem."""
        if not entities:
            return ["No relevant code found to suggest fixes."]
        
        try:
            entity_info = []
            for entity in entities[:3]:  # Limit to top 3
                entity_info.append(f"{entity.type.value}: {entity.name}")
            
            prompt = f"""Problem: {problem}

Relevant code entities:
{chr(10).join(entity_info)}

Suggest 3-5 specific, actionable steps to address this problem:"""
            
            response = self.llm_client.generate_completion(prompt, max_tokens=200)
            
            # Parse suggestions (simple line-based parsing)
            suggestions = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                    suggestions.append(line.lstrip('-*0123456789. '))
            
            return suggestions[:5] if suggestions else [response]
            
        except Exception:
            return ["Unable to generate fix suggestions."]
    
    def _generate_analysis_summary(self, problem: str, entities: List[CodeEntity]) -> str:
        """Generate analysis summary."""
        if not entities:
            return "No relevant code found for analysis."
        
        try:
            entity_count = len(entities)
            file_count = len(set(entity.path for entity in entities))
            
            summary = f"""Analysis Summary:
- Found {entity_count} relevant code entities across {file_count} files
- Primary entities: {', '.join(entity.name for entity in entities[:3])}
- Problem focus: {problem}"""
            
            return summary
            
        except Exception:
            return "Analysis summary unavailable."
    
    def _trace_forward_dependencies(self, entity: CodeEntity, graph: CodeGraph, max_depth: int) -> List[CodeEntity]:
        """Trace forward dependencies (what this entity depends on)."""
        visited = set()
        dependencies = []
        
        def _trace_recursive(current_entity: CodeEntity, depth: int):
            if depth >= max_depth or current_entity.id in visited:
                return
            
            visited.add(current_entity.id)
            deps = graph.get_dependencies(current_entity)
            
            for dep in deps:
                if dep.id not in visited:
                    dependencies.append(dep)
                    _trace_recursive(dep, depth + 1)
        
        _trace_recursive(entity, 0)
        return dependencies
    
    def _trace_backward_dependencies(self, entity: CodeEntity, graph: CodeGraph, max_depth: int) -> List[CodeEntity]:
        """Trace backward dependencies (what depends on this entity)."""
        visited = set()
        dependents = []
        
        def _trace_recursive(current_entity: CodeEntity, depth: int):
            if depth >= max_depth or current_entity.id in visited:
                return
            
            visited.add(current_entity.id)
            deps = graph.get_dependents(current_entity)
            
            for dep in deps:
                if dep.id not in visited:
                    dependents.append(dep)
                    _trace_recursive(dep, depth + 1)
        
        _trace_recursive(entity, 0)
        return dependents