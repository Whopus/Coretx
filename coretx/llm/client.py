"""
LLM client for interacting with various language models.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
import openai
from openai import OpenAI, AsyncOpenAI

from ..models import LLMConfig, AnalysisError


class LLMClient:
    """Client for interacting with language models."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        self._async_client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the LLM client based on configuration."""
        if self.config.provider == "openai":
            client_kwargs = {}
            
            if self.config.api_key:
                client_kwargs["api_key"] = self.config.api_key
            if self.config.api_base:
                client_kwargs["base_url"] = self.config.api_base
            
            self._client = OpenAI(**client_kwargs)
            self._async_client = AsyncOpenAI(**client_kwargs)
        else:
            raise AnalysisError(f"Unsupported LLM provider: {self.config.provider}")
    
    def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a completion from the LLM."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=max_tokens or self.config.max_tokens,
                temperature=temperature or self.config.temperature,
                timeout=self.config.timeout
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise AnalysisError(f"LLM completion failed: {e}")
    
    async def generate_completion_async(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a completion asynchronously."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self._async_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=max_tokens or self.config.max_tokens,
                temperature=temperature or self.config.temperature,
                timeout=self.config.timeout
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise AnalysisError(f"Async LLM completion failed: {e}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            # Handle custom API format if using custom base URL
            if self.config.api_base and "comfly.chat" in self.config.api_base:
                import requests
                import json
                
                embeddings = []
                for text in texts:
                    payload = json.dumps({
                        "model": self.config.embedding_model,
                        "normalized": True,
                        "embedding_type": "float",
                        "input": text
                    })
                    headers = {
                        'Authorization': f'Bearer {self.config.api_key}',
                        'Content-Type': 'application/json'
                    }
                    
                    response = requests.post(
                        f"{self.config.api_base}/embeddings",
                        headers=headers,
                        data=payload
                    )
                    response.raise_for_status()
                    
                    embedding_data = response.json()
                    embeddings.append(embedding_data["data"][0]["embedding"])
                
                return embeddings
            else:
                # Standard OpenAI API
                response = self._client.embeddings.create(
                    model=self.config.embedding_model,
                    input=texts
                )
                
                return [embedding.embedding for embedding in response.data]
            
        except Exception as e:
            raise AnalysisError(f"Embedding generation failed: {e}")
    
    async def generate_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings asynchronously."""
        try:
            response = await self._async_client.embeddings.create(
                model=self.config.embedding_model,
                input=texts
            )
            
            return [embedding.embedding for embedding in response.data]
            
        except Exception as e:
            raise AnalysisError(f"Async embedding generation failed: {e}")
    
    def analyze_code_semantics(self, code: str, language: str, context: str = "") -> Dict[str, Any]:
        """Analyze the semantic meaning of code."""
        system_prompt = """You are a code analysis expert. Analyze the provided code and extract semantic information.

Return your analysis in the following JSON format:
{
    "purpose": "Brief description of what this code does",
    "complexity": "low|medium|high",
    "key_concepts": ["concept1", "concept2"],
    "dependencies": ["dependency1", "dependency2"],
    "side_effects": ["effect1", "effect2"],
    "patterns": ["pattern1", "pattern2"],
    "quality_issues": ["issue1", "issue2"]
}"""
        
        prompt = f"""Language: {language}
Context: {context}

Code:
```{language}
{code}
```

Analyze this code and provide semantic information."""
        
        try:
            response = self.generate_completion(prompt, system_prompt)
            # Parse JSON response
            import json
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            # Fallback to basic analysis
            return {
                "purpose": f"Code in {language}",
                "complexity": "medium",
                "key_concepts": [],
                "dependencies": [],
                "side_effects": [],
                "patterns": [],
                "quality_issues": []
            }
    
    def generate_description(self, entity_name: str, entity_type: str, code: str, language: str) -> str:
        """Generate a natural language description for a code entity."""
        prompt = f"""Generate a concise, clear description for this {entity_type} in {language}:

Name: {entity_name}
Code:
```{language}
{code[:500]}...
```

Provide a 1-2 sentence description of what this {entity_type} does."""
        
        try:
            return self.generate_completion(prompt, max_tokens=100)
        except Exception:
            return f"{language} {entity_type}: {entity_name}"
    
    def extract_relationships(self, code: str, language: str, entities: List[str]) -> List[Dict[str, Any]]:
        """Extract relationships between code entities."""
        system_prompt = """You are a code analysis expert. Identify relationships between code entities.

Return relationships in JSON format:
[
    {
        "source": "entity_name",
        "target": "entity_name", 
        "type": "calls|uses|inherits|implements|imports",
        "description": "Brief description"
    }
]"""
        
        entities_str = ", ".join(entities)
        prompt = f"""Language: {language}
Known entities: {entities_str}

Code:
```{language}
{code}
```

Identify relationships between these entities in the code."""
        
        try:
            response = self.generate_completion(prompt, system_prompt, max_tokens=500)
            import json
            return json.loads(response)
        except Exception:
            return []
    
    def answer_query(self, query: str, context: str, entities: List[str]) -> Dict[str, Any]:
        """Answer a natural language query about code."""
        system_prompt = """You are a code analysis assistant. Answer questions about code based on the provided context.

Return your response in JSON format:
{
    "answer": "Direct answer to the question",
    "relevant_entities": ["entity1", "entity2"],
    "confidence": 0.8,
    "suggestions": ["follow-up question 1", "follow-up question 2"]
}"""
        
        entities_str = ", ".join(entities[:20])  # Limit to avoid token overflow
        prompt = f"""Question: {query}

Available entities: {entities_str}

Context:
{context[:2000]}...

Answer the question based on the provided code context."""
        
        try:
            response = self.generate_completion(prompt, system_prompt)
            import json
            return json.loads(response)
        except Exception as e:
            return {
                "answer": f"I couldn't analyze the code to answer your question. Error: {str(e)}",
                "relevant_entities": [],
                "confidence": 0.0,
                "suggestions": []
            }