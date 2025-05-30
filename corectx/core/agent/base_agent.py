"""Base agent class for LLM interactions."""

import json
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
import logging

from ...config import AgentConfig

logger = logging.getLogger(__name__)


class Message:
    """Represents a message in the conversation."""
    
    def __init__(self, role: str, content: str, tool_calls: Optional[List[Dict]] = None,
                 tool_call_id: Optional[str] = None, name: Optional[str] = None):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id
        self.name = name
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        msg_dict = {
            'role': self.role,
            'content': self.content
        }
        
        if self.tool_calls:
            msg_dict['tool_calls'] = self.tool_calls
        
        if self.tool_call_id:
            msg_dict['tool_call_id'] = self.tool_call_id
        
        if self.name:
            msg_dict['name'] = self.name
        
        return msg_dict


class BaseAgent(ABC):
    """Base class for LLM agents."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.messages: List[Message] = []
        self.tools: Dict[str, Callable] = {}
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def add_tool(self, name: str, func: Callable, description: str = "") -> None:
        """Add a tool function that the agent can call."""
        self.tools[name] = func
        
        # Store tool metadata
        if not hasattr(func, '_tool_metadata'):
            func._tool_metadata = {
                'name': name,
                'description': description
            }
    
    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to the conversation."""
        message = Message(role, content, **kwargs)
        self.messages.append(message)
    
    def clear_messages(self) -> None:
        """Clear conversation history."""
        self.messages.clear()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as list of dictionaries."""
        return [msg.to_dict() for msg in self.messages]
    
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None,
                         use_tools: bool = True) -> Dict[str, Any]:
        """Generate a response from the LLM."""
        pass
    
    def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool function call."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**arguments)
            logger.debug(f"Tool '{tool_name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return f"Error: {str(e)}"
    
    def process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple tool calls and return results."""
        results = []
        
        for tool_call in tool_calls:
            tool_id = tool_call.get('id', '')
            function_info = tool_call.get('function', {})
            tool_name = function_info.get('name', '')
            
            try:
                # Parse arguments
                arguments_str = function_info.get('arguments', '{}')
                arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                
                # Execute tool
                result = self.execute_tool_call(tool_name, arguments)
                
                # Format result
                results.append({
                    'tool_call_id': tool_id,
                    'role': 'tool',
                    'name': tool_name,
                    'content': json.dumps(result) if not isinstance(result, str) else result
                })
                
            except Exception as e:
                logger.error(f"Error processing tool call {tool_id}: {e}")
                results.append({
                    'tool_call_id': tool_id,
                    'role': 'tool',
                    'name': tool_name,
                    'content': f"Error: {str(e)}"
                })
        
        return results
    
    def run_conversation(self, initial_prompt: str, system_prompt: Optional[str] = None,
                        max_iterations: Optional[int] = None) -> Dict[str, Any]:
        """Run a complete conversation with tool usage."""
        if max_iterations is None:
            max_iterations = self.config.max_iterations
        
        # Add initial prompt
        self.add_message('user', initial_prompt)
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # Generate response
            response = self.generate_response(
                prompt=initial_prompt if iteration == 1 else "",
                system_prompt=system_prompt,
                use_tools=True
            )
            
            # Add assistant message
            assistant_message = response.get('message', {})
            self.add_message(
                role='assistant',
                content=assistant_message.get('content', ''),
                tool_calls=assistant_message.get('tool_calls', [])
            )
            
            # Check if there are tool calls to process
            tool_calls = assistant_message.get('tool_calls', [])
            if not tool_calls:
                # No more tool calls, conversation is complete
                break
            
            # Process tool calls
            tool_results = self.process_tool_calls(tool_calls)
            
            # Add tool results to conversation
            for result in tool_results:
                self.add_message(**result)
        
        return {
            'conversation': self.get_conversation_history(),
            'iterations': iteration,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost
        }
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible tool schemas for function calling."""
        schemas = []
        
        for tool_name, tool_func in self.tools.items():
            # Get function signature and docstring
            import inspect
            sig = inspect.signature(tool_func)
            doc = inspect.getdoc(tool_func) or ""
            
            # Build parameter schema
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for param_name, param in sig.parameters.items():
                param_type = "string"  # Default type
                param_desc = f"Parameter {param_name}"
                
                # Try to infer type from annotation
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"
                    elif param.annotation == list:
                        param_type = "array"
                    elif param.annotation == dict:
                        param_type = "object"
                
                parameters["properties"][param_name] = {
                    "type": param_type,
                    "description": param_desc
                }
                
                # Add to required if no default value
                if param.default == inspect.Parameter.empty:
                    parameters["required"].append(param_name)
            
            schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": doc,
                    "parameters": parameters
                }
            }
            
            schemas.append(schema)
        
        return schemas