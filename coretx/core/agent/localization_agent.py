"""Specialized agent for code localization tasks."""

import json
import time
from typing import Dict, Any, Optional, List
import logging

from .base_agent import BaseAgent
from ...config import AgentConfig

logger = logging.getLogger(__name__)


class LocalizationAgent(BaseAgent):
    """Agent specialized for code localization using LLM with function calling."""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.client = None
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Setup the LLM client based on configuration."""
        try:
            if self.config.model_name.startswith('gpt-'):
                # OpenAI client
                import openai
                self.client = openai.OpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.api_base
                )
                self.client_type = 'openai'
            
            elif self.config.model_name.startswith('claude-'):
                # Anthropic client
                import anthropic
                self.client = anthropic.Anthropic(
                    api_key=self.config.api_key
                )
                self.client_type = 'anthropic'
            
            else:
                # Use litellm for other models
                import litellm
                self.client = litellm
                self.client_type = 'litellm'
                
                # Set API key if provided
                if self.config.api_key:
                    import os
                    os.environ['OPENAI_API_KEY'] = self.config.api_key
            
        except ImportError as e:
            logger.error(f"Required client library not installed: {e}")
            raise
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None,
                         use_tools: bool = True) -> Dict[str, Any]:
        """Generate response using the configured LLM."""
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Add conversation history
        messages.extend(self.get_conversation_history())
        
        # Add current prompt if not empty
        if prompt:
            messages.append({
                'role': 'user',
                'content': prompt
            })
        
        # Prepare tool schemas if using tools
        tools = None
        if use_tools and self.tools:
            tools = self.get_tool_schemas()
        
        # Generate response based on client type
        try:
            if self.client_type == 'openai':
                return self._generate_openai_response(messages, tools)
            elif self.client_type == 'anthropic':
                return self._generate_anthropic_response(messages, tools)
            else:  # litellm
                return self._generate_litellm_response(messages, tools)
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'message': {
                    'role': 'assistant',
                    'content': f"Error: {str(e)}"
                },
                'usage': {'total_tokens': 0}
            }
    
    def _generate_openai_response(self, messages: List[Dict], tools: Optional[List[Dict]]) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        kwargs = {
            'model': self.config.model_name,
            'messages': messages,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens
        }
        
        if tools:
            kwargs['tools'] = tools
            kwargs['tool_choice'] = 'auto'
        
        response = self.client.chat.completions.create(**kwargs)
        
        # Update token usage
        if response.usage:
            self.total_tokens += response.usage.total_tokens
        
        return {
            'message': response.choices[0].message.model_dump(),
            'usage': response.usage.model_dump() if response.usage else {}
        }
    
    def _generate_anthropic_response(self, messages: List[Dict], tools: Optional[List[Dict]]) -> Dict[str, Any]:
        """Generate response using Anthropic API."""
        # Convert messages format for Anthropic
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                user_messages.append(msg)
        
        kwargs = {
            'model': self.config.model_name,
            'messages': user_messages,
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature
        }
        
        if system_message:
            kwargs['system'] = system_message
        
        if tools:
            # Convert OpenAI tool format to Anthropic format
            anthropic_tools = []
            for tool in tools:
                func_info = tool['function']
                anthropic_tools.append({
                    'name': func_info['name'],
                    'description': func_info['description'],
                    'input_schema': func_info['parameters']
                })
            kwargs['tools'] = anthropic_tools
        
        response = self.client.messages.create(**kwargs)
        
        # Convert response format
        message_content = ""
        tool_calls = []
        
        for content_block in response.content:
            if content_block.type == 'text':
                message_content += content_block.text
            elif content_block.type == 'tool_use':
                tool_calls.append({
                    'id': content_block.id,
                    'type': 'function',
                    'function': {
                        'name': content_block.name,
                        'arguments': json.dumps(content_block.input)
                    }
                })
        
        result_message = {
            'role': 'assistant',
            'content': message_content
        }
        
        if tool_calls:
            result_message['tool_calls'] = tool_calls
        
        return {
            'message': result_message,
            'usage': {
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
        }
    
    def _generate_litellm_response(self, messages: List[Dict], tools: Optional[List[Dict]]) -> Dict[str, Any]:
        """Generate response using LiteLLM."""
        import litellm
        
        kwargs = {
            'model': self.config.model_name,
            'messages': messages,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens
        }
        
        if tools:
            kwargs['tools'] = tools
            kwargs['tool_choice'] = 'auto'
        
        response = litellm.completion(**kwargs)
        
        # Update token usage
        if response.usage:
            self.total_tokens += response.usage.total_tokens
        
        return {
            'message': response.choices[0].message.model_dump(),
            'usage': response.usage.model_dump() if response.usage else {}
        }
    
    def localize_code(self, problem_description: str, repository_context: str = "") -> Dict[str, Any]:
        """
        Perform code localization for a given problem description.
        
        Args:
            problem_description: Description of the issue/bug to locate
            repository_context: Additional context about the repository
            
        Returns:
            Dictionary containing localization results
        """
        system_prompt = self._get_localization_system_prompt()
        
        # Construct the localization prompt
        prompt = self._construct_localization_prompt(problem_description, repository_context)
        
        # Run conversation with tools
        result = self.run_conversation(prompt, system_prompt)
        
        # Extract localization results from conversation
        localization_results = self._extract_localization_results(result['conversation'])
        
        return {
            'localization_results': localization_results,
            'conversation': result['conversation'],
            'iterations': result['iterations'],
            'total_tokens': result['total_tokens']
        }
    
    def _get_localization_system_prompt(self) -> str:
        """Get the system prompt for code localization."""
        return """You are a code localization expert. Your task is to help locate relevant code entities (files, classes, functions) that are related to a given problem description.

You have access to various tools to search and explore the codebase:
- Search for code entities by name or content
- Explore file contents and structure
- Analyze dependencies and relationships
- Navigate the code graph

Your goal is to:
1. Understand the problem description
2. Use available tools to search and explore the codebase
3. Identify relevant files, classes, and functions
4. Provide a comprehensive list of located entities with explanations

Be systematic in your approach:
- Start with broad searches based on keywords from the problem
- Narrow down to specific entities
- Explore relationships and dependencies
- Verify your findings by examining code content

Always explain your reasoning and provide confidence scores for your findings."""
    
    def _construct_localization_prompt(self, problem_description: str, repository_context: str) -> str:
        """Construct the initial prompt for localization."""
        prompt_parts = [
            "Please help me locate code entities related to the following problem:",
            "",
            "**Problem Description:**",
            problem_description,
        ]
        
        if repository_context:
            prompt_parts.extend([
                "",
                "**Repository Context:**",
                repository_context
            ])
        
        prompt_parts.extend([
            "",
            "Please use the available tools to search and explore the codebase systematically.",
            "Identify relevant files, classes, and functions that might be related to this problem.",
            "Provide explanations for why each entity is relevant."
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_localization_results(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Extract localization results from the conversation."""
        results = {
            'files': [],
            'classes': [],
            'functions': [],
            'explanations': [],
            'confidence_scores': {}
        }
        
        # Parse assistant messages for localization results
        for message in conversation:
            if message['role'] == 'assistant':
                content = message['content']
                
                # Look for structured results in the content
                # This is a simplified extraction - could be enhanced with better parsing
                if 'LOCALIZATION RESULTS' in content.upper():
                    # Extract structured results
                    lines = content.split('\n')
                    current_section = None
                    
                    for line in lines:
                        line = line.strip()
                        if line.upper().startswith('FILES:'):
                            current_section = 'files'
                        elif line.upper().startswith('CLASSES:'):
                            current_section = 'classes'
                        elif line.upper().startswith('FUNCTIONS:'):
                            current_section = 'functions'
                        elif line.startswith('- ') and current_section:
                            entity = line[2:].strip()
                            if current_section in results:
                                results[current_section].append(entity)
        
        return results