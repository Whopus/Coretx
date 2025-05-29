"""Tool registry and management for agents."""

from typing import Dict, Callable, Any, Optional, List
import inspect
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing agent tools."""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: Optional[str] = None, description: str = "", 
                category: str = "general") -> Callable:
        """Decorator to register a function as a tool."""
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            
            # Store the function
            self.tools[tool_name] = func
            
            # Extract metadata
            sig = inspect.signature(func)
            doc = inspect.getdoc(func) or description
            
            self.tool_metadata[tool_name] = {
                'name': tool_name,
                'description': doc,
                'category': category,
                'signature': str(sig),
                'parameters': self._extract_parameters(sig, doc)
            }
            
            # Add metadata to function
            func._tool_metadata = self.tool_metadata[tool_name]
            
            return func
        
        return decorator
    
    def _extract_parameters(self, sig: inspect.Signature, doc: str) -> Dict[str, Any]:
        """Extract parameter information from function signature and docstring."""
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Parse docstring for parameter descriptions
        param_descriptions = self._parse_docstring_params(doc)
        
        for param_name, param in sig.parameters.items():
            param_info = {
                "description": param_descriptions.get(param_name, f"Parameter {param_name}")
            }
            
            # Infer type from annotation
            if param.annotation != inspect.Parameter.empty:
                param_info["type"] = self._python_type_to_json_type(param.annotation)
            else:
                param_info["type"] = "string"  # Default type
            
            parameters["properties"][param_name] = param_info
            
            # Add to required if no default value
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
        
        return parameters
    
    def _parse_docstring_params(self, doc: str) -> Dict[str, str]:
        """Parse parameter descriptions from docstring."""
        param_descriptions = {}
        
        if not doc:
            return param_descriptions
        
        lines = doc.split('\n')
        in_params_section = False
        
        for line in lines:
            line = line.strip()
            
            if line.lower().startswith('args:') or line.lower().startswith('parameters:'):
                in_params_section = True
                continue
            
            if in_params_section:
                if line.startswith('returns:') or line.startswith('yields:'):
                    break
                
                if ':' in line and not line.startswith(' '):
                    # Parameter line: "param_name: description"
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        param_name = parts[0].strip()
                        description = parts[1].strip()
                        param_descriptions[param_name] = description
        
        return param_descriptions
    
    def _python_type_to_json_type(self, python_type) -> str:
        """Convert Python type to JSON schema type."""
        type_mapping = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        
        # Handle typing module types
        if hasattr(python_type, '__origin__'):
            origin = python_type.__origin__
            if origin is list:
                return "array"
            elif origin is dict:
                return "object"
            elif origin is tuple:
                return "array"
        
        return type_mapping.get(python_type, "string")
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_tools(self, category: Optional[str] = None) -> Dict[str, Callable]:
        """Get all tools, optionally filtered by category."""
        if category is None:
            return self.tools.copy()
        
        filtered_tools = {}
        for name, func in self.tools.items():
            if self.tool_metadata[name]['category'] == category:
                filtered_tools[name] = func
        
        return filtered_tools
    
    def get_tool_schemas(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible tool schemas."""
        schemas = []
        tools = self.get_tools(category)
        
        for name, func in tools.items():
            metadata = self.tool_metadata[name]
            
            schema = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": metadata['description'],
                    "parameters": metadata['parameters']
                }
            }
            
            schemas.append(schema)
        
        return schemas
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools with their metadata."""
        return list(self.tool_metadata.values())
    
    def remove_tool(self, name: str) -> bool:
        """Remove a tool from the registry."""
        if name in self.tools:
            del self.tools[name]
            del self.tool_metadata[name]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self.tools.clear()
        self.tool_metadata.clear()


# Global tool registry instance
default_registry = ToolRegistry()

# Convenience functions
def register_tool(name: Optional[str] = None, description: str = "", 
                 category: str = "general") -> Callable:
    """Register a tool using the default registry."""
    return default_registry.register(name, description, category)

def get_tool(name: str) -> Optional[Callable]:
    """Get a tool from the default registry."""
    return default_registry.get_tool(name)

def get_tools(category: Optional[str] = None) -> Dict[str, Callable]:
    """Get tools from the default registry."""
    return default_registry.get_tools(category)

def get_tool_schemas(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get tool schemas from the default registry."""
    return default_registry.get_tool_schemas(category)